import requests
from bs4 import BeautifulSoup


BASE_URL = 'https://mangareader.to'

class MangaReaderAPI:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MangaReaderAPI, cls).__new__(cls)
        return cls._instance

    def search_manga(self, query):
        try:
            response = requests.get(f'{BASE_URL}/search?keyword={query}')
            response.raise_for_status()
            data = response.text
            soup = BeautifulSoup(data, 'html.parser')

            results = []
            items = soup.select('div.manga_list-sbs div.mls-wrap div.item')
            for item in items:
                manga_result = {
                    'id': item.select_one('a.manga-poster')['href'].split('/')[1],
                    'title': item.select_one('div.manga-detail h3.manga-name a').text.strip(),
                    'image': item.select_one('a.manga-poster img')['src'],
                    'genres': [genre.text for genre in item.select('div.manga-detail div.fd-infor span > a')]
                }
                results.append(manga_result)

            return results
        except requests.RequestException as e:
            print(f"Error performing search: {e}")
            return []

    def fetch_manga_info(self, manga_id):
        url = f'{BASE_URL}/{manga_id}'
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.text
            soup = BeautifulSoup(data, 'html.parser')

            container = soup.select_one('div.container')

            manga_info = {
                'id': manga_id,
                'title': container.select_one('div.anisc-detail h2.manga-name').text.strip(),
                'image': container.select_one('img.manga-poster-img')['src'],
                'description': container.select_one('div.modal-body div.description-modal').text.replace('\n', ' ').strip(),
                'genres': [genre.text.strip() for genre in container.select('div.sort-desc div.genres a')],
                'chapters': []
            }

            chapters = container.select('div.chapters-list-ul ul li')
            for chapter in chapters:
                manga_chapter = {
                    'id': chapter.select_one('a')['href'].split('/read/')[1],
                    'title': chapter.select_one('a')['title'].strip(),
                    'chapter': chapter.select_one('a span.name').text.split('Chapter ')[1].split(':')[0]
                }
                manga_info['chapters'].append(manga_chapter)

            return manga_info
        except requests.RequestException as e:
            print(f"Error fetching manga info: {e}")
            return None

    def fetch_chapter_pages(self, chapter_id):
        url = f'{BASE_URL}/read/{chapter_id}'
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.text
            soup = BeautifulSoup(data, 'html.parser')

            reading_id = soup.select_one('div#wrapper')['data-reading-id']

            if not reading_id:
                raise Exception('Unable to find pages')

            ajax_url = f'https://mangareader.to/ajax/image/list/chap/{reading_id}?mode=vertical&quality=high'
            response = requests.get(ajax_url)
            response.raise_for_status()
            pages_data = response.json()['html']
            pages_soup = BeautifulSoup(pages_data, 'html.parser')

            pages = []
            items = pages_soup.select('div#main-wrapper div.container-reader-chapter div.iv-card')
            for i, item in enumerate(items):
                page = {
                    'img': item['data-url'].replace('&amp;', '&'),
                    'page': i + 1
                }
                pages.append(page)

            return pages
        except requests.RequestException as e:
            print(f"Error fetching chapter pages: {e}")
            return []
        
    def get_hot_manga(self):
        try:
            url = f'{BASE_URL}/home'
            response = requests.get(url)
            response.raise_for_status()
            data = response.text
            soup = BeautifulSoup(data, 'html.parser')

            trending_manga = []
            items = soup.select('div.item')

            for item in items:
                title_tag = item.select_one('div.manga-poster img')
                image_tag = item.select_one('div.manga-poster img')
                link_tag = item.select_one('div.manga-poster a.link-mask')
                alias_name_tag = item.select_one('p.alias-name')
                rating_tag = item.select_one('div.mp-desc p i.fa-star')
                languages_tag = item.select_one('span.tick-lang')
                latest_chapter_tag = item.select('p a i.far.fa-file-alt')
                
                if not title_tag or not image_tag or not link_tag:
                    continue

                manga = {
                    'title': title_tag['alt'],
                    'image': image_tag['src'],
                    'link': BASE_URL + link_tag['href'],
                    'alias_name': alias_name_tag.text.strip() if alias_name_tag else None,
                    'rating': rating_tag.parent.text.strip() if rating_tag else None,
                    'languages': languages_tag.text.strip() if languages_tag else None,
                    'latest_chapter': latest_chapter_tag[0].parent['href'] if latest_chapter_tag else None,
                    'latest_volume': latest_chapter_tag[1].parent['href'] if len(latest_chapter_tag) > 1 else None
                }

                # Only add the manga if it has the essential information
                if manga['title'] and manga['image'] and manga['link']:
                    trending_manga.append(manga)

            return trending_manga
        except requests.RequestException as e:
            print(f"Error fetching hot manga: {e}")
            return []

