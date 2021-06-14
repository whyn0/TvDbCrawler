from concurrent import futures
import concurrent
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import re
import classes

base_url = 'https://www.thetvdb.com'
url = 'https://www.thetvdb.com/series/la-casa-de-papel'
url2 = 'https://www.thetvdb.com/movies/a-time-to-kill'


def crawl_index(soup):
    serie_id = ''
    titles = {}
    descriptions = {}
    genres = []

    serie_id = re.findall("\d+", soup.find('li', {'class': 'list-group-item clearfix'}).text)[0]
    descriptions_divs = soup.find_all('div', {"class": 'change_translation_text'})
    generes_li = soup.find_all('li', {'class': 'list-group-item clearfix'})

    # find modify date
    for l in generes_li:
        for s in l.find_all('strong'):
            if 'Modified' in s.text:
                modify_date = l.find('span').text
    # find genres
    for l in generes_li:
        for span in l.find_all('span'):
            for a in span.find_all('a', href=re.compile('genres')):
                genres.append(a.text)
    # find description
    for d in descriptions_divs:
        titles.update({d['data-language']: d['data-title']})
        descriptions.update({d['data-language']: d.text})
    return serie_id, titles, descriptions, genres, modify_date


def crawl_season_list(soup):
    season_alternatives = {}
    season_alternatives_titles = [x.text for x in soup.find_all('li', {'role': 'presentation'})]
    season_alternatives_titles.reverse()
    print(season_alternatives_titles)
    # find div of clas tab-content
    div_list = soup.find('div', {'class': 'tab-content'}).find_all('div', {'class': 'season_append'})
    for child in div_list:
        temp_url = []
        for li in child.find_all('li'):
            if li.get('data-number') is not None:
                temp_url.append(li.find('a')['href'])
        season_alternatives.update({season_alternatives_titles.pop(): temp_url})
    return season_alternatives


def crawl_episodes(url):
    code = requests.get(url)
    plain = code.text
    soup = BeautifulSoup(plain, 'html.parser')
    season_descriptions = {x['data-language']: x.text for x in
                           soup.find_all('div', {'class': 'change_translation_text'})}
    episodes_url_list = [base_url + x.find('a')['href'] for x in soup.find_all('td') if x.find('a') is not None]
    procs = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        episodes_list = list(executor.map(threaded_episode_crawler, episodes_url_list))
    return classes.Season(url[-1:], season_descriptions, episodes_list)


def threaded_episode_crawler(url):
    try:
        print('thread started on url {}'.format(url))
        ep_plain = requests.get(url).text
        ep_soup = BeautifulSoup(ep_plain, 'html.parser')
        description_div = ep_soup.find_all('div', {'class': 'change_translation_text'})
        ep_titles = {x['data-language']: x['data-title'] for x in description_div}
        ep_descriptions = {x['data-language']: x.text for x in description_div}
        originally_aired = ep_soup.find('a', href=re.compile('/on-today/\d+')).text
        duration = ep_soup.find('span', string=re.compile('\d+ \S+')).text.strip()
        return classes.Episode(ep_titles, ep_descriptions, originally_aired, duration)
    except Exception as e:
        print(e)
    return None


def crawl(url):
    code = requests.get(url)
    plain = code.text
    soup = BeautifulSoup(plain, 'html.parser')
    serie_id, titles, descriptions, genres, modify_date = crawl_index(soup)
    seasons_url_list = crawl_season_list(soup)
    season_dict = {}
    for key in seasons_url_list.keys():
        season_list = []
        for u in seasons_url_list[key]:
            season_list.append(crawl_episodes(u))
        season_dict.update({key: season_list})
    return classes.Serie(serie_id, titles, descriptions, genres, modify_date, season_dict)


if __name__ == '__main__':
    serie = crawl(url)
    print(serie)