import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import re
from classes import *

url = 'https://www.thetvdb.com/series/la-casa-de-papel'

def crawl_index(soup):
    serie_id = ''
    titles = {}
    descriptions = {}

    serie_id = re.findall("\d+",soup.find('li', {'class' : 'list-group-item clearfix'}).text)[0]
    descriptions_divs = soup.find_all('div' , {"class" : 'change_translation_text'})
    generes_li = soup.find_all('li',  {'class' : 'list-group-item clearfix'})
    #print(generes_li.get('span'))
    for l in generes_li:
        print(l.get('strong'))
    for d in descriptions_divs:
        titles.update({d['data-language'] : d['data-title']})
        descriptions.update({d['data-language'] : d.text})
    print(serie_id)
    return serie_id, titles, descriptions

def crawl(url):
    code = requests.get(url)
    plain = code.text
    soup = BeautifulSoup(plain, 'html.parser')
    serie_id, titles, descriptions = crawl_index(soup)


crawl(url)