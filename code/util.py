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

news_api_key = '7d337567864a45f19a5fe1a56d31c1bd'
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
