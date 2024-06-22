import json
import requests
import cloudscraper
from bs4 import BeautifulSoup
import re

class Mangasee123:
    def __init__(self):
        self.name = 'MangaSee'
        self.baseUrl = 'https://mangasee123.com'
        self.logo = ('https://scontent.fman4-1.fna.fbcdn.net/v/t1.6435-1/80033336_1830005343810810_419412485691408384_n.png?'
                     'stp=dst-png_p148x148&_nc_cat=104&ccb=1-7&_nc_sid=1eb0c7&_nc_ohc=XpeoABDI-sEAX-5hLFV&_nc_ht=scontent.fman4-1.fna&oh=00_AT9nIRz5vPiNqqzNpSg2bJymX22rZ1JumYTKBqg_cD0Alg&oe=6317290E')
        self.scraper = cloudscraper.create_scraper()

    def fetch_manga_info(self, manga_id):
        manga_info = {
            'id': manga_id,
            'title': '',
        }
        url = f'{self.baseUrl}/manga/{manga_id}'

        try:
            response = self.scraper.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            schema_script = soup.select_one('body > script:nth-child(15)')
            if schema_script and schema_script.string:
                main_entity = json.loads(schema_script.string)['mainEntity']

                manga_info['title'] = main_entity['name']
                manga_info['altTitles'] = main_entity['alternateName']
                manga_info['genres'] = main_entity['genre']

            manga_info['image'] = soup.select_one('img.bottom-5')['src']
            manga_info['headerForImage'] = {'Referer': self.baseUrl}
            manga_info['description'] = soup.select_one('.top-5 .Content').text

            content_script = soup.select_one('body > script:nth-child(16)')
            if content_script and content_script.string:
                chapters_data = self.process_script_tag_variable(content_script.string, 'vm.Chapters = ')

                manga_info['chapters'] = [
                    {
                        'id': f"{manga_id}-chapter-{self.process_chapter_number(chapter['Chapter'])}",
                        'title': chapter['ChapterName'] or f"Chapter {self.process_chapter_number(chapter['Chapter'])}",
                        'releaseDate': chapter['Date'],
                    }
                    for chapter in chapters_data
                ]

            return manga_info
        except Exception as err:
            raise Exception(str(err))

    def fetch_chapter_pages(self, chapter_id):
        images = []
        url = f'{self.baseUrl}/read-online/{chapter_id}-page-1.html'

        try:
            response = self.scraper.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            chapter_script = soup.select_one('body > script:nth-child(19)')
            if chapter_script and chapter_script.string:
                cur_chapter = self.process_script_tag_variable(chapter_script.string, 'vm.CurChapter = ')
                image_host = self.process_script_tag_variable(chapter_script.string, 'vm.CurPathName = ')
                cur_chapter_length = int(cur_chapter['Page'])

                for i in range(cur_chapter_length):
                    chapter = self.process_chapter_for_image_url(re.sub('[^0-9.]', '', chapter_id))
                    page = f"{i + 1:03}"
                    manga_id = chapter_id.split('-chapter-', 1)[0]
                    image_path = f'https://{image_host}/manga/{manga_id}/{chapter}-{page}.png'

                    images.append(image_path)

            pages = [
                {
                    'page': i + 1,
                    'img': image,
                    'headerForImage': {'Referer': self.baseUrl},
                }
                for i, image in enumerate(images)
            ]

            return pages
        except Exception as err:
            raise Exception(str(err))

    def process_script_tag_variable(self, script, variable):
        chop_front = script[script.find(variable) + len(variable):]
        chapters = json.loads(chop_front[:chop_front.find(';')])
        return chapters

    def process_chapter_for_image_url(self, chapter):
        if '.' not in chapter:
            return chapter.zfill(4)
        values = chapter.split('.')
        pad = values[0].zfill(4)
        return f"{pad}.{values[1]}"


    def search(self, query):
        matches = []
        sanitized_query = query.replace(' ', '').lower()

        try:
            response = self.scraper.get(f'{self.baseUrl}/_search.php')
            response.raise_for_status()
            data = response.json()

            for item in data:
                sanitized_alts = [alt.replace(' ', '').lower() for alt in item['a']]
                if (sanitized_query in item['s'].replace(' ', '').lower() or
                        sanitized_query in sanitized_alts):
                    matches.append(item)

            results = [
                {
                    'id': val['i'],
                    'title': val['s'],
                    'altTitles': val['a'],
                    'image': f'https://temp.compsci88.com/cover/{val["i"]}.jpg',
                    'headerForImage': {'Referer': self.baseUrl},
                }
                for val in matches
            ]

            return {'results': results}
        except Exception as err:
            raise Exception(str(err))


    def process_chapter_number(self, chapter):
        decimal = chapter[-1]
        chapter = chapter[1:-1]
        if decimal == '0':
            return str(int(chapter))
        if chapter.startswith('0'):
            chapter = chapter[1:]
        return f"{int(chapter)}.{decimal}"

    def process_chapter_for_image_url(self, chapter):
        if '.' not in chapter:
            return chapter.zfill(4)
        values = chapter.split('.')
        pad = values[0].zfill(4)
        return f"{pad}.{values[1]}"

# Example usage:
manga = Mangasee123()
media_info = manga.search('oyasumi')
manga_info = manga.fetch_manga_info(media_info['results'][0]['id'])
chapter_pages = manga.fetch_chapter_pages(manga_info['chapters'][0]['id'])
print(chapter_pages)
# print(media_info, manga_info)
