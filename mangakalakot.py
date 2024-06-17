import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://mangakakalot.com'
READMANGANATO_URL = 'https://readmanganato.com'

class MangaKakalotAPI:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MangaKakalotAPI, cls).__new__(cls)
        return cls._instance

    def fetch_manga_info(self, manga_id: str):
        manga_info = {
            'id': manga_id,
            'title': '',
            'altTitles': [],
            'description': '',
            'image': '',
            'genres': [],
            'status': '',
            'views': 0,
            'authors': [],
            'chapters': []
        }
        url = f'{BASE_URL}/{manga_id}' if 'read' in manga_id else f'{READMANGANATO_URL}/{manga_id}'
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.text
            soup = BeautifulSoup(data, 'html.parser')

            if BASE_URL in url:
                manga_info['title'] = soup.select_one('div.manga-info-top > ul > li:nth-child(1) > h1').text
                manga_info['altTitles'] = soup.select_one('div.manga-info-top > ul > li:nth-child(1) > h2').text.replace('Alternative :', '').split(';')
                manga_info['description'] = soup.select_one('#noidungm').text.replace(f'{manga_info["title"]} summary:', '').replace('\n', '').strip()
                manga_info['image'] = soup.select_one('div.manga-info-top > div > img')['src']
                manga_info['genres'] = [genre.text for genre in soup.select('div.manga-info-top > ul > li:nth-child(7) > a')]
                status_text = soup.select_one('div.manga-info-top > ul > li:nth-child(3)').text.replace('Status :', '').strip()
                manga_info['status'] = 'COMPLETED' if status_text == 'Completed' else 'ONGOING' if status_text == 'Ongoing' else 'UNKNOWN'
                manga_info['views'] = int(soup.select_one('div.manga-info-top > ul > li:nth-child(6)').text.replace('View : ', '').replace(',', '').strip())
                manga_info['authors'] = [author.text for author in soup.select('div.manga-info-top > ul > li:nth-child(2) > a')]
                manga_info['chapters'] = [{
                    'id': chapter.select_one('span > a')['href'].split('chapter/')[1],
                    'title': chapter.select_one('span > a').text,
                    'views': int(chapter.select_one('span:nth-child(2)').text.replace(',', '').strip()),
                    'releasedDate': chapter.select_one('span:nth-child(3)')['title']
                } for chapter in soup.select('div.chapter-list > div.row')]
            else:
                manga_info['title'] = soup.select_one('div.panel-story-info > div.story-info-right > h1').text
                manga_info['altTitles'] = soup.select_one('div.story-info-right > table > tbody > tr:nth-child(1) > td.table-value > h2').text.split(';')
                manga_info['description'] = soup.select_one('#panel-story-info-description').text.replace('Description :', '').replace('\n', '').strip()
                manga_info['image'] = soup.select_one('div.story-info-left > span.info-image > img')['src']
                manga_info['genres'] = [genre.text for genre in soup.select('div.story-info-right > table > tbody > tr:nth-child(4) > td.table-value > a')]
                status_text = soup.select_one('div.story-info-right > table > tbody > tr:nth-child(3) > td.table-value').text.strip()
                manga_info['status'] = 'COMPLETED' if status_text == 'Completed' else 'ONGOING' if status_text == 'Ongoing' else 'UNKNOWN'
                manga_info['views'] = int(soup.select_one('div.story-info-right > div > p:nth-child(2) > span.stre-value').text.replace(',', '').strip())
                manga_info['authors'] = [author.text for author in soup.select('div.story-info-right > table > tbody > tr:nth-child(2) > td.table-value > a')]
                manga_info['chapters'] = [{
                    'id': chapter.select_one('a')['href'].split('.com/')[1] + '$$READMANGANATO',
                    'title': chapter.select_one('a').text,
                    'views': int(chapter.select_one('span.chapter-view.text-nowrap').text.replace(',', '').strip()),
                    'releasedDate': chapter.select_one('span.chapter-time.text-nowrap')['title']
                } for chapter in soup.select('div.container-main-left > div.panel-story-chapter-list > ul > li')]

            return manga_info
        except requests.RequestException as e:
            print(f"Error fetching manga info: {e}")
            return None

    def fetch_chapter_pages(self, chapter_id: str):
        try:
            url = f'{BASE_URL}/chapter/{chapter_id}' if '$$READMANGANATO' not in chapter_id else f'{READMANGANATO_URL}/{chapter_id.replace("$$READMANGANATO", "")}'
            response = requests.get(url)
            response.raise_for_status()
            data = response.text
            soup = BeautifulSoup(data, 'html.parser')

            pages = [{
                'img': page['src'],
                'page': i,
                'title': page['alt'].replace('- Mangakakalot.com', '').replace('- MangaNato.com', '').strip(),
                'headerForImage': {'Referer': BASE_URL}
            } for i, page in enumerate(soup.select('div.container-chapter-reader > img'))]

            return pages
        except requests.RequestException as e:
            print(f"Error fetching chapter pages: {e}")
            return []

    def search_manga(self, query: str):
        try:
            response = requests.get(f'{BASE_URL}/search/story/{query.replace(" ", "_")}')
            response.raise_for_status()
            data = response.text
            soup = BeautifulSoup(data, 'html.parser')

            results = [{
                'id': item.select_one('div > h3 > a')['href'].split('/')[3],
                'title': item.select_one('div > h3 > a').text,
                'image': item.select_one('a > img')['src'],
                'headerForImage': {'Referer': BASE_URL}
            } for item in soup.select('div.daily-update > div > div')]

            return results
        except requests.RequestException as e:
            print(f"Error searching manga: {e}")
            return []

    def fetch_hot_manga(self, page=1):
        url = f'{BASE_URL}/manga_list?type=topview&category=all&state=all&page={page}'
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.text
            soup = BeautifulSoup(data, 'html.parser')

            hot_manga = []
            items = soup.select('div.list-truyen-item-wrap')
            for item in items:
                manga = {
                    'title': item.select_one('h3 a').text,
                    'image': item.select_one('a img')['src'],
                    'link': item.select_one('h3 a')['href'],
                    'latest_chapter': item.select_one('a.list-story-item-wrap-chapter').text.strip() if item.select_one('a.list-story-item-wrap-chapter') else 'N/A',
                    'views': item.select_one('span.aye_icon').text.strip() if item.select_one('span.aye_icon') else 'N/A',
                    'description': item.select_one('p').text.strip() if item.select_one('p') else 'N/A'
                }
                hot_manga.append(manga)

            return hot_manga
        except requests.RequestException as e:
            print(f"Error fetching hot manga: {e}")
            return []


