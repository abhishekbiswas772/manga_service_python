import requests
from bs4 import BeautifulSoup


BASE_URL = 'https://mangapill.com'

class MangaPillAPI:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MangaPillAPI, cls).__new__(cls)
        return cls._instance

    def search(self, query):
        try:
            response = requests.get(f'{BASE_URL}/search?q={query}')
            response.raise_for_status()
            data = response.text
            soup = BeautifulSoup(data, 'html.parser')

            results = []
            items = soup.select('div.container div.my-3.justify-end > div')
            for item in items:
                manga = {
                    'id': item.select_one('a')['href'].split('/manga/')[1],
                    'title': item.select_one('div > a > div').text.strip(),
                    'image': item.select_one('a img')['data-src']
                }
                results.append(manga)

            return {'results': results}
        except requests.RequestException as e:
            print(f"Error searching manga: {e}")
            return {'results': []}

    def fetch_manga_info(self, manga_id):
        try:
            response = requests.get(f'{BASE_URL}/manga/{manga_id}')
            response.raise_for_status()
            data = response.text
            soup = BeautifulSoup(data, 'html.parser')

            manga_info = {
                'id': manga_id,
                'title': soup.select_one('div.container div.my-3 div.flex-col div.mb-3 h1').text.strip(),
                'description': soup.select_one('div.container div.my-3 div.flex-col p.text--secondary').text.replace('\n', ' '),
                'releaseDate': soup.select_one('div.container div.my-3 div.flex-col div.gap-3.mb-3 div:contains("Year")').text.split('Year\n')[1].strip(),
                'genres': [genre.strip() for genre in soup.select_one('div.container div.my-3 div.flex-col div.mb-3:contains("Genres")').text.split('\n') if genre and genre != 'Genres'],
                'chapters': []
            }

            chapters = soup.select('div.container div.border-border div#chapters div.grid-cols-1 a')
            for chapter in chapters:
                chapter_info = {
                    'id': chapter['href'].split('/chapters/')[1],
                    'title': chapter.text.strip(),
                    'chapter': chapter.text.split('Chapter ')[1]
                }
                manga_info['chapters'].append(chapter_info)

            return manga_info
        except requests.RequestException as e:
            print(f"Error fetching manga info: {e}")
            return None

    def fetch_chapter_pages(self, chapter_id):
        try:
            response = requests.get(f'{BASE_URL}/chapters/{chapter_id}')
            response.raise_for_status()
            data = response.text
            soup = BeautifulSoup(data, 'html.parser')

            pages = []
            chapter_pages = soup.select('chapter-page')
            for page in chapter_pages:
                page_info = {
                    'img': page.select_one('div picture img')['data-src'],
                    'page': float(page.select_one('div[data-summary] > div').text.split('page ')[1])
                }
                pages.append(page_info)

            return pages
        except requests.RequestException as e:
            print(f"Error fetching chapter pages: {e}")
            return []


    def fetch_recently_added_mangas(self):
        try:
            response = requests.get(f'{BASE_URL}/mangas/new')
            response.raise_for_status()
            data = response.text
            soup = BeautifulSoup(data, 'html.parser')

            recently_added = []
            mangas = soup.select('div.grid-cols-2 > div')
            for manga in mangas:
                manga_info = {
                    'title': manga.select_one('a div.mt-3').text.strip(),
                    'image': manga.select_one('a figure img')['data-src'],
                    'link': BASE_URL + manga.select_one('a')['href'],
                    'description': manga.select_one('a div.line-clamp-2.text-xs.text-secondary').text.strip() if manga.select_one('a div.line-clamp-2.text-xs.text-secondary') else '',
                    'tags': [tag.text for tag in manga.select('div.text-xs.leading-5.font-semibold.bg-card.rounded.p-1')]
                }
                recently_added.append(manga_info)

            return recently_added
        except requests.RequestException as e:
            print(f"Error fetching recently added mangas: {e}")
            return []
        


