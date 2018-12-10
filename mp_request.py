import pandas as pd
import multiprocessing as mp 
import util


zm_mex = pd.read_csv('zmmex.csv')[['CVE_MUN', 'MUN']]

crimes = ['homicidio', 'homicidios', 'muerto', 'muerte', 'muertos', 'muertes',  
          'asesinato', 'asesinatos', 'asesinados', 'asesinado',
          'ejecucion', 'ejecuciones', 'ejecutado', 'ejecutados',
          'secuestro', 'secuestros','secuestrado', 'secuestrada', 'secuestrados', 'secuestradas',
          'rapto', 'raptos', 'raptado', 'raptados', 'raptadas' 
          'levanton', 'levantones'
          'feminicidio', 'feminicidios', 'asesinada', 'asesinadas', 'muerta','muertas']

cities = list(set(zm_mex['MUN']))

keywords = util.build_keywords_list(cities, crimes)

url_requests = [util.build_url(k, '2018-12-03T00:00:00', '2018-12-03T23:59:59') for k in keywords][:10]


def put_in_queue(inputs_list, q):
	for inp in inputs_list:
		q.put(inp)

def make_req(q, l):
	count = 0
	while True:
		myurl = q.get()
		l.append(util.get_news_json(myurl))
		count +=1

		if q.empty():
			q.close()
			print("Queue closed")
			break


## multiprocessing part

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

	#print(list_with_news)
d = util.news_dict_of_dict(list_with_news)
for k, v in d.items():
	v['entitymentions'] = None
    v['relevant'] = 0

#util.compare_similarity(d)
#list_of_links = util.get_values(d,'url')

def get_content(article_dict, results_mg):
    '''
    populate articles dictionaries with contente, entity mentions 
    and relevance classification.
    Inputs:
    -article_dict(dictionary): dictionary with articles from 
     news API responses
    -results (mp.manager dictionary object): dictionary to store 
     the results
    returns mp.manager dictionary object with updated results.
    '''
    article_dict['content'] = util.get_text_news(article_dict['url'])
    article_dict['entitymentions'] = util.get_entity_tup(get_entities(article_dict['content']))
    article_dict['relevant'] = is_relevant(article_dict['entitymentions'], relevant_words)
    return article_dict


if __name__ == '__main__':
    p = mp.Pool(3)
    result = p.map_async(get_content, list_of_links ) 
    p.close()
    p.join()
    
list_of_texts = result.get()
print(list_of_texts)