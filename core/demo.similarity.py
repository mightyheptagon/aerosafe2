from __future__ import print_function
from stopwords import get_english_stop_words
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from nltk.stem import *
from math import log

stop_words = get_english_stop_words()
stemmer = PorterStemmer()

examples = ["Machine learning is super fun", "Python is super, super cool",
"Statistics is cool, too",
"Data science is fun",
"Python is great for machine learning",
"I like football",
"Football is great to watch"]

examples = ["The game of life is a game of everlasting learning",
"The unexamined life is not worth living",
"Never stop learning"]
# structure
# + articles
# |+ article_tokens
#  |+ article
#   |- token

# Split a list of articles into a list of articles in form of tokens
# ["I am a boy", "I am a girl"] -> [["I", "am", "a", "boy"], ["I", "am", "a", "girl"]]
def article_tokenize(articles):
    article_tokens = []
    for temp in articles:
        temp=temp.lower()
        article_tokens.append(temp.replace(',',' ').split()) # tokenize
    return article_tokens

# Cleaning data with stop-words
def stopword_filter(article_tokens):
    for article in article_tokens:
        for token in article:
            if token in stop_words:
                article.remove(token)
    return article_tokens

# Stemming
def stemming(article_tokens):
    return [[stemmer.stem(token) for token in article] for article in article_tokens]

# Tf calculation # normalized
def tfcalc(token, article):
    return article.count(token)/float(len(article))

# IDF calculation
def idfcalc(token, article_tokens):
    countDoc=0 # count of articles with the token
    for article in article_tokens:
        if token in article:
            countDoc=countDoc + 1

    if countDoc>0:
        return 1.0 + (log(float(len(article_tokens))/countDoc))
    else:
        return 1.0

# Cosine similarity
# def cos_similiarity(query, target):

# Debug
x = article_tokenize(examples)
x = stopword_filter(x)
x = stemming(x)
tfidf = TfidfVectorizer().fit_transform(x)
