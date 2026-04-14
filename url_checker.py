from newspaper import Article
from detector import analyze_article

def check_url(url: str):
    print(f"\n🔗 Fetching article from URL...")
    try:
        article = Article(url)
        article.download()
        article.parse()

        data = {
            "title": article.title,
            "description": article.meta_description or "",
            "source": article.source_url,
            "content": article.text,
            "url": url
        }

        print(f"📰 TITLE  : {data['title']}")
        result = analyze_article(data)
        print(f"🔍 VERDICT: {result['verdict']}")
        print(f"📊 SCORE  : {result['confidence']}")
        print(f"🚩 FLAGS  : {', '.join(result['red_flags'])}")

    except Exception as e:
        print(f"❌ Could not fetch article: {e}")

if __name__ == "__main__":
    url = input("Paste any news article URL: ").strip()
    check_url(url)