from __future__ import print_function
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from stopwords import get_english_stop_words
from credentials import get_credentials
from nltk.stem import *
from decode import decodeword
import MySQLdb
import sys
import numpy

stop_words = get_english_stop_words()
stemmer = PorterStemmer()
dataset = []
testData = []

db = MySQLdb.connect("127.0.0.1", "aero", get_credentials(), "aerotest")
cursor = db.cursor()
sqlA = "select distinct ev_id from aircraft_accident order by ev_id"
cursor.execute(sqlA)
effectiveEventId = []
for item in cursor.fetchall():
    effectiveEventId.append(item[0])
db.close()

db = MySQLdb.connect("127.0.0.1", "aero", get_credentials(), "aerotest")
cursor = db.cursor()
sqlB = "select distinct ev_id, narr_cause from narratives where NULLIF(narr_cause, '') IS NOT NULL order by ev_id"
cursor.execute(sqlB)
narratives = []
for item in cursor.fetchall():
    narratives.append({
        "event_id": item[0],
        "cause": item[1]
    })
db.close()

for eventId in effectiveEventId:
    for x in narratives:
        if x['event_id'] == eventId:
            index = narratives.index(x)
            temp = narratives[index]['cause'].split()
            temp = [decodeword(word) for word in temp if word.lower() not in stop_words]
            temp = [stemmer.stem(decodeword(word)) for word in temp]
            dataset.append({
                "event_id": eventId,
                "cause": ' '.join(temp),
                "original-text": narratives[index]['cause']
            })
            continue

for record in dataset:
    testData.append(record['cause'])

vectorizer = TfidfVectorizer(
    min_df=1, stop_words='english', decode_error='ignore')
tfidf = vectorizer.fit_transform([narrative for narrative in testData])


cosine_similarities = (tfidf * tfidf.T).A;

for i in range(0, len(dataset)):
    cosine_similarities = linear_kernel(tfidf[i:i + 1], tfidf).flatten()
    related_docs_indices = cosine_similarities.argsort()[:-10:-1]
    print(related_docs_indices)
    print(cosine_similarities[related_docs_indices])
    for index in related_docs_indices:
        print(dataset[index]['original-text'])
