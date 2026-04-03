import requests
import os
from dotenv import load_dotenv

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")  # ✅ reads from .env file

def fetch_latest_news(topic="technology", count=5):
    """Fetch real-time news articles from NewsAPI"""
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": topic,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": count,
        "apiKey": NEWS_API_KEY  # ✅ uses the variable
    }
    response = requests.get(url, params=params)
    data = response.json()

    articles = []
    if data.get("status") == "ok":
        for article in data.get("articles", []):
            articles.append({
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "source": article.get("source", {}).get("name", ""),
                "url": article.get("url", ""),
                "content": article.get("content", "")
            })
    return articles