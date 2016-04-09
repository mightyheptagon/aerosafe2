from numpy import zeros
from scipy.linalg import svd
from math import log
from numpy import asarray, sum
from nltk.corpus import stopwords
from sklearn.preprocessing import Normalizer
from stopwords import get_english_stop_words
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

titles = ["There is a myth that all lementable boys go to club every night in Hong Kong", "Hong Kong has a world-known skyline, you can take the tram there to enjoy the view", "It is such a great pleasure to walk on this trail on Sunday", "Lan Kwai Fong has so many club and it is one of the best place for drinking"]
vectorizer = TfidfVectorizer(max_df=0.5,stop_words='english')
X = vectorizer.fit_transform(titles)
lsa = TruncatedSVD(23)
X = lsa.fit_transform(X)
X = Normalizer(copy=False).fit_transform(X)

print(cosine_similarity(X))
