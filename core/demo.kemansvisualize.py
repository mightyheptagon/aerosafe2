'''
Created on Apr 4, 2013

@author: v3ss
'''

from classify import recursive_load_files
from time import time
import numpy as np
import pylab as pl

from sklearn import metrics
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import scale
from sklearn.cluster import KMeans, MiniBatchKMeans
from os.path import isdir
from os import listdir
from os.path import join

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.linear_model import Perceptron, RidgeClassifier, SGDClassifier
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.decomposition import RandomizedPCA
from sklearn.utils.validation import check_random_state
from time import time

import numpy as np
import os

import traceback


def clustering_from_files(trainer_path = "./dataset/dataset/training_data/"):
    classifier = "NB"
    load_files = recursive_load_files
    trainer_path = os.path.realpath(trainer_path)
    data_train = load_files(trainer_path, load_content = True, shuffle = False)



    print "Extracting features from the training dataset using a sparse vectorizer"
    t0 = time()
    vectorizer = TfidfVectorizer(sublinear_tf=True, max_df=0.7,
                                 stop_words='english',charset_error="ignore")

    X_train = vectorizer.fit_transform(data_train.data)

    print "done in %fs" % (time() - t0)

    print "Targets:",data_train.target
    km = MiniBatchKMeans(n_clusters=15, init='k-means++', n_init=1,
                         init_size=1000,
                         batch_size=1000, verbose=1)

#     kmeans = KMeans(init='k-means++', n_clusters=5, n_init=1)
    print "Clustering sparse data with %s" % km
    t0 = time()

    return  (km,X_train)

def reduce_dems(X_train):
    rpca=RandomizedPCA(n_components=2)
    return rpca.fit_transform(X_train)

def plot(kmeans,reduced_data):
    kmeans.fit(reduced_data)
    h = 0.1
    x_min, x_max = reduced_data[:, 0].min() + 1, reduced_data[:, 0].max() - 1
    y_min, y_max = reduced_data[:, 1].min() + 1, reduced_data[:, 1].max() - 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
    Z = kmeans.predict(np.c_[xx.ravel(), yy.ravel()])

    # Put the result into a color plot
    Z = Z.reshape(xx.shape)
    pl.figure(1)
    pl.clf()

    pl.plot(reduced_data[:, 0], reduced_data[:, 1], 'k.', markersize=2)
    # Plot the centroids as a white X
    centroids = kmeans.cluster_centers_
    pl.scatter(centroids[:, 0], centroids[:, 1],
               marker='x', s=20, linewidths=3,
               color='r', zorder=10)
    pl.title('K-means clustering on selected 20_newsgroup (religion group and technology) ')
    pl.xlim(x_min, x_max)
    pl.ylim(y_min, y_max)
    pl.xticks(())
    pl.yticks(())
    pl.show()

def main():
    k_means,X_train = clustering_from_files()
    reduced = reduce_dems(X_train)
    plot(k_means,reduced)

if __name__ == "__main__":
    main()
