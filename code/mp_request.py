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

url_requests = [util.build_url(k, '2018-12-03T00:00:00', '2018-12-03T23:59:59') for k in keywords]


def put_in_queue(inputs_list, q):
	for inp in inputs_list:
		q.put(inp)

def make_req(q, l):
	while True:
		myurl = q.get()
		l.append(util.get_news_json(myurl))

		if q.empty():
			q.close()
			print("Queue closed")
			break


## multiprocessing part

if __name__ == '__main__':
	q = mp.Queue()
	manager = mp.Manager()
	l = manager.list()
	p1 = mp.Process(name='putting urls in q', target=put_in_queue, args=(url_requests, q))
	p2 = mp.Process(name='getting_req_a', target=make_req, args=(q, l))
	p3 = mp.Process(name='getting_req_b', target=make_req, args=(q, l))

	p1.start()
	p2.start()
	p3.start()

	p1.join()
	p2.join()
	p3.join()

	print(l)