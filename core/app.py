import decimal
from flask import Flask, jsonify, render_template, send_from_directory, request
from decimal import *
import time
import json
import urllib2
import dbNTSB
from decode import decodeword
from datetime import date, datetime
from flask.ext.cors import CORS
from werkzeug.contrib.cache import SimpleCache
from LSA import LSAinit, LSAevaluate, returnTD
from sklearn.metrics.pairwise import linear_kernel
from random import shuffle
import numpy

cache = SimpleCache()
print "[Init] initializing LSA similarity component..."
dataset = LSAinit()
print "[Init] LSA evaluation starting..."
dtmLSA = LSAevaluate()
print "[Init] Initialization done."
testData = returnTD()


def json_date_handler(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    elif isinstance(obj, date) or isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    else:
        raise TypeError("Type not serializable")

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/api/v2/ntsb/incidents/list/listrange', methods=['GET'])
def getentirelistX():
    print "[LReq] get entire list according to requested day range"
    try:
        startyear = request.args.get('startyear')   # in format: YYYY
        startmonth = request.args.get('startmonth')   # in format: MM
        startday = request.args.get('startday')   # in format: DD
        endyear = request.args.get('endyear')   # in format: YYYY
        endmonth = request.args.get('endmonth')   # in format: MM
        endday = request.args.get('endday')   # in format: DD

        cached_query = cache.get('history%s%s%s%s%s%s' % (
            startyear, startmonth, startday, endyear, endmonth, endday))
        if cached_query is None:
            cnx = dbNTSB.connect()
            if endyear is None and endmonth is None and endday is None:  # to be deprecated
                result = dbNTSB.query(cnx, "select e.lat, e.lon, e.ev_id, e.ev_date, e.approx_loc, if(i.inj_count is null, 0, i.inj_count) as inj_count from events e left outer join injurytotal_view i  on e.ev_id = i.ev_id left outer join aircraft_accident a on e.ev_id = a.ev_id where e.lat and e.lon is not null and a.acft_category = 'AIR' and ev_date = '%s-%s-%s'" % (startyear, startmonth, startday))
            else:
                result = dbNTSB.query(cnx, "select e.lat, e.lon, e.ev_id, e.ev_date, e.approx_loc, if(i.inj_count is null, 0, i.inj_count) as inj_count from events e left outer join injurytotal_view i  on e.ev_id = i.ev_id left outer join aircraft_accident a on e.ev_id = a.ev_id where e.lat and e.lon is not null and a.acft_category = 'AIR' and ev_date BETWEEN '%s-%s-%s' AND '%s-%s-%s'" % (startyear, startmonth, startday, endyear, endmonth, endday))
            for r in result:
                r['lat'] = float(r['lat'].strip())
                r['lon'] = float(r['lon'].strip())
            dbNTSB.close(cnx)
            response = json.dumps(result, sort_keys=True, indent=4, separators=(
                ',', ':'), default=json_date_handler)
            cache.set('history%s%s%s%s%s%s' % (startyear, startmonth, startday,
                                               endyear, endmonth, endday), response, timeout=60 * 60 * 24)
            print "[LReq] cached query for later loading"
        else:
            print "[LReq] using cached query mode"
            response = cached_query
    except:
        response = "[Err] API error"
        print response
    return response


@app.route('/api/v2/ntsb/incidents/incidentdetails', methods=['GET'])
def getincidentDetail():
    print "[IDReq] get incident detail based on user query id"
    eventid = request.args.get('incident')
    cached_query = cache.get('incident-%s' % eventid)
    if cached_query is None:
        cnx = dbNTSB.connect()
        eventDetail = dbNTSB.query(
            cnx, "select ev_date, ev_city, ev_state, country_name from events inner join country on events.ev_country = country.country_code where ev_id = '%s'" % eventid)
        casualtyDetail = dbNTSB.query(
            cnx, "select inj_count from injurytotal_view where ev_id = '%s'" % eventid)
        engineDetail = dbNTSB.query(
            cnx, "select eng_model, eng_mfgr from engines where ev_id = '%s'" % eventid)
        aircraftDetail = dbNTSB.query(
            cnx, "select acft_model, acft_make, type_fly from aircraft where ev_id ='%s'" % eventid)
        narrativeDetail = dbNTSB.query(
            cnx, "select narr_accp, narr_accf, narr_cause from narratives where ev_id = '%s'" % eventid)
        if not casualtyDetail:
            casualtyDetail = ({'inj_count': Decimal('0')},)
        response = json.dumps(eventDetail + casualtyDetail + engineDetail + aircraftDetail + narrativeDetail,
                              sort_keys=True, indent=4, separators=(',', ':'), default=json_date_handler, ensure_ascii=False)
        cache.set('incident-%s' % eventid, response, timeout=60 * 60 * 24)
        print "[IDReq] cached query for later loading"
        dbNTSB.close(cnx)
    else:
        print "[IDReq] using cached query mode"
        response = cached_query
    return response


@app.route('/api/v2/ntsb/incidents/similarincidents', methods=['GET'])
def getsimilarIncidents():
    print "[SIReq] get similar incident based on user query id"
    eventid = request.args.get('incident')
    index = 0
    found = False
    # no cache will be used for similarity
    for i in dataset:
        if i['event_id'] == eventid:
            found = True
            break
        else:
            index = index + 1
    if not found:
        response = "[Err] API error"
        print response
    else:
        similarities = numpy.dot(dtmLSA, dtmLSA.T[:, index])
        related_docs_indices = similarities.argsort()[:-10:-1]
        testData = returnTD()
        relatedIncidentsID = []
        for x in related_docs_indices:
            if dataset[x]['event_id'] == eventid:
                continue
            relatedIncidentsID.append(dataset[x]['event_id'])

        # Process each event_id in relatedIncidents
        relatedIncidents = []
        cnx = dbNTSB.connect()
        for i in relatedIncidentsID:
            eventDetail = dbNTSB.query(
                cnx, "select events.ev_id, ev_date, ev_city, ev_state, country_name, inj_count from events inner join country on events.ev_country = country.country_code left join injurytotal_view on events.ev_id = injurytotal_view.ev_id where events.ev_id = '%s'" % i)
            relatedIncidents.append(eventDetail)
        dbNTSB.close(cnx)

        response = json.dumps(relatedIncidents, sort_keys=True,
                              indent=4, separators=(',', ':'), default=json_date_handler)
    return response

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
