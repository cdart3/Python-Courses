# Take in the url of a newspaper article and automatically summarize it in 3 sentences
# This exercise is based pretty much entirely off this blog post:
# http://glowingpython.blogspot.in/2014/09/text-summarization-with-nltk.html

from nltk.tokenize import sent_tokenize as st, word_tokenize as wt
from nltk.corpus import stopwords
from collections import defaultdict
from string import punctuation
from heapq import nlargest
import urllib2
from bs4 import BeautifulSoup


# Step 1: Download contents of url

def getWashPostText(url):
	# This is specific to Washington Post, because of the html/CSS structure

	try:

		page = urllib2.urlopen(url).read().decode('utf8')

	except:
		return (None,None)

	# Step 2: Extract the article from all other html

	soup = BeautifulSoup(page)
	if soup is None:
		return (None, None)

	text = ' '.join(map(lambda p: p.text, soup.find_all('article')))
	# This will fetch everything betweeen article tags

	soup2 = BeautifulSoup(text)

	text = ' '.join(map(lambda p: p.text, soup2.find_all('p')))
	# This will fetch everything within the article tag that has a p tag

	return soup.title.text, text

# Step 3: Figure out the 3 most important sentences in the article
# How? 
# Find the most common words in the article
# Find the sentence in which those most common words occur the most

class FrequencySummarizer:
	def __init__(self, min_cut=0.1,max_cut=0.9):
		self._min_cut = min_cut
		self._max_cut = max_cut
		self._stopwords = set(stopwords.words('english') +list(punctuation))
	
	# If a variable is defined here, it belongs to the class and not to any individual instance

	def _compute_frequencies (self, word_sent):
		# Take in a list of sentences and outputs a dictionary with key:words value:frequency
		freq = defaultdict(int)
		for sentence in word_sent:
			for word in sentence:
				if word not in self._stopwords:
					freq[word] += 1
		# Normalize the frequencies by dividing each by the highest frequency
		# Filter out frequencies that are too high or too low
		max_freq = float(max(freq.values()))
		for word in freq.keys():
			freq[word] = freq[word]/max_freq
			if freq[word] >= self._max_cut or freq[word] <= self._min_cut:
				del freq[word]
		return freq

	def summarize(self, text, n):

		sents = st(text)
		assert n <= len(sents)
		# assert is a way of making sure a condition holds true
		# will throw error if it is false

		word_sent = [wt(s.lower()) for s in sents]
		# list of lists of all the sentences 
		self._freq = self._compute_frequencies(word_sent)
		ranking = defaultdict(int)
		for i,sent in enumerate(word_sent):
			# enumerate creates a tuple with index,element for each entry in the list
			# allows need for a counter variable, but makes it easy to index
			for word in sent:
				if word in self._freq:
					ranking[i] += self._freq[word]

		sents_idx = nlargest(n,ranking, key = ranking.get)
		print [sents[j] for j in sents_idx]

someUrl = "https://www.washingtonpost.com/news/the-switch/wp/2016/05/02/hulu-may-soon-offer-live-tv-including-sports/"

someText = getWashPostText(someUrl)
fs = FrequencySummarizer()
summary = fs.summarize(someText[1], 3)