import requests
from bs4 import BeautifulSoup
import json

BASE_URL = 'https://mangasee123.com'

class MangaSeeAPI:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MangaSeeAPI, cls).__new__(cls)
        return cls._instance

    def search_manga(self, query):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': 'https://mangasee123.com'
            }
            response = requests.get('https://mangasee123.com/_search.php', headers = headers)
            response.raise_for_status()
            data = response.json()
            sanitized_query = query.replace(' ', '').lower()
            matches = []
            for item in data:
                sanitized_alts = [alt.replace(' ', '').lower() for alt in item['a']]

                if (sanitized_query in item['s'].replace(' ', '').lower() or
                        sanitized_query in sanitized_alts):
                    matches.append({
                        'id': item['i'],
                        'title': item['s'],
                        'altTitles': item['a'],
                        'image': f"https://temp.compsci88.com/cover/{item['i']}.jpg",
                        'headerForImage': {'Referer': 'https://mangasee123.com'}
                    })

            return matches
        except requests.RequestException as e:
            print(f"Error performing search: {e}")
            raise

    def get_hot_manga(self):
        try:
            url = 'https://mangasee123.com/hot.php'
            response = requests.get(url)
            response.raise_for_status()
            data = response.text
            soup = BeautifulSoup(data, 'html.parser')
            script_tag = soup.find('script', text=lambda x: x and 'vm.HotUpdateJSON' in x)
            if not script_tag:
                print("Hot manga data not found.")
                return []
            script_content = script_tag.string
            start_index = script_content.find('vm.HotUpdateJSON = ') + len('vm.HotUpdateJSON = ')
            end_index = script_content.find(';', start_index)
            json_data = script_content[start_index:end_index].strip()
            hot_manga_list = json.loads(json_data)
            manga_list = []
            for manga in hot_manga_list:
                manga_list.append({
                    'title': manga['SeriesName'],
                    'chapter': manga['Chapter'],
                    'date': manga['Date'],
                    'image': f"https://temp.compsci88.com/cover/{manga['IndexName']}.jpg",
                    'link': f"https://mangasee123.com/read-online/{manga['IndexName']}-chapter-{manga['Chapter']}-page-1.html"
                })

            return manga_list

        except requests.RequestException as e:
            print(f"Error fetching hot manga: {e}")
            return []

    def fetch_manga_info(self, manga_id):
        url = f'{BASE_URL}/manga/{manga_id}'
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.text
            soup = BeautifulSoup(data, 'html.parser')

            manga_info = {
                'id': manga_id,
                'title': '',
                'altTitles': [],
                'genres': [],
                'image': '',
                'description': '',
                'chapters': []
            }

            # Extract the JSON-LD data from the script tag
            schema_script = soup.select_one('script[type="application/ld+json"]')
            if schema_script:
                schema_data = json.loads(schema_script.string)
                main_entity = schema_data['mainEntity']
                manga_info['title'] = main_entity['name']
                manga_info['altTitles'] = main_entity.get('alternateName', [])
                manga_info['genres'] = main_entity.get('genre', [])

            manga_info['image'] = soup.select_one('img.bottom-5').get('src')
            manga_info['description'] = soup.select_one('.top-5 .Content').text.strip()

            # Extract chapters data from the script tag
            script_tag = soup.find('script', text=lambda x: x and 'vm.Chapters = ' in x)
            if script_tag:
                script_content = script_tag.string
                start_index = script_content.find('vm.Chapters = ') + len('vm.Chapters = ')
                end_index = script_content.find(';', start_index)
                chapters_data = json.loads(script_content[start_index:end_index].strip())

                manga_info['chapters'] = [
                    {
                        'id': f"{manga_id}-chapter-{self.process_chapter_number(chapter['Chapter'])}",
                        'title': chapter.get('ChapterName', f"Chapter {self.process_chapter_number(chapter['Chapter'])}"),
                        'releaseDate': chapter['Date']
                    }
                    for chapter in chapters_data
                ]

            return manga_info
        except requests.RequestException as e:
            print(f"Error fetching manga info: {e}")
            return None

    def fetch_chapter_pages(self, chapter_id):
        url = f'{BASE_URL}/read-online/{chapter_id}-page-1.html'
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.text
            soup = BeautifulSoup(data, 'html.parser')

            # Extract chapter and image path data from the script tag
            script_tag = soup.find('script', text=lambda x: x and 'vm.CurChapter = ' in x)
            if not script_tag:
                print("Chapter script tag not found.")
                return []

            script_content = script_tag.string
            cur_chapter = self.process_script_tag_variable(script_content, 'vm.CurChapter = ')
            image_host = self.process_script_tag_variable(script_content, 'vm.CurPathName = ')
            cur_chapter_length = int(cur_chapter['Page'])

            images = [
                f"https://{image_host}/manga/{chapter_id.split('-chapter-')[0]}/{self.process_chapter_for_image_url(chapter_id)}-{str(i + 1).zfill(3)}.png"
                for i in range(cur_chapter_length)
            ]

            return images
        except requests.RequestException as e:
            print(f"Error fetching chapter pages: {e}")
            return []

    def process_script_tag_variable(self, script, variable):
        start_index = script.find(variable) + len(variable)
        end_index = script.find(';', start_index)
        variable_data = json.loads(script[start_index:end_index].strip())
        return variable_data

    def process_chapter_number(self, chapter):
        decimal = chapter[-1]
        chapter = chapter[1:-1]
        if decimal == '0':
            return chapter
        return f"{chapter}.{decimal}"

    def process_chapter_for_image_url(self, chapter):
        if '.' not in chapter:
            return chapter.zfill(4)
        values = chapter.split('.')
        return f"{values[0].zfill(4)}.{values[1]}"
