import urllib3
import urllib
import json
import pandas as pd
import bs4
import re
import nltk
import datetime
from nltk.corpus import words
from nltk.corpus import stopwords
import math
from pycorenlp import StanfordCoreNLP

news_api_key = 'a0849f217c5d4628a7350ce96868c85d'
crimes = ['homicidio', 'asesinato', 'ejecucion',
'secuestro', 'rapto', 'privacion ilegal de la libertad', 'levanton',
'feminicidio']
cities = []


def make_soup(myurl):
    pm = urllib3.PoolManager()
    html = pm.urlopen(url = myurl, method = 'GET').data
    return bs4.BeautifulSoup(html, 'html5lib')


def build_keywords_list(cities_list, crimes_list):
	crimes_string = ' OR '.join(crimes_list)
	return [city+' AND '+'('+crimes_string+')' for city in cities_list] 



def build_url(keywords_list, date_from, date_to, languaje = 'es', key=news_api_key):
	url = 'https://newsapi.org/v2/everything?q={}&from={}&to={}&language={}&sortBy=relevancy&pageSize=100&apiKey={}'
	keywords = urllib.parse.quote(keywords_list)
	myurl = url.format(keywords, date_from, date_to, languaje, key)
	return myurl

def get_news_json(myurl):
	http = urllib3.PoolManager()
	r = http.request('GET', myurl)
	return json.loads(r.data.decode('utf-8'))

def get_json_values(json_object, key):
	return [article[key] for article in json_object['articles']]

def text_from_url(url, content):
	soup = make_soup(url)
	all_text = [t.text for t in soup.find_all(True) if content in t.text]
	lens = [len(i) for i in all_text]
	index_text = lens.index(max(lens))
	return all_text[index_text]

def similarity_score(dict1,dict2):
    '''Returns a similarity score to test if two strings
    in two 'different' news are in reality the same
    inputs: dict1 and dict2: dictionaries
    output: score (int)'''
    score_1 = fuzz.token_set_ratio(dict1['title'], dict2['title'])
    score_2 = fuzz.token_set_ratio(dict1['description'], dict2['description'])
    score_3 = fuzz.token_set_ratio(dict1['content'], dict2['content'])
    return 0.4*score_1 + 0.3*score_2 + 0.3*score_3
