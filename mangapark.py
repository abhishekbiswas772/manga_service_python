import requests
from bs4 import BeautifulSoup
import json

BASE_URL = 'https://v2.mangapark.net'

class MangaParkAPI:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MangaParkAPI, cls).__new__(cls)
        return cls._instance

    def search(self, query, page=1):
        url = f'{BASE_URL}/search?q={query}&page={page}'
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.text
            soup = BeautifulSoup(data, 'html.parser')

            results = []
            items = soup.select('.item')
            for item in items:
                cover = item.select_one('.cover')
                manga = {
                    'id': cover['href'].replace('/manga/', ''),
                    'title': cover['title'],
                    'image': cover.select_one('img')['src']
                }
                results.append(manga)

            return {'results': results}
        except requests.RequestException as e:
            print(f"Error searching manga: {e}")
            return {'results': []}

    def fetch_manga_info(self, manga_id):
        url = f'{BASE_URL}/manga/{manga_id}'
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.text
            soup = BeautifulSoup(data, 'html.parser')

            manga_info = {
                'id': manga_id,
                'title': soup.select_one('div.pb-1.mb-2.line-b-f.hd h2 a').text(),
                'image': soup.select_one('img.w-100')['src'],
                'description': soup.select_one('.limit-html.summary').text(),
                'chapters': []
            }

            chapters = soup.select('.py-1.item')
            for chapter in chapters:
                chapter_info = {
                    'id': f"{manga_id}/" + chapter.select_one('a.ml-1.visited.ch')['href'].split(f'/manga/{manga_id}/')[1].split('/')[0],
                    'title': chapter.select_one('.ml-1.visited.ch').text + chapter.select_one('div.d-none.d-md-flex.align-items-center.ml-0.ml-md-1.txt').text.strip(),
                    'releaseDate': chapter.select_one('span.time').text.strip()
                }
                manga_info['chapters'].append(chapter_info)

            return manga_info
        except requests.RequestException as e:
            print(f"Error fetching manga info: {e}")
            return None

    def fetch_chapter_pages(self, chapter_id):
        url = f'{BASE_URL}/manga/{chapter_id}'
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.text
            soup = BeautifulSoup(data, 'html.parser')

            script_content = soup.find(text=lambda x: 'var _load_pages' in x)
            var_load_pages = script_content.split('var _load_pages = ')[1].split('];')[0] + ']'
            load_pages_json = json.loads(var_load_pages)

            pages = [{'page': page['n'], 'img': page['u']} for page in load_pages_json]

            return pages
        except requests.RequestException as e:
            print(f"Error fetching chapter pages: {e}")
            return []


