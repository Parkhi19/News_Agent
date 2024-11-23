from fastapi import HTTPException
import os
import http.client
from datetime import datetime, timedelta
import urllib.parse
import json
from NewsArticle import NewsArticle


def fetch_top_news():
    API_URL = os.getenv("MEDIASTACK_API_URL")
    API_KEY = os.getenv("MEDIASTACK_API_KEY")

    if not API_URL or not API_KEY:
        raise HTTPException(status_code=500, detail="API URL or API Key not set in environment variables")

    api_connection = http.client.HTTPSConnection(API_URL)

    now = datetime.utcnow().date()
    yesterday = (datetime.utcnow() - timedelta(days=1)).date()

    params = urllib.parse.urlencode({
        "access_key": API_KEY,
        "categories": "general",
        "sort": "published_desc",
        "limit": 5,
        "languages": "en",
        "date": f"{yesterday},{now}",
    })

    api_connection.request("GET", f"/v1/news?{params}")
    response = api_connection.getresponse()
    if response.status != 200:
        raise HTTPException(status_code=response.status, detail="Failed to fetch news from MediaStack API")

    data = response.read()
    json_data = json.loads(data.decode("utf-8"))

    filtered_news = []
    for article in json_data.get("data", []):
        news_article = NewsArticle(
            title=article.get("title", "No Title"),
            description=article.get("description", "No Description"),
            url=article.get("url", "No URL")
        )
        filtered_news.append(news_article)

    return filtered_news