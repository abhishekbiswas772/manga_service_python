from flask import Flask, request, jsonify

from AniListManager import fetch_latest_manga_data, fetch_manga_data



app = Flask(__name__)

@app.route('/v1/manga/getPopularManga', methods=['GET'])
def search_in_mangareader():
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


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=80)
