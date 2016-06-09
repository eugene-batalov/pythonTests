# -*- coding: utf-8 -*-
"""
Created on Fri May 20 23:48:51 2016

@author: galinabatalova
"""
import urllib
import ssl
import time
from multiprocessing.dummy import Pool as ThreadPool

def timer(f):
    def tmp(*args, **kwargs):
        t = time.time()
        res = f(*args, **kwargs)
        print ("Время выполнения функции: %f секунд" % (time.time()-t))
        return res
    return tmp

@timer
def run(threads):
    urls = ['http://www.python.org',
    	'http://www.python.org/about/',
    	'http://www.onlamp.com/pub/a/python/2003/04/17/metaclasses.html',
    	'http://www.python.org/doc/',
    	'http://www.python.org/download/',
    	'http://www.python.org/getit/',
    	'http://www.python.org/community/',
    	'https://wiki.python.org/moin/',
    	'http://planet.python.org/',
    	'https://wiki.python.org/moin/LocalUserGroups',
    	'http://www.python.org/psf/',
    	'http://docs.python.org/devguide/',
    	'http://www.python.org/community/awards/'
         ]
    results = []
    scontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    
    requests = [urllib.request.Request(url=url,data=b'None',
                headers={'User-Agent':' Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'})
                for url in urls]
    pool = ThreadPool(threads)    
    results = list(pool.map(lambda x: urllib.request.urlopen(x, context=scontext), requests))
    pool.close()
    pool.join()

    dataLen = [len(result.read().decode('utf-8')) for result in results]
    print(threads, 'поток(ов), прочитано', sum(dataLen), 'байт')

run(9)