import MySQLdb
import json
import urllib2
import time
from credentials import get_credentials

db_v = MySQLdb.connect("127.0.0.1", "aero", get_credentials(), "aerotest") # for viewing data
print "mysql connection for fetching data is now established"

cursor_v = db_v.cursor()

cursor_v.execute("select E.lon, E.lat, E.ev_id, concat_ws(' ', trim(E.ev_city), trim(S.name), trim(C.COUNTRY_NAME)) from events as E join states as S on E.ev_state = S.state join Country as C on E.ev_country = C.COUNTRY_CODE where E.approx_loc = true and ((lat is null and lon is null) or (lat = '' and lon = '')) order by E.ev_id ASC")

row = cursor_v.fetchone()

while row is not None:
    print "querying: %s" % \
        (row[3])

    url = "http://nominatim.openstreetmap.org/search/%s?format=json&limit=1" % \
        (row[3].strip().replace(" ", "%20"))

    print url
    count = 0
    print "start geocoding..."

    db_a = MySQLdb.connect("127.0.0.1", "aero", "get_credentials(),", "aerotest") # for updating data
    print "mysql connection for altering data is now established"
    cursor_a = db_a.cursor()

    try:
        response = json.loads(urllib2.urlopen(url).read())
        lat = response[0]['lat'][:10] # limitation constraint of DB
        lon = response[0]['lon'][:10] # limitation constraint of DB
        print "lat: %s lon: %s" % \
            (lat, lon)
        print "updating corresponsing database"
        alter_command = "update events set lat = '%s', lon = '%s' where ev_id = '%s'" % \
            (lat, lon, row[2])
        print ("> %s" % (alter_command))
        cursor_a.execute(alter_command)
        db_a.commit()
        print ("alter success.")
        count = count + 1
    except:
        db_a.rollback()
        print "error: it may be caused by no result returned, or internal error"

    db_a.close()
    row = cursor_v.fetchone()

cursor_v.close()
cursor_a.close()
db_v.close()

print "%i records successfully geo-coded and its relevant record has been updated in the database. "
