import pandas as pd
import multiprocessing as mp
import util
import pandas as pd

# Relevant cities
zm_mex = pd.read_csv('zmmex.csv')[['CVE_MUN', 'MUN']]

# Relevant crimes
crimes = ['homicidio', 'homicidios', 'muerto', 'muerte', 'muertos', 'muertes',
          'asesinato', 'asesinatos', 'asesinados', 'asesinado',
          'ejecucion', 'ejecuciones', 'ejecutado', 'ejecutados',
          'secuestro', 'secuestros','secuestrado', 'secuestrada', 'secuestrados', 'secuestradas',
          'rapto', 'raptos', 'raptado', 'raptados', 'raptadas'
          'levanton', 'levantones'
          'feminicidio', 'feminicidios', 'asesinada', 'asesinadas', 'muerta','muertas']

cities = list(set(zm_mex['MUN']))

# We are splitting the number of requests per account because there is a limit in
#the free trial version
keywords_1 = util.build_keywords_list(cities[:200], crimes)
keywords_2 = util.build_keywords_list(cities[200:], crimes)

#api_keys = ['0b6de9bf595e40829cb5268169ee7ba7','1a94631ab2124685abc43845400c7ad1']
api_keys = ['4c385a784ea8469fb21e04c6ff1647e4', 'ba0ab75193234c3a9df448229437b84c']
url_requests_1 = [util.build_url(k, '2018-12-01T00:00:00', '2018-12-07T23:59:59', key= api_keys[0]) for k in keywords_1]
url_requests_2 = [util.build_url(k, '2018-12-01T00:00:00', '2018-12-07T23:59:59', key= api_keys[1]) for k in keywords_2]
url_requests = url_requests_1 + url_requests_2


def put_in_queue(inputs_list, q):
    '''Puts an input in a Queue object
    Inputs:
        inputs_list: list with inputs to pass
        q: Manager process object
    Output:
        No output
    '''
    for inp in inputs_list:
        q.put(inp)

def make_req(q, l):
    '''makes the request and appends the json files with news to a list
    inputs:
        q: manager process object
        l: list where news will be appended'''
    count = 0
    while True:
        myurl = q.get()
        l.append(util.get_news_json(myurl))
        count +=1
        if q.empty():
            q.close()
            print("Queue closed from first process")
            break



## Multiprocessing part 1
##  In this multiprocessing part, we put the urls in the Queue and make the
# requests to create the news files.

if __name__ == '__main__':
    q = mp.Queue()
    manager = mp.Manager()
    list_with_news = manager.list()
    p1 = mp.Process(name='putting urls in q', target=put_in_queue, args=(url_requests, q))
    p2 = mp.Process(name='getting_req_a', target=make_req, args=(q, list_with_news))
    p3 = mp.Process(name='getting_req_b', target=make_req, args=(q, list_with_news))

    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()

list_with_news = util.news_dict_of_dict(list_with_news) #this creates a list
# with all the news from the requests

################################################
def update_dict(q, l):
    '''creates a list with all news coming from the manager object, selecting
    the relevant ones"
    inputs:
    q:
        Manager object
    l:
        List of news
    output:
        no output
    '''
    while True:
        article = q.get()
        l.append(util.get_content(article))
        if q.empty():
            q.close()
            print("Queue closed")
            break
## Second multiprocessing part
# For each url, it creates the news text and selects the relevant news using the
# function update_dict

if __name__ == '__main__':

    q = mp.Queue()
    manager = mp.Manager()
    list_of_dict = manager.list()
    print('second process:')
    print(list_of_dict, type(list_of_dict))

    p1 = mp.Process(name='putting urls in q', target=put_in_queue, args=(list_with_news, q))
    p2 = mp.Process(name='create news', target=update_dict, args=(q, list_of_dict))
    p3 = mp.Process(name = 'create news again', target=update_dict, args=(q, list_of_dict))
    p1.start()
    p2.start()
    p3.start()

list_of_news = []
for element in list_of_dict:
    list_of_news.append(element)
df = pd.DataFrame(list_of_news)
df.to_csv('first_week2.csv', index = False)

# def get_content(list_with_articles):
#     '''
#     populates articles dictionaries with content, entity mentions
#     and relevance classification.
#     Inputs:
#     -article_dict(dictionary): dictionary with articles from
#      news API responses
#     -results (mp.manager dictionary object): dictionary to store
#      the results
#     returns mp.manager dictionary object with updated results.
#     '''
#     d ={}
#     for article in list_with_articles:
#         relevance = is_relevant(article['entitymentions'], relevant_words)
#         if (is_relevant(article), relevant_words) == 1:
#             d['content'] = article
#             d['entitymentions'] = get_entity_tup(get_entities(article['content']))
#
#     return article
#     #return get_text_news(article['url'])
