import requests
from flask import jsonify

def fetch_anime_data(page=1, per_page=10):
    url = "https://graphql.anilist.co/"
    
    query = """
    query ($page: Int, $perPage: Int) {
      Page(page: $page, perPage: $perPage) {
        pageInfo {
          total
          currentPage
          lastPage
          hasNextPage
          perPage
        }
        media(type: ANIME, sort: POPULARITY_DESC, status: RELEASING) {
          id
          title {
            romaji
            english
            native
          }
          popularity
          genres
          averageScore
          status
          startDate {
            year
            month
            day
          }
          endDate {
            year
            month
            day
          }
          chapters
          volumes
          coverImage {
            large
            medium
          }
        }
      }
    }
    """
    
    headers = {
        "Content-Type": "application/json",
    }

    variables = {
        "page": page,
        "perPage": per_page
    }

    payload = {
        "query": query,
        "variables": variables
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return jsonify(data), 200
    else:
        print(f"Request failed with status code {response.status_code}")
        print(response.text)
        return jsonify({"error": "Request failed"}), 400
    

def fetch_latest_manga_data(page=1, per_page=10):
    url = "https://graphql.anilist.co/"
    
    query = """
    query ($page: Int, $perPage: Int) {
      Page(page: $page, perPage: $perPage) {
        pageInfo {
          total
          currentPage
          lastPage
          hasNextPage
          perPage
        }
        media(type: ANIME, sort: START_DATE, status: RELEASING) {
          id
          title {
            romaji
            english
            native
          }
          popularity
          genres
          averageScore
          status
          startDate {
            year
            month
            day
          }
          endDate {
            year
            month
            day
          }
          chapters
          volumes
          coverImage {
            large
            medium
          }
        }
      }
    }
    """
    
    headers = {
        "Content-Type": "application/json",
    }

    variables = {
        "page": page,
        "perPage": per_page
    }

    payload = {
        "query": query,
        "variables": variables
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return jsonify(data), 200
    else:
        print(f"Request failed with status code {response.status_code}")
        print(response.text)
        return jsonify({"error": "Request failed"}), 400
    

