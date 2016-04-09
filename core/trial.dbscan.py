from __future__ import print_function
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from stopwords import get_english_stop_words
from nltk.stem import *
from sklearn.cluster import DBSCAN, KMeans
from sklearn.metrics import adjusted_rand_score
from decode import decodeword
from credentials import get_credentials
from sklearn import metrics
import MySQLdb
import sys
import numpy as np
import matplotlib.pyplot as plt

from sklearn.decomposition import PCA

##################### FETCHING DATABASE FOR RESOURCES REQUIRED ###########
db = MySQLdb.connect("127.0.0.1", "aero", get_credentials(), "aerotest")
cursor = db.cursor()
sql = "select narr_cause from narratives where NULLIF(narr_cause, '') IS NOT NULL limit;"
#sql = "select ev_id, narr_accp, narr_accf, narr_cause from narratives where NULLIF(narr_cause, '') IS NOT NULL;"
cursor.execute(sql)
narratives = []
for item in cursor.fetchall():
    narratives.append(item[0])
db.close()
################################# FETCHING ENDS HERE #####################

dataset = []
stop_words = get_english_stop_words()
stemmer = PorterStemmer()

for narrative in narratives:
    words = narrative.replace(',', ' ').split()
    words = [decodeword(word)
             for word in words if word.lower() not in stop_words]
    words = [stemmer.stem(decodeword(word)) for word in words]
    dataset.append(' '.join(words))
    # dataset.append(' '.join(words))

tfidf = TfidfVectorizer(decode_error='ignore', stop_words='english')
matrix = tfidf.fit_transform(dataset)

db = DBSCAN(eps=0.00238442934246, min_samples=10).fit(matrix.toarray())
core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
core_samples_mask[db.core_sample_indices_] = True
labels = db.labels_
terms = tfidf.get_feature_names()
print (db.core_sample_indices_)
for index in db.core_sample_indices_:
    print (terms[index])
# Number of clusters in labels, ignoring noise if present.
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

print('Estimated number of clusters: %d' % n_clusters_)
print("Silhouette Coefficient: %0.3f"
      % metrics.silhouette_score(matrix, labels))
