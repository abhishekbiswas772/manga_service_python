from flask import Flask, request, jsonify
from AniListManager import fetch_latest_manga_data, fetch_manga_data
from MangaSeeClient import Mangasee123
from deep_translator import GoogleTranslator

app = Flask(__name__)
manga_parser = Mangasee123()

@app.route('/v1/manga/getPopularManga', methods=['GET'])
def get_popular_manga():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    result = fetch_manga_data(page, per_page)
    return result



@app.route('/v1/manga/getLatestManga', methods=['GET'])
def get_latest_manga():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    result = fetch_latest_manga_data(page, per_page)
    return result


@app.route('/manga/mangasee123/info', methods=['GET'])
def get_manga_info():
    manga_id = request.args.get('id')
    if not manga_id:
        return jsonify({'error': 'ID parameter is required'}), 400
    try:
        manga_info = manga_parser.fetch_manga_info(manga_id)
        return jsonify(manga_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/manga/mangasee123/read/<chapter_id>', methods=['GET'])
def get_chapter_pages(chapter_id):
    try:
        chapter_pages = manga_parser.fetch_chapter_pages(chapter_id)
        return jsonify(chapter_pages)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/manga/mangasee123/<query>', methods=['GET'])
def search_manga(query):
    try:
        search_results = manga_parser.search(query)
        return jsonify(search_results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/translate', methods=['POST'])
def translate_text():
    data = request.json
    text = data.get('text')
    target_language = data.get('target_language', 'en')

    if not text:
        return jsonify({"error": "Text to translate is required"}), 400

    try:
        translator = GoogleTranslator(source='auto', target=target_language)
        translation = translator.translate(text)
        return jsonify({
            "original_text": text,
            "translated_text": translation,
            "target_language": target_language
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/v1/anime/getPopularAnime', methods=['GET'])
def get_popular_anime():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    result = fetch_manga_data(page, per_page)
    return result



@app.route('/v1/anime/getLatestAnime', methods=['GET'])
def get_latest_anime():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    result = fetch_latest_manga_data(page, per_page)
    return result
            
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=80)
