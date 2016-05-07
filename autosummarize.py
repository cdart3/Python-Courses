#!/usr/bin/python
''' Multiline comment example
Take in the url of a newspaper article and automatically summarize it in 3 sentences
This exercise is based pretty much entirely off this blog post:
http://glowingpython.blogspot.in/2014/09/text-summarization-with-nltk.html
'''

from nltk.tokenize import sent_tokenize as st, word_tokenize as wt
from nltk.corpus import stopwords
from collections import defaultdict
from string import punctuation
from heapq import nlargest
import urllib2
from bs4 import BeautifulSoup

def getWashPostText(url):
	""""
	This is specific to Washington Post, because of the html/CSS structure
	Algorithm:
		1. downloads contents of url using try catch
		2. extracts article from html
		3. fetch everything betweeen article tags
		4. grab innerHTML from p tags
	returns article title and article body
	"""

	try:

		page = urllib2.urlopen(url).read().decode('utf8')

	except:
		return (None,None)

	soup = BeautifulSoup(page, "html.parser") # Beautiful soup threw me a warning to add "html.parser" as a second param
	if soup is None:
		return (None, None)

	text = ' '.join(map(lambda p: p.text, soup.find_all('article')))
	soup2 = BeautifulSoup(text, "html.parser") # See comment above
	p_tags = ' '.join(map(lambda p: p.text, soup2.find_all('p')))
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
		return [sents[j] for j in sents_idx] # sexy list comprehension

	def print_summary(self,summary):
		'''
		TODO: define this in class -> def __str__(self):
		given output of summarize()
		returns as string
		no return
		'''
		for line in summary:
			print line

def main():
	wp_url = "https://www.washingtonpost.com/news/the-switch/wp/2016/05/02/hulu-may-soon-offer-live-tv-including-sports/"
	wp_text = getWashPostText(wp_url)
	fs = FrequencySummarizer()
	summary = fs.summarize(wp_text[1], 3)
	fs.print_summary(summary)

'''
if you chmod u+x file_name and have the lines below
you can use ./autosummarize to run this program 
instead of 
python program name
'''
if __name__ == '__main__':
	main()
