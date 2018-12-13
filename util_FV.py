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
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from nltk.stem.snowball import SnowballStemmer
urllib3.disable_warnings()

nlp = StanfordCoreNLP('http://localhots:9000') #NLP object to conduct text analysis
stemmer = SnowballStemmer("spanish") # SnowballStemmer object fo analyzing text in Spanish
#news_api_key = ['a0849f217c5d4628a7350ce96868c85d', '7d337567864a45f19a5fe1a56d31c1bd'] # Api keys for using news.org

news_api_key = ['1a94631ab2124685abc43845400c7ad1', 'a0849f217c5d4628a7350ce96868c85d'] # Api keys for using news.org



def make_soup(myurl):
    '''
    Creates a BeautifulSoup object
    inputs:
        myurl - string with the url
    output:
        BeautifulSoup object
    '''
    pm = urllib3.PoolManager()
    html = pm.urlopen(url = myurl, method = 'GET', redirect= False).data
    return bs4.BeautifulSoup(html, 'html5lib')

def get_text_news(url, tag = 'p'):
    '''
    Extracts the text part from the BeautifulSoup object
    using the tag p. Other parts of the BeautifulSoup object can be
    retrieved by changing the tag.
    inputs:
        url - string with the url
        tag - tag to aceess the info. Default is 'p'
    output:
        string with text
    '''
    url = valid_url(url)
    soup = make_soup(url)
    text = ' '.join([t.text.encode('utf-8', 'ignore').decode('utf-8') for t in \
    soup.find_all('p')])
    #print(url)
    return text

def valid_url(url):
    '''
    If the url contains strange characters, it cleans it by encoding the text
    to utf-8
    inputs:
        url - string (raw URL text)
    output:
        valid url (string)
    '''
    a=urllib.parse.urlsplit(url)
    valid = urllib.parse.urlunparse((a.scheme, a.netloc,
                                     urllib.parse.quote(a.path.encode('utf-8')),\
                                      '','', ''))
    return valid

def get_entities(text, nlp=nlp):
    '''
    Extracts entities from a corpus of text_from_url
    inputs:
        text - string to be analyzed
        nlp -  NLP object to conduct the analysis
    output:
        dictionary - dictionary with entities
    '''
    return nlp.annotate(text, properties={'annotators': 'ner', 'outputFormat': 'json'})


def get_entity_tup(annotator_dict):
    '''
    Creates a list with the entities found in a text
    inputs:
        annotator_dict - dictionary with entities
    output:
        list with entities
    '''
    ners = []
    for sentence in annotator_dict['sentences']:
        for entity in sentence['entitymentions']:
            ners.append((entity['ner'],entity['text']))
    return list(set(ners))


def is_relevant(tup_list, relevant_words):
    '''Determines if a text found in a news is relevant for this work
    It compares stemmed words in the news against a list of stemmed words that is
    relevant for the project (e.g. if a text contains the stemmed word from homicide 'homic',
    it will keep the news)
    inputs:
        tup_list: tuple with entities
        relevant_words: list of relevant words to be compared with
    output:
        integer (1 if is relevant, 0 otherwise)'''

    relevant_tags = ['CAUSE_OF_DEATH', 'CRIMINAL_CHARGE']
    entity_list = [tup[1] for tup in tup_list if tup[0] in relevant_tags]
    to_compare = set([stemmer.stem(entity.lower()) for entity in entity_list])
    relevant_words = set(relevant_words)
    intersect = list(relevant_words.intersection(to_compare))
    if len(intersect) > 0:
        return 1
    else:
        return 0

def get_content2(article):
    '''
    Extracts relevant articles from the sources.
    Inputs:
        article: raw list of articles coming from the requests
    Output:
    '''
    print('get_content2 working')
    text = get_text_news(article['url'])
    entities = get_entities(text, nlp)
    print(entitites)
    tuple_entities = get_entity_tup(entities)
    relevance = is_relevant(tuple_entities, relevant_words)
    if relevance == 1:
        return text
#return get_text_news(article['url'])


def build_keywords_list(cities_list, crimes_list):
    '''Creates a list with keywords needed for running the search
    inputs:
        cities_list: list of relevant cities
        crimes_list: list of relevant crimes
    output:
        list with all city and crime combinations
        '''
    crimes_string = ' OR '.join(crimes_list)
    return [city+' AND '+'('+crimes_string+')' for city in cities_list]



