
import requests 
from requests import get
from bs4 import BeautifulSoup
from collections import Counter
from string import punctuation
import pandas as pd
import csv
import itertools
import numpy as np
import string
import unicodedata

#Set variables to file names/locations
url_csv = 'url.csv' #csv file containing all URLs to scrape
keyword_csv = 'keywords,csv'
outfile_name = 'outfile.csv'


def analyse_online_archive(url_csv, keyword_csv, outfile_name):
	# List of URLs for each day of Spiegel Online web archives
	with open(url_csv, 'r') as f:
		reader = csv.reader(f)
		url_list = list(reader)
	url_list = list(itertools.chain(*url_list))

	# Create corresponding list of URL IDs/issue numbers
	url_id = [str(i) for i in range(1, len(url_list)+1)]

	# Create list of keywords from 'keyword_stems.csv'
	with open(keyword_csv, 'r', encoding = 'utf-8-sig') as f:
		reader = csv.reader(f)
		keywords = list(reader)
	keywords = list(itertools.chain(*keywords))

	a = 1 #set counter to 1

	punct = '!"#$%\'()*+,-./:;<=>?@[\\]^_`{}~'
	transtab = str.maketrans(dict.fromkeys(punct, ''))
	keyword_counter = []	
	for url in url_list:
		r = requests.get(url)
		soup = BeautifulSoup(r.content, features = "html.parser")
		text_li = (''.join(s.findAll(text = True))for s in soup.findAll('li'))
		
		counts = Counter((x.rstrip(punctuation).lower() for y in text_li for x in y.split()))
		list_headlines  = counts.most_common()

		keyword_hits_list = []
		for x in range(0, len(list_headlines)):
			temp = list(list_headlines[x]) # convert from tuple to list
			temp[1] = str(temp[1]) #change number (at index 1) into string
			n_temp = [(unicodedata.normalize('NFKD', word).encode('ASCII', 'ignore')).lower().decode() for word in temp] #normalised umlauts in data
			
			#check word (at index 0) against list of keywords, add new column = 1 if match, = 0 otherwise.
			hits = 0 
			for i in range(0, len(keywords)):
				if keywords[i] in n_temp[0]:
					hits = hits + 1
			if hits != 0:
				n_temp.append(1)
			else:
				n_temp.append(0)
			
			keyword_hits = int(n_temp[1])*int(n_temp[2])
			keyword_hits_list.append(keyword_hits)
		
		keyword_counts = sum(keyword_hits_list)
		keyword_counter.append(keyword_counts)
		
		print("day {0} complete".format(a))

		if list_headlines != []:
			a = a + 1
		else:
			break

	df = pd.DataFrame({"id": url_id, "keywords": keyword_counter})
	df.to_csv(outfile_name, index=False)
	

analyse_online_archive(url_csv, keyword_csv, outfile_name)




	