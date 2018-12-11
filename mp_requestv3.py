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

url_requests = [util.build_url(k, '2018-12-05T00:00:00', '2018-12-10T23:59:59') for k in keywords][:10]


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
    
l = util.news_dict_of_dict(list_with_news)

################################################
def update_dict(q, l):

    while True:
        article = q.get()
        l.append(util.get_content(article))
        if q.empty():
            q.close()
            print("Queue closed")
            break

#if __name__ == '__main__':
#     p = mp.Pool(3)
#     result = p.map(get_content, l)
#     p.start()
#     p.join()
#     p.close()
# print(result.get())
#     dictionary = manager.dict()
#     p = mp.Pool(3)
#     dictionary = p.map_async(get_content,list_of_links)
#     p.close()
#     p.join()

q = mp.Queue()
manager = mp.Manager()
list_of_dict = manager.list()
p1 = mp.Process(name='putting urls in q', target=put_in_queue, args=(l, q))
p2 = mp.Process(name='create news', target=update_dict, args=(q, list_of_dict))
p3 = mp.Process(name = 'create news again', target=update_dict, args=(q, list_of_dict))

p1.start()
p2.start()
p3.start()
p1.join()
p2.join()
p3.join()
