import random
import requests
import json

from flask import Flask, request, jsonify
from flask_cors import CORS
from googleapiclient.discovery import build

import base64
from requests import post, get

app = Flask(__name__)
CORS(app)

YOUTUBE_API_KEY = 'AIzaSyCw70b8J5ytEi0RUXi0Byxipt2peQbUwFI'
GOOGLE_SEARCH_ENGINE_ID = "95b4f0461be9e4731"   # Wu Hongchuan
GOOGLE_API_KEY = "AIzaSyBqRnuNHWAUKHCe2uLcdNkopIjIoc7Er5I"   # Wu Hongchuan
# GOOGLE_SEARCH_ENGINE_ID = 'c7dcb66945bd746c4'   # Jiang Jintian
# GOOGLE_API_KEY = 'AIzaSyDuytXx3Jj6PceDb-bDKWGJIMv54lxWwyo'   # Jiang Jintian

youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

client_id = "b0f0ad81e61b4faab57cecd13ea40b04" # HE longyan
client_secret = "1a33231e84354e098a52962d81999c9c" # HE longyan

def get_token():
    auth_string = client_id + ":" + client_secret
    autu_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(autu_bytes), "utf-8")
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    print(result)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

@app.route('/chatbot-api/album', methods=['GET'])
def get_album():
    keywords = request.args.get('keywords')
    print('keywords', keywords)
    token = get_token()
    if keywords: # 根据关键词搜索唱片
        try:
            url = "https://api.spotify.com/v1/search"
            headers = get_auth_header(token)
            query = f"?q={keywords}&type=album&limit=1"
            query_url = url + query
            result = get(query_url, headers=headers)
            print('result', result)
            json_result = json.loads(result.content)["albums"]["items"]
            response = {
                'message': 'OK',
                'data': json_result[0]["external_urls"]["spotify"]
            }
            return jsonify(response), 200
        except ConnectionError:
            response = { 'message': 'Connection Failed' }
            return jsonify(response), 500
    else:
        response = { 'message': 'No result!' }
        return jsonify(response), 400


@app.route('/chatbot-api/artist', methods=['GET'])
def get_artist():
    keywords = request.args.get('keywords')
    print('keywords',keywords)
    token = get_token()
    if keywords: # 根据关键词搜索唱片
        try:
            url = "https://api.spotify.com/v1/search"
            headers = get_auth_header(token)
            query = f"?q={keywords}&type=artist&limit=1"
            query_url = url + query
            result = get(query_url, headers=headers)
            json_result = json.loads(result.content)["artists"]["items"]
            response = {
                'message': 'OK',
                'data': json_result[0]["external_urls"]["spotify"]
            }
            return jsonify(response), 200
        except ConnectionError:
            response = { 'message': 'Connection Failed' }
            return jsonify(response), 500
    else:
        response = { 'message': 'No result!' }
        return jsonify(response), 400


# get youtube video
@app.route('/chatbot-api/youtube', methods=['GET'])
def get_youtube_videos():
    keywords = request.args.get('keywords')
    print('keywords',keywords)
    if keywords: # 根据关键词搜索 YouTube 视频
        try:
            global youtube
            req = youtube.search().list(
                part="id, snippet",
                q=keywords,
                type="video",
                maxResults=50,
            )
            res = req.execute()

            random_video = random.choice(res["items"])
            video_id = random_video['id']['videoId']

            response = {
                'message': 'OK',
                'data': video_id
            }
            return jsonify(response), 200
        except ConnectionError:
            response = { 'message': 'Connection Failed' }
            return jsonify(response), 500
    else: # 没有关键词则列出3条热门的视频
        try:
            req = youtube.videos().list(
                part="snippet,contentDetails,statistics",
                chart="mostPopular",
                maxResults=100
            )
            res = req.execute()
            videos = []
            # handle res
            for item in random.sample(res.get("items", []), 3):
                title = item["snippet"]["title"]
                url = f"https://www.youtube.com/watch?v={item['id']}"
                like_count = item["statistics"]["likeCount"]
                video_info = f"{title}\n{url}\n👍{like_count}"
                videos.append(video_info)
            
            response = {
                'message': 'OK',
                'data': videos
            }
            return jsonify(response), 200
        except ConnectionError:
            response = { 'message': 'Connection Failed' }
            return jsonify(response), 500


@app.route('/chatbot-api/img', methods=['GET'])
def get_google_imgs():
    keywords = request.args.get('keywords')
    print('keywords',keywords)
    if not keywords:
        response = { 'message': 'Invalid format' }
        return jsonify(response), 400

    try:
        # Get the search term from the message text
        search_term = ''.join(keywords)
        # Define the search URL with the search term, API key, and search engine ID
        search_url = "https://www.googleapis.com/customsearch/v1"
        # Send the search request to the API and get the JSON response
        params = {
            'q': search_term,
            'cx': GOOGLE_SEARCH_ENGINE_ID,
            'searchType': 'image',
            'key': GOOGLE_API_KEY
        }
        res = requests.get(search_url, params=params).json()
        print(res)
        if 'items' in res and len(res['items']) > 0:
            # Get the URL of the first image in the response
            image_url = res['items'][0]['link']
            response = {
                'message': 'OK',
                'data': image_url
            }
            return jsonify(response), 200
        else:
            print('Sorry')
            response = { 'message': 'Sorry, I could not find any images for the requested search term.' }
            return jsonify(response), 500
    except:
        response = { 'message': 'Something went wrong.' }
        return jsonify(response), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
