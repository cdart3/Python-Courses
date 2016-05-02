import nltk

from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from string import punctuation
from nltk.stem.lancaster import LancasterStemmer

text = "Wes had a little lamb. His fleece was white as snow"
sents = sent_tokenize(text)

words = [word_tokenize(sent) for sent in sents]

StopWords = set(stopwords.words('english')+list(punctuation))

NoStopWords = [word for word in word_tokenize(text) if word not in StopWords]

print NoStopWords