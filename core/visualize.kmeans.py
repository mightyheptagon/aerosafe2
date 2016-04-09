from __future__ import print_function
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from stopwords import get_english_stop_words
from nltk.stem import *
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.decomposition import TruncatedSVD
from decode import decodeword
from sklearn.preprocessing import Normalizer
from sklearn import metrics
import MySQLdb
from sklearn.pipeline import make_pipeline
import sys
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from credentials import get_credentials()

##################### FETCHING DATABASE FOR RESOURCES REQUIRED ###########
db = MySQLdb.connect("127.0.0.1", "aero", get_credentials(), "aerotest")
cursor = db.cursor()
sql = "select narr_cause from narratives, events where DATE_FORMAT(events.ev_date, '%Y-%m') BETWEEN '1985-01' AND '1990-12' and narratives.ev_id = events.ev_id and NULLIF(narr_cause, '') IS NOT NULL;"
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

tfidf = TfidfVectorizer(decode_error='ignore', stop_words='english')
matrix = tfidf.fit_transform(dataset)
true_k = 3

svd = TruncatedSVD(100)
normalizer = Normalizer(copy=False)
lsa = make_pipeline(svd, normalizer)
matrix = lsa.fit_transform(matrix)

explained_variance = svd.explained_variance_ratio_.sum()
print("Explained variance of the SVD step: {}%".format(
    int(explained_variance * 100)))

km = KMeans(n_clusters=true_k, init='k-means++', max_iter=100, n_init=1, verbose=True)

print("Clustering sparse data with %s" % km)
km.fit(matrix)
print()

print("Silhouette Coefficient: %0.3f"
      % metrics.silhouette_score(matrix, km.labels_, sample_size=1000))

print("Top terms per cluster:")

original_space_centroids = svd.inverse_transform(km.cluster_centers_)
order_centroids = original_space_centroids.argsort()[:, ::-1]

terms = tfidf.get_feature_names()
for i in range(true_k):
    print("Cluster %d:" % i, end='')
    for ind in order_centroids[i, :10]:
        print(' %s' % terms[ind], end='')
    print()


reduced_data = PCA(n_components=2).fit_transform(matrix)
kmeans = KMeans(init='k-means++', n_clusters=true_k, n_init=10)
kmeans.fit(reduced_data)

# Step size of the mesh. Decrease to increase the quality of the VQ.
h = .02     # point in the mesh [x_min, m_max]x[y_min, y_max].

# Plot the decision boundary. For that, we will assign a color to each
x_min, x_max = reduced_data[:, 0].min() - 1, reduced_data[:, 0].max() + 1
y_min, y_max = reduced_data[:, 1].min() - 1, reduced_data[:, 1].max() + 1
xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

# Obtain labels for each point in mesh. Use last trained model.
Z = kmeans.predict(np.c_[xx.ravel(), yy.ravel()])

# Put the result into a color plot
Z = Z.reshape(xx.shape)
plt.figure(1)
plt.clf()
plt.imshow(Z, interpolation='nearest',
           extent=(xx.min(), xx.max(), yy.min(), yy.max()),
           cmap=plt.cm.Paired,
           aspect='auto', origin='lower')

plt.plot(reduced_data[:, 0], reduced_data[:, 1], 'k.', markersize=2)
# Plot the centroids as a white X
centroids = kmeans.cluster_centers_
plt.scatter(centroids[:, 0], centroids[:, 1],
            marker='x', s=169, linewidths=3,
            color='w', zorder=10)
plt.title('K-means clustering on the flight incident cause data (PCA-reduced data)\n')
plt.xlim(x_min, x_max)
plt.ylim(y_min, y_max)
plt.xticks(())
plt.yticks(())
plt.show()
