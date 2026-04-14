import re

# ─────────────────────────────────────────
# CREDIBLE SOURCES (expanded)
# ─────────────────────────────────────────
CREDIBLE_SOURCES = [
    # International
    "reuters", "bbc", "associated press", "ap news", "bloomberg",
    "the guardian", "new york times", "washington post", "npr",
    "forbes", "cnbc", "cnn", "time", "al jazeera", "abc news",
    "cbs news", "nbc news", "the verge", "techcrunch", "wired",
    "the economist", "financial times", "wall street journal",
    "wsj", "sky news", "independent", "telegraph", "usa today",

    # Indian sources
    "ndtv", "the hindu", "hindustan times", "times of india",
    "indian express", "india today", "the wire", "scroll",
    "the print", "livemint", "business standard", "firstpost",
    "deccan herald", "tribune", "news18", "zee news",
    "economic times", "moneycontrol", "ani", "pti"
]

# ─────────────────────────────────────────
# FAKE / CLICKBAIT KEYWORDS
# ─────────────────────────────────────────
FAKE_KEYWORDS = [
    # Sensational claims
    "you won't believe", "shocking truth", "they don't want you to know",
    "what they're hiding", "mainstream media won't tell", "wake up",
    "truth revealed", "exposed", "going viral", "share before deleted",
    "banned video", "censored", "deep state", "conspiracy", "hoax",
    "plandemic", "fake pandemic", "sheeple", "new world order",

    # Medical misinformation
    "miracle cure", "doctors hate", "big pharma hiding", "100% cure",
    "instant cure", "secret remedy", "government hiding cure",

    # Clickbait patterns
    "click here", "you must see", "what happened next",
    "this will shock you", "number will shock", "nobody is talking about",

    # Emotional manipulation
    "urgent", "breaking alert", "act now", "limited time",
    "before it's too late", "they are coming for"
]

# ─────────────────────────────────────────
# SATIRE / PARODY DOMAINS
# ─────────────────────────────────────────
SATIRE_SOURCES = [
    "theonion", "babylonbee", "newsthump", "thespoof",
    "waterfordwhispersnews", "duffelblog"
]

# ─────────────────────────────────────────
# MAIN ANALYZER
# ─────────────────────────────────────────
def analyze_article(article: dict) -> dict:
    title       = (article.get("title") or "").strip()
    description = (article.get("description") or "").strip()
    source      = (article.get("source") or "").lower().strip()
    source_id   = article.get("source_id")
    content     = (article.get("content") or "").strip()
    url         = (article.get("url") or "").lower()

    title_lower = title.lower()
    desc_lower  = description.lower()
    full_text   = f"{title_lower} {desc_lower} {content.lower()}"

    red_flags = []
    score = 50  # Start neutral

    # ── CHECK 1: Source credibility (most important) ──
    is_credible = any(s in source for s in CREDIBLE_SOURCES)
    is_satire   = any(s in source for s in SATIRE_SOURCES)
    is_credible_url = any(s in url for s in CREDIBLE_SOURCES)

    if is_satire:
        score -= 40
        red_flags.append("Satire or parody source")
    elif is_credible or is_credible_url:
        score += 35
    elif source_id:
        score += 25
        # Do not append red flag, NewsAPI explicitly verifies their Top global sources via IDs
    else:
        looks_like_news = any(w in source for w in ["news", "times", "post", "daily", "journal", "gazette", "chronicle", "tribune", "wire", "herald", "today"])
        if looks_like_news:
            score += 15
            red_flags.append(f"Unlisted generic news source: '{article.get('source')}'")
        else:
            score -= 5
            if source:
                red_flags.append(f"Unrecognized source: '{article.get('source')}'")
            else:
                score -= 10
                red_flags.append("No source provided")

    # ── CHECK 2: Clickbait / fake keywords ──..
    
    found_keywords = [kw for kw in FAKE_KEYWORDS if kw in full_text]
    if found_keywords:
        deduction = min(len(found_keywords) * 12, 40)
        score -= deduction
        red_flags.append(f"Suspicious keywords: {', '.join(found_keywords[:3])}")

    # ── CHECK 3: ALL CAPS words in title ──
    caps_words = re.findall(r'\b[A-Z]{4,}\b', title)
    caps_words = [w for w in caps_words if w not in
                  ["NASA", "FIFA", "NATO", "ISRO", "DRDO", "WHO", "UN",
                   "USA", "UK", "UPI", "GDP", "RBI", "BJP", "INC", "PM",
                   "CM", "AI", "IT", "TV", "IPL", "ICC", "BCCI"]]
    if len(caps_words) >= 2:
        score -= 12
        red_flags.append(f"Excessive CAPS in title: {', '.join(caps_words[:3])}")

    # ── CHECK 4: Excessive punctuation ──
    if re.search(r'!{2,}', title) or re.search(r'\?{2,}', title):
        score -= 10
        red_flags.append("Excessive punctuation in title (!!! or ???)")

    # ── CHECK 5: Content length check ──
    word_count = len(content.split())
    is_truncated = "[+" in content

    if word_count == 0:
        score -= 20
        red_flags.append("No article content available")
    elif word_count < 30 and not is_truncated:
        score -= 12
        red_flags.append("Very short article content")
    elif word_count > 150:
        score += 10  # Longer articles = more legit
    elif is_truncated:
        score += 5  # NewsAPI provides truncated valid content

    # ── CHECK 6: No description ──
    if not description:
        score -= 8
        red_flags.append("No article description")

    # ── CHECK 7: Title too long (clickbait) ──
    if len(title) > 120:
        score -= 8
        red_flags.append("Unusually long title")

    # ── CHECK 8: URL quality ──
    suspicious_url_patterns = [
        r'\d{5,}',           # Lots of numbers in URL
        r'(free|win|prize)', # Scammy URL words
        r'\.(tk|ml|ga|cf|gq|xyz|biz|info)(/|$)',  # Cheap/spam TLDs
        r'(blogspot\.com|wordpress\.com|wixsite\.com|weebly\.com)' # Free subdomains
    ]
    for pattern in suspicious_url_patterns:
        if re.search(pattern, url):
            score -= 12
            red_flags.append("Suspicious URL pattern (spam domain or free host)")
            break

    # ── CHECK 9: Title ends with clickbait question ──
    clickbait_endings = [
        "?", "you need to know", "here's why", "this is why",
        "find out", "the truth", "what really happened"
    ]
    if any(title_lower.endswith(e) for e in clickbait_endings):
        if not is_credible:
            score -= 8
            red_flags.append("Clickbait-style title ending")

    # ── CHECK 10: Multiple exclamation in description ──
    if description.count('!') >= 3:
        score -= 8
        red_flags.append("Emotionally charged description")

    # ── Clamp score 0–100 ──
    score = max(0, min(score, 100))

    # ── Verdict ──
    if score >= 65:
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