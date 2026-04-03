import re

# Known credible sources
CREDIBLE_SOURCES = [
    "reuters", "bbc", "associated press", "ap news", "the guardian",
    "new york times", "washington post", "npr", "bloomberg", "time",
    "forbes", "cnbc", "cnn", "ndtv", "the hindu", "al jazeera",
    "abc news", "cbs news", "nbc news", "the verge", "techcrunch"
]

# Clickbait / fake news trigger words
FAKE_KEYWORDS = [
    "shocking", "you won't believe", "miracle", "secret", "they don't want you to know",
    "banned", "censored", "100%", "cure", "hoax", "conspiracy", "deep state",
    "exposed", "truth revealed", "mainstream media won't tell", "going viral",
    "what they're hiding", "wake up", "sheeple", "plandemic", "fake pandemic"
]

# Sensational punctuation patterns
SENSATIONAL_PATTERNS = [
    r'!{2,}',        # Multiple exclamation marks
    r'\?{2,}',       # Multiple question marks
    r'[A-Z]{5,}',    # All caps words
]

def analyze_article(article: dict) -> dict:
    title = (article.get("title") or "").lower()
    description = (article.get("description") or "").lower()
    source = (article.get("source") or "").lower()
    content = (article.get("content") or "").lower()
    full_text = f"{title} {description} {content}"

    red_flags = []
    score = 100  # Start with 100 (trustworthy), deduct points

    # ✅ Check 1: Source credibility
    is_credible_source = any(s in source for s in CREDIBLE_SOURCES)
    if is_credible_source:
        score += 20
    else:
        score -= 20
        red_flags.append(f"Unknown or unverified source: '{article.get('source')}'")

    # ✅ Check 2: Fake/clickbait keywords
    found_keywords = [kw for kw in FAKE_KEYWORDS if kw in full_text]
    if found_keywords:
        score -= len(found_keywords) * 15
        red_flags.append(f"Clickbait/fake keywords found: {', '.join(found_keywords)}")

    # ✅ Check 3: Sensational punctuation
    original_title = article.get("title") or ""
    for pattern in SENSATIONAL_PATTERNS:
        if re.search(pattern, original_title):
            score -= 15
            red_flags.append("Sensational punctuation or ALL CAPS in title")
            break

    # ✅ Check 4: Very short content (low effort article)
    if len(content) < 100:
        score -= 20
        red_flags.append("Article content is very short or missing")

    # ✅ Check 5: No description
    if not article.get("description"):
        score -= 10
        red_flags.append("No article description provided")

    # ✅ Check 6: Title too long (often clickbait)
    if len(original_title) > 100:
        score -= 10
        red_flags.append("Title is unusually long (possible clickbait)")

    # Clamp score between 0 and 100
    score = max(0, min(score, 100))

    # Determine verdict
    if score >= 70:
        verdict = "✅ REAL"
    elif score >= 40:
        verdict = "⚠️ SUSPICIOUS"
    else:
        verdict = "❌ FAKE"

    return {
        "article": article,
        "verdict": verdict,
        "confidence": f"{score}%",
        "red_flags": red_flags if red_flags else ["None"]
    }