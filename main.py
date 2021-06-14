import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import re
from classes import *

url = 'https://www.thetvdb.com/series/la-casa-de-papel'
url2 = 'https://www.thetvdb.com/movies/a-time-to-kill'

def crawl_index(soup):
    serie_id = ''
    titles = {}
    descriptions = {}
    genres = []

    serie_id = re.findall("\d+",soup.find('li', {'class' : 'list-group-item clearfix'}).text)[0]
    descriptions_divs = soup.find_all('div' , {"class" : 'change_translation_text'})
    generes_li = soup.find_all('li',  {'class' : 'list-group-item clearfix'})
    
    #find modify date
    for l in generes_li:
        for s in l.find_all('strong'):
            if 'Modified' in s.text:
                modify_date = l.find('span').text
    #find genres
    for l in generes_li:
        for span in l.find_all('span'):
            for a in span.find_all('a', href=re.compile('genres')):
                genres.append(a.text)
    #find description
    for d in descriptions_divs:
        titles.update({d['data-language'] : d['data-title']})
        descriptions.update({d['data-language'] : d.text})
    return serie_id, titles, descriptions, genres, modify_date

def crawl_seasons(soup):
    url_list = []
    li_group_seasons = soup.find('div' , {'class' : 'season_append'}).find('ul').find_all('li', {'class' : 'list-group-item'})
    for li in li_group_seasons:
        if li.get('data-number') is not None:
            url_list.append(li.find('a')['href'])
    return url_list

def crawl_episodes(url):
    print('thread start with url {}'.format(url))
    code = requests.get(url)
    plain = code.text
    soup = BeautifulSoup(plain, 'html.parser')
    print(plain)

def crawl(url):
    code = requests.get(url)
    plain = code.text
    soup = BeautifulSoup(plain, 'html.parser')
    serie_id, titles, descriptions, genres, modify_date = crawl_index(soup)
    season_url_list = crawl_seasons(soup)
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(crawl_episodes, season_url_list)


crawl(url)