import requests
import os
from dotenv import load_dotenv
from autocorrect import Speller
from duckduckgo_search import DDGS

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

spell = Speller(lang='en')

def fetch_latest_news(topic="technology", count=5):
    """Fetch real-time news articles from NewsAPI and DDGS for massive past & present coverage"""
    corrected_topic = spell(topic)
    res = []
    seen_urls = set()
    
    # ── 1. DUCKDUCKGO SEARCH (For past and present un-capped news) ──
    try:
        ddgs_news = DDGS().news(topic, max_results=count)
        for r in ddgs_news:
            url = r.get("url", "")
            if url and url not in seen_urls:
                res.append({
                    "title": r.get("title", ""),
                    "description": r.get("body", ""),
                    "source": r.get("source", ""),
                    "url": url,
                    "content": r.get("body", "")
                })
                seen_urls.add(url)
    except Exception:
        pass
        
    # ── 2. NEWSAPI (For immediate major publisher news) ──
    try:
        url = "https://newsapi.org/v2/everything"
        # Extract meaningful keywords for strict AND matching
        words = [w for w in corrected_topic.split() if len(w) > 3 or w[0].isupper()]
        if not words: words = corrected_topic.split()
        
        query = " AND ".join(words[:4]) if len(words) > 1 else corrected_topic
        
        params = {
            "q": query,
            "language": "en",
            "sortBy": "relevancy",
            "pageSize": count,
            "apiKey": NEWS_API_KEY
        }
        data = requests.get(url, params=params).json()
        articles = data.get("articles", [])
        
        if not articles and len(words) > 1:
            params["q"] = " OR ".join(words[:2])
            data = requests.get(url, params=params).json()
            articles = data.get("articles", [])
            
        for article in articles:
            a_url = article.get("url", "")
            if a_url and a_url not in seen_urls:
                res.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "source": article.get("source", {}).get("name", ""),
                    "source_id": article.get("source", {}).get("id", ""),
                    "url": a_url,
                    "content": article.get("content", "")
                })
                seen_urls.add(a_url)
    except Exception:
        pass
        
    return res