def build_url(keywords_list, date_from, date_to, language = 'es', key=news_api_key):
    '''constructs a url to run the search
    inputs:
        keywords_list:  list of keywords for running the search
        date_from:      date when the search starts (string)
        date_to:        date when the search ends (string)
        language:       language in which results are retrieved. Default is Spanish (string)
        key:            API key (string)
    output:
        url (string)
        '''
    url = 'https://newsapi.org/v2/everything?q={}&from={}&to={}&language={}&sortBy=relevancy&pageSize=100&apiKey={}'
    keywords = urllib.parse.quote(keywords_list)
    myurl = url.format(keywords, date_from, date_to, language, key)
    return myurl

def get_news_json(myurl):
    '''Create a json file with the information from the news that contains a specific search
    inputs:
        myurl (string)
    output:
        json file
    '''
    http = urllib3.PoolManager()
    r = http.request('GET', myurl)
    return json.loads(r.data.decode('utf-8'))

def get_values(articles_list, key):
    '''
    Creates a list with values from the key in the json dictionary
    that contains a news
    inputs:
        articles_list: list of dictionaries
        key: key in the dictionary
    returns:
        list
    '''
    return [article[key] for article in articles_list]

# def text_from_url(url, content):
# 	soup = make_soup(url)
# 	all_text = [t.text for t in soup.find_all(True) if content in t.text]
# 	lens = [len(i) for i in all_text]
# 	index_text = lens.index(max(lens))
# 	return all_text[index_text]

def news_dict_of_dict(responses):
    '''Creates a dictionary of dictionaries where the key
    is a unique ID for each news, and the value is a dictionary with the contents
    of the news
    input: responses (list)
           it's the output from the requests. Each element of this list is a dictionary with one or many
           news
    output: a new dictionary with an id for each news

           '''
    news_collection = []
    for response in responses:
        if 'articles' in response.keys():
            for article in response['articles']:
                news_collection.append(article)
    return news_collection

def similarity_score(dict1,dict2):
    '''Returns a similarity score to test if two strings
    in two 'different' news are in reality the same
    inputs: dict1 and dict2: dictionaries
    output: score (int)'''
    score_1 = fuzz.token_set_ratio(dict1['title'], dict2['title'])
    score_2 = fuzz.token_set_ratio(dict1['description'], dict2['description'])
    score_3 = fuzz.token_set_ratio(dict1['content'], dict2['content'])
    return 0.4*score_1 + 0.3*score_2 + 0.3*score_3

#
# def compare_similarity(d):
#     '''Compares how similar  two different news are'''
#     size = len(d)
#     t = 80
#     for start in range(size):
#         temp = []
#         for key in range(start + 1, size):
#             if d[key]['unique'] == 1:
#                 s = similarity_score(d[start], d[key])
#                 if s > t:
#                     temp.append(key)
#         for index in temp:
#             d[index]['unique'] = 0
# from nltk.corpus import stopwords

def clean_sentence(sentence):
    '''
    Removes unknown characters or unknown words, change capital to lower letters and remove
    english stop words
    Inputs:
        Sentence (string): a sting to be cleaned
    Output:
        Cleaned sentence (string)
    '''
    new = ''
    for l in sentence:
        if re.match('[a-zA-Z0-9_\s]',l):
            new += l

    tokens = nltk.word_tokenize(new)
    tokens = [t.lower() for t in tokens]

    new_tokens = []
    imp_words = set(stopwords.words('spanish'))
    for t in tokens:
        if t in imp_words:
            new_tokens.append(t)

    return ' '.join(new_tokens)

def get_content(article):
    '''
    populates articles dictionaries with content, entity mentions
    and relevance classification.
    Inputs:
    -article_dict(dictionary): dictionary with articles from
     news API responses
    -results (mp.manager dictionary object): dictionary to store
     the results
    returns mp.manager dictionary object with updated results.
    '''
#     article['content'] = get_text_news(article['url'])
#     article['entitymentions'] = get_entity_tup(get_entities(article['content']))
#     article['relevant'] = is_relevant(article['entitymentions'], relevant_words)
#     return article
    return get_text_news(article['url'])
