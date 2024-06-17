from flask import Flask, request, jsonify
from mangakalakot import MangaKakalotAPI
from mangapark import MangaParkAPI
from mangapill import MangaPillAPI
from mangareader import MangaReaderAPI
from mangasee import MangaSeeAPI


app = Flask(__name__)

api_mangasee = MangaSeeAPI()
api_mangareader = MangaReaderAPI()
api_mangakalakot = MangaKakalotAPI()
api_mangapark = MangaParkAPI()
api_mangapill = MangaPillAPI()

# mangasee
@app.route('/v1/mangasee/search', methods=['GET'])
def search_in_mangasee():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400
    results = api_mangasee.search_manga(query)
    return jsonify(results)

@app.route('/v1/mangasee/hot', methods=['GET'])
def hot_manga_in_mangasee():
    results = api_mangasee.get_hot_manga()
    return jsonify(results)

@app.route('/v1/mangasee/manga/<manga_id>', methods=['GET'])
def manga_info_in_mangasee(manga_id):
    result = api_mangasee.fetch_manga_info(manga_id)
    if not result:
        return jsonify({'error': 'Manga not found'}), 404
    return jsonify(result)

@app.route('/v1/mangasee/chapter/<chapter_id>', methods=['GET'])
def chapter_pages_in_mangasee(chapter_id):
    results = api_mangasee.fetch_chapter_pages(chapter_id)
    if not results:
        return jsonify({'error': 'Chapter not found'}), 404
    return jsonify(results)


# mangareader
@app.route('/v1/mangareader/search', methods=['GET'])
def search_in_mangareader():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400
    results = api_mangareader.search_manga(query)
    return jsonify(results)

@app.route('/v1/mangareader/manga/<manga_id>', methods=['GET'])
def manga_info_in_mangareader(manga_id):
    result = api_mangareader.fetch_manga_info(manga_id)
    if not result:
        return jsonify({'error': 'Manga not found'}), 404
    return jsonify(result)

@app.route('/v1/mangareader/chapter/<chapter_id>', methods=['GET'])
def chapter_pages_in_mangareader(chapter_id):
    results = api_mangareader.fetch_chapter_pages(chapter_id)
    if not results:
        return jsonify({'error': 'Chapter not found'}), 404
    return jsonify(results)

@app.route('/v1/mangareader/hot', methods=['GET'])
def hot_manga_in_mangareader():
    results = api_mangareader.get_hot_manga()
    return jsonify(results)


#mangakalakot
@app.route('/v1/mangakalakot/search', methods=['GET'])
def search_manga_in_mangakalakot():
    query = request.args.get('query', '')
    results = api_mangakalakot.search_manga(query)
    return jsonify(results)

@app.route('/v1/mangakalakot/info', methods=['GET'])
def fetch_manga_info_in_mangakalakot():
    manga_id = request.args.get('manga_id', '')
    results = api_mangakalakot.fetch_manga_info(manga_id)
    return jsonify(results)

@app.route('/v1/mangakalakot/chapters', methods=['GET'])
def fetch_chapter_pages_in_mangakalakot():
    chapter_id = request.args.get('chapter_id', '')
    results = api_mangakalakot.fetch_chapter_pages(chapter_id)
    return jsonify(results)

@app.route('/v1/mangakalakot/hot', methods=['GET'])
def get_hot_manga_in_mangakalakot():
    page = request.args.get('page', default=1, type=int)
    results = api_mangakalakot.fetch_hot_manga(page)
    return jsonify(results)


#mangapark
@app.route('/v1/mangapark/search', methods=['GET'])
def search_manga_in_mangapark():
    query = request.args.get('query')
    page = request.args.get('page', default=1, type=int)
    results = api_mangapark.search(query, page)
    return jsonify(results)

@app.route('/v1/mangapark/manga/<manga_id>', methods=['GET'])
def get_manga_info_in_mangapark(manga_id):
    manga_info = api_mangapark.fetch_manga_info(manga_id)
    if manga_info:
        return jsonify(manga_info)
    else:
        return jsonify({'error': 'Manga not found'}), 404

@app.route('/v1/mangapark/chapter/<chapter_id>', methods=['GET'])
def get_chapter_pages_in_mangapark(chapter_id):
    pages = api_mangapark.fetch_chapter_pages(chapter_id)
    return jsonify(pages)


#mangapill
@app.route('/v1/mangapill/search', methods=['GET'])
def search_manga_in_mangapill():
    query = request.args.get('query')
    results = api_mangapill.search(query)
    return jsonify(results)

@app.route('/v1/mangapill/manga/<manga_id>', methods=['GET'])
def get_manga_info_in_mangapill(manga_id):
    manga_info = api_mangapill.fetch_manga_info(manga_id)
    if manga_info:
        return jsonify(manga_info)
    else:
        return jsonify({'error': 'Manga not found'}), 404

@app.route('/v1/mangapill/chapter/<chapter_id>', methods=['GET'])
def get_chapter_pages_in_mangapill(chapter_id):
    pages = api_mangapill.fetch_chapter_pages(chapter_id)
    return jsonify(pages)

@app.route('/v1/mangapill/hot', methods=['GET'])
def get_recently_added_mangas_in_mangapill():
    recently_added = api_mangapill.fetch_recently_added_mangas()
    return jsonify(recently_added)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=80)
