import pandas as pd
from datetime import datetime
from news_fetcher import fetch_latest_news
from detector import analyze_article
import difflib

# ─────────────────────────────────────────
# CSV SAVE
# ─────────────────────────────────────────
def save_to_csv(results: list, topic: str):
    rows = []
    for r in results:
        rows.append({
            "Topic": topic,
            "Title": r["article"]["title"],
            "Source": r["article"]["source"],
            "Verdict": r["verdict"],
            "Trust Score": r["confidence"],
            "Red Flags": ', '.join(r["red_flags"]),
            "URL": r["article"]["url"],
            "Checked At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    df = pd.DataFrame(rows)
    filename = f"results_{topic}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False)
    print(f"\n✅ Results saved to: {filename}")


# ─────────────────────────────────────────
# PRINT RESULT
# ─────────────────────────────────────────
def print_result(result, index):
    article = result["article"]
    print("\n" + "=" * 65)
    print(f"📰 [{index}] {article['title']}")
    print(f"🔗 SOURCE     : {article['source']}")
    print(f"🔍 VERDICT    : {result['verdict']}")
    print(f"📊 TRUST SCORE: {result['confidence']}")
    print(f"🚩 RED FLAGS  : {', '.join(result['red_flags'])}")
    print(f"🔗 URL        : {article['url']}")
    print("=" * 65)


# ─────────────────────────────────────────
# MODE 1 — CHECK BY TOPIC
# ─────────────────────────────────────────
def check_by_topic():
    topic = input("\nEnter a news topic (e.g. 'AI', 'elections', 'health'): ")
    count = int(input("How many articles to analyze? (1-100): "))

    print(f"\n🔍 Fetching {count} latest articles about '{topic}'...")
    articles = fetch_latest_news(topic=topic, count=count)

    if not articles:
        print("❌ No articles found. Check your NewsAPI key in .env file.")
        return

    print(f"✅ Found {len(articles)} articles. Analyzing...\n")

    all_results = []
    real_count = suspicious_count = fake_count = 0

    for i, article in enumerate(articles, 1):
        result = analyze_article(article)
        print_result(result, i)
        all_results.append(result)

        if "REAL" in result["verdict"]:
            real_count += 1
        elif "SUSPICIOUS" in result["verdict"]:
            suspicious_count += 1
        else:
            fake_count += 1

    print(f"\n📊 SUMMARY FOR '{topic.upper()}'")
    print(f"  ✅ Real       : {real_count}")
    print(f"  ⚠️  Suspicious  : {suspicious_count}")
    print(f"  ❌ Fake        : {fake_count}")
    print(f"  📰 Total       : {len(articles)}")

    save_to_csv(all_results, topic)


# ─────────────────────────────────────────
# MODE 2 — CHECK BY URL
# ─────────────────────────────────────────
def check_by_url():
    url = input("\nPaste any news article URL: ").strip()

    print(f"\n🔗 Fetching article from URL...")
    try:
        from newspaper import Article, Config
        config = Config()
        config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        art = Article(url, config=config)
        art.download()
        art.parse()

        data = {
            "title": art.title,
            "description": art.meta_description or "",
            "source": art.source_url,
            "content": art.text,
            "url": url
        }

        print("\n" + "=" * 65)
        print(f"📰 TITLE      : {data['title']}")
        result = analyze_article(data)
        print(f"🔗 SOURCE     : {data['source']}")
        print(f"🔍 VERDICT    : {result['verdict']}")
        print(f"📊 TRUST SCORE: {result['confidence']}")
        print(f"🚩 RED FLAGS  : {', '.join(result['red_flags'])}")
        print("=" * 65)

        # Save single URL result to CSV
        save_to_csv([result], "url_check")

    except Exception as e:
        print(f"❌ Could not fetch article: {e}")


# ─────────────────────────────────────────
# MODE 3 — CHECK BY CLAIM
# ─────────────────────────────────────────
def check_by_claim():
    claim = input("\nEnter your news claim: ").strip()

    print(f"\n🔍 Searching NewsAPI for: '{claim}'...")
    articles = fetch_latest_news(topic=claim, count=30)

    print("\n" + "=" * 65)
    print(f"📰 YOUR CLAIM : {claim}")
    print("=" * 65)

    if not articles:
        print("🔍 VERDICT    : ❌ FAKE / UNVERIFIED")
        print("💬 REASON     : No matching news found in any real source.")
        print("=" * 65)
        return

    claim_words = [w.strip("?!.,#") for w in claim.lower().split() if len(w) > 3 or w.isupper()]
    if not claim_words:
        claim_words = claim.lower().split()
        
    scored_articles = []

    for article in articles:
        text_block = (article["title"] or "").lower() + " " + (article["description"] or "").lower() + " " + (article["content"] or "").lower()
        words_list = text_block.split()
        
        match_count = sum(1 for cw in claim_words if difflib.get_close_matches(cw, words_list, n=1, cutoff=0.6))
        score = (match_count / len(claim_words)) * 100 if claim_words else 0
        scored_articles.append((article, score))

    matched = [x for x in scored_articles if x[1] >= 40]
    matched.sort(key=lambda x: x[1], reverse=True)

    if matched:
        best, score = matched[0]
        result = analyze_article(best)
        print(f"🔍 VERDICT    : ✅ REAL — Found in verified news sources!")
        print(f"📊 MATCH SCORE: {score:.0f}%")
        print(f"🔗 SOURCE     : {best['source']}")
        print(f"📰 FOUND AS   : {best['title']}")
        print(f"🔗 URL        : {best['url']}")
        print(f"🚩 RED FLAGS  : {', '.join(result['red_flags'])}")

        if len(matched) > 1:
            print(f"\n📌 Also reported by {len(matched)-1} other source(s):")
            for art, s in matched[1:4]:
                print(f"   • {art['source']} ({s:.0f}% match) — {art['title'][:60]}...")
    else:
        print(f"🔍 VERDICT    : ❌ FAKE / UNVERIFIED")
        print(f"💬 REASON     : Claim not found in any verified news source.")
        print(f"\n📌 Best related matches (Doesn't confirm your claim directly):")
        # Display the highest semantically relevant API results
        for art in articles[:3]:
            match_s = next(s for a, s in scored_articles if a == art)
            print(f"   • {art['source']} ({match_s:.0f}% match) — {art['title'][:60]}...")

    print("=" * 65)


# ─────────────────────────────────────────
# MAIN MENU
# ─────────────────────────────────────────
def main():
    print("\n" + "=" * 65)
    print("       🗞️  FAKE NEWS DETECTOR — Powered by NewsAPI")
    print("=" * 65)

    while True:
        print("\n📌 Choose an option:")
        print("  1️⃣  Search news by TOPIC")
        print("  2️⃣  Check a NEWS URL")
        print("  3️⃣  Verify a news CLAIM")
        print("  4️⃣  Exit")

        choice = input("\nEnter choice (1/2/3/4): ").strip()

        if choice == "1":
            check_by_topic()
        elif choice == "2":
            check_by_url()
        elif choice == "3":
            check_by_claim()
        elif choice == "4":
            print("\n👋 Goodbye!")
            break
        else:
            print("⚠️  Invalid choice. Please enter 1, 2, 3 or 4.")

if __name__ == "__main__":
    main()