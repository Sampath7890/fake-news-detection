import streamlit as st
import pandas as pd
from datetime import datetime
from news_fetcher import fetch_latest_news
from detector import analyze_article
import difflib

# ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TruthLens — Fake News Detector",
    page_icon="🔎",
    layout="wide"
)

# ─────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0a0f;
    color: #e8e8f0;
}

.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 50%, #0a0f1a 100%);
    min-height: 100vh;
}

/* ── Hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem 3rem; max-width: 1100px; }

/* ── Hero Section ── */
.hero {
    text-align: center;
    padding: 3.5rem 2rem 2rem 2rem;
    margin-bottom: 2rem;
}
.hero-badge {
    display: inline-block;
    background: rgba(99, 179, 237, 0.1);
    border: 1px solid rgba(99, 179, 237, 0.3);
    color: #63b3ed;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 0.4rem 1rem;
    border-radius: 50px;
    margin-bottom: 1.5rem;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 3.8rem;
    font-weight: 800;
    line-height: 1.1;
    background: linear-gradient(135deg, #ffffff 0%, #63b3ed 50%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 1rem;
}
.hero-sub {
    font-size: 1.1rem;
    color: #6b7280;
    font-weight: 300;
    max-width: 480px;
    margin: 0 auto;
    line-height: 1.7;
}

/* ── Tab Styling ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03);
    border-radius: 16px;
    padding: 6px;
    border: 1px solid rgba(255,255,255,0.06);
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 12px;
    padding: 0.6rem 1.5rem;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 0.9rem;
    color: #6b7280;
    border: none;
    transition: all 0.2s ease;
}
.stTabs [aria-selected="true"] {
    background: rgba(99, 179, 237, 0.15) !important;
    color: #63b3ed !important;
    border: 1px solid rgba(99, 179, 237, 0.3) !important;
}
.stTabs [data-baseweb="tab-border"] { display: none; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem; }

/* ── Input Fields ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    color: #e8e8f0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s ease !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: rgba(99, 179, 237, 0.5) !important;
    box-shadow: 0 0 0 3px rgba(99, 179, 237, 0.08) !important;
}
.stTextInput label, .stTextArea label, .stSlider label {
    color: #9ca3af !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}

/* ── Slider ── */
.stSlider > div > div > div > div {
    background: #63b3ed !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.65rem 2rem !important;
    letter-spacing: 0.02em;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 25px rgba(99, 102, 241, 0.45) !important;
}

/* ── Download Button ── */
.stDownloadButton > button {
    background: rgba(255,255,255,0.05) !important;
    color: #9ca3af !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 1.2rem !important;
}
.stDownloadButton > button:hover {
    background: rgba(255,255,255,0.08) !important;
    color: #e8e8f0 !important;
}

/* ── Cards ── */
.card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s ease;
}
.card:hover { border-color: rgba(255,255,255,0.14); }
.card-real    { border-left: 3px solid #34d399; }
.card-fake    { border-left: 3px solid #f87171; }
.card-suspicious { border-left: 3px solid #fbbf24; }

.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: #e8e8f0;
    margin-bottom: 0.75rem;
    line-height: 1.4;
}
.card-meta {
    font-size: 0.82rem;
    color: #6b7280;
    margin-bottom: 0.5rem;
}

/* ── Verdict Pills ── */
.pill {
    display: inline-block;
    padding: 0.3rem 0.9rem;
    border-radius: 50px;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.pill-real    { background: rgba(52, 211, 153, 0.15); color: #34d399; border: 1px solid rgba(52,211,153,0.3); }
.pill-fake    { background: rgba(248, 113, 113, 0.15); color: #f87171; border: 1px solid rgba(248,113,113,0.3); }
.pill-suspicious { background: rgba(251,191,36,0.15); color: #fbbf24; border: 1px solid rgba(251,191,36,0.3); }

/* ── Stat Box ── */
.stat-row {
    display: flex;
    gap: 1rem;
    margin: 1.5rem 0;
}
.stat-box {
    flex: 1;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.2rem;
    text-align: center;
}
.stat-number {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 0.3rem;
}
.stat-label {
    font-size: 0.78rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 500;
}

/* ── Trust Score Bar ── */
.trust-bar-wrap {
    background: rgba(255,255,255,0.06);
    border-radius: 50px;
    height: 6px;
    width: 100%;
    margin-top: 0.4rem;
}
.trust-bar-fill {
    height: 6px;
    border-radius: 50px;
    transition: width 0.6s ease;
}

/* ── Red Flags ── */
.flag-tag {
    display: inline-block;
    background: rgba(248,113,113,0.1);
    color: #f87171;
    border: 1px solid rgba(248,113,113,0.2);
    border-radius: 6px;
    font-size: 0.75rem;
    padding: 0.2rem 0.6rem;
    margin: 0.15rem;
}
.flag-none {
    display: inline-block;
    background: rgba(52,211,153,0.1);
    color: #34d399;
    border: 1px solid rgba(52,211,153,0.2);
    border-radius: 6px;
    font-size: 0.75rem;
    padding: 0.2rem 0.6rem;
}

/* ── Divider ── */
.custom-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin: 2rem 0;
}

/* ── Section Label ── */
.section-label {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #6b7280;
    margin-bottom: 1rem;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #e8e8f0 !important;
}
.streamlit-expanderContent {
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-top: none !important;
    border-radius: 0 0 12px 12px !important;
    background: rgba(255,255,255,0.02) !important;
}

/* ── Alerts ── */
.stSuccess, .stError, .stWarning, .stInfo {
    border-radius: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1rem;
}
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.8rem !important;
    color: #e8e8f0 !important;
}
[data-testid="stMetricLabel"] {
    color: #6b7280 !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: #63b3ed !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def get_pill(verdict):
    if "REAL" in verdict:
        return '<span class="pill pill-real">✓ Real</span>'
    elif "SUSPICIOUS" in verdict:
        return '<span class="pill pill-suspicious">⚠ Suspicious</span>'
    else:
        return '<span class="pill pill-fake">✕ Fake</span>'

def get_card_class(verdict):
    if "REAL" in verdict: return "card card-real"
    if "SUSPICIOUS" in verdict: return "card card-suspicious"
    return "card card-fake"

def get_bar_color(score_str):
    try:
        score = int(score_str.replace("%", ""))
        if score >= 70: return "#34d399", score
        if score >= 40: return "#fbbf24", score
        return "#f87171", score
    except:
        return "#6b7280", 50

def render_flags(flags):
    if flags == ["None"] or not flags:
        return '<span class="flag-none">✓ No red flags</span>'
    return " ".join([f'<span class="flag-tag">⚑ {f}</span>' for f in flags])

def save_csv(results, topic):
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
    return pd.DataFrame(rows).to_csv(index=False).encode("utf-8")

def render_article_card(result, index):
    article = result["article"]
    verdict = result["verdict"]
    bar_color, bar_width = get_bar_color(result["confidence"])
    card_class = get_card_class(verdict)
    pill = get_pill(verdict)
    flags_html = render_flags(result["red_flags"])

    st.markdown(f"""
    <div class="{card_class}">
        <div class="card-meta">#{index} &nbsp;·&nbsp; {article['source']}</div>
        <div class="card-title">{article['title']}</div>
        <div style="display:flex; align-items:center; gap:1rem; margin-bottom:0.75rem;">
            {pill}
            <span style="font-size:0.82rem; color:#9ca3af;">Trust: {result['confidence']}</span>
        </div>
        <div class="trust-bar-wrap">
            <div class="trust-bar-fill" style="width:{bar_width}%; background:{bar_color};"></div>
        </div>
        <div style="margin-top:0.75rem;">{flags_html}</div>
        <div style="margin-top:0.75rem;">
            <a href="{article['url']}" target="_blank"
               style="font-size:0.8rem; color:#63b3ed; text-decoration:none;">
               ↗ Read original article
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# HERO
# ─────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">TruthLens</div>
    <div class="hero-sub">
        Detect fake news instantly. Search by topic, paste a URL,
        or verify any claim — in seconds.
    </div>
</div>
""", unsafe_allow_html=True)
# ─────────────────────────────────────────
# TABS
# ─────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "🔍  Search by Topic",
    "🔗  Check a URL",
    "📝  Verify a Claim"
])


# ══════════════════════════════════════════
# TAB 1 — TOPIC
# ══════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-label">Search & Analyze</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns([3, 1])
    with col_a:
        topic = st.text_input("Topic", placeholder="e.g.  AI · elections · climate · health",
                               label_visibility="collapsed")
    with col_b:
        count = st.slider("Articles", 1, 100, 20, label_visibility="collapsed")
        st.caption(f"Fetching **{count}** articles")

    if st.button("🔍  Analyze Topic", key="topic_btn", use_container_width=True):
        if not topic.strip():
            st.warning("Please enter a topic to search.")
        else:
            with st.spinner(f"Fetching {count} articles about **{topic}**…"):
                articles = fetch_latest_news(topic=topic, count=count)

            if not articles:
                st.error("No articles found. Please check your NewsAPI key in `.env`.")
            else:
                all_results = []
                real = suspicious = fake = 0

                for i, article in enumerate(articles, 1):
                    result = analyze_article(article)
                    all_results.append(result)
                    if "REAL" in result["verdict"]: real += 1
                    elif "SUSPICIOUS" in result["verdict"]: suspicious += 1
                    else: fake += 1

                # Summary stats
                st.markdown(f"""
                <div class="stat-row">
                    <div class="stat-box">
                        <div class="stat-number" style="color:#34d399;">{real}</div>
                        <div class="stat-label">Real</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" style="color:#fbbf24;">{suspicious}</div>
                        <div class="stat-label">Suspicious</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" style="color:#f87171;">{fake}</div>
                        <div class="stat-label">Fake</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" style="color:#63b3ed;">{len(all_results)}</div>
                        <div class="stat-label">Total</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
                st.markdown('<div class="section-label">Results</div>', unsafe_allow_html=True)

                for i, result in enumerate(all_results, 1):
                    render_article_card(result, i)

                # CSV download
                csv = save_csv(all_results, topic)
                st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
                st.download_button(
                    "💾  Download Results as CSV",
                    data=csv,
                    file_name=f"truthlens_{topic}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )


# ══════════════════════════════════════════
# TAB 2 — URL
# ══════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-label">Paste Any Article URL</div>', unsafe_allow_html=True)
    url = st.text_input("URL", placeholder="https://www.bbc.com/news/...",
                         label_visibility="collapsed")

    if st.button("🔗  Analyze URL", key="url_btn", use_container_width=True):
        if not url.strip().startswith("http"):
            st.warning("Please paste a valid URL starting with `https://`")
        else:
            with st.spinner("Fetching and analyzing article…"):
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

                    result = analyze_article(data)
                    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
                    render_article_card(result, 1)

                    csv = save_csv([result], "url_check")
                    st.download_button(
                        "💾  Download Result as CSV",
                        data=csv,
                        file_name=f"truthlens_url_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Could not fetch article: `{e}`")


# ══════════════════════════════════════════
# TAB 3 — CLAIM
# ══════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-label">Verify Any News Claim</div>', unsafe_allow_html=True)
    claim = st.text_input("Claim", placeholder="e.g.  Rashmika and Vijay got married",
                           label_visibility="collapsed")

    if st.button("📝  Verify Claim", key="claim_btn", use_container_width=True):
        if not claim.strip():
            st.warning("Please enter a news claim to verify.")
        else:
            # ✅ CORRECT — use single quotes inside f-string
            with st.spinner(f"Searching verified sources for '{claim}'…"):
                articles = fetch_latest_news(topic=claim, count=30)

            st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
            st.markdown(f"""
            <div style="font-size:0.82rem; color:#6b7280; margin-bottom:0.5rem;">
                YOUR CLAIM
            </div>
            <div style="font-family:'Syne',sans-serif; font-size:1.3rem;
                        font-weight:700; color:#e8e8f0; margin-bottom:1.5rem;">
                "{claim}"
            </div>
            """, unsafe_allow_html=True)

            if not articles:
                st.markdown(f"""
                <div class="card card-fake">
                    <span class="pill pill-fake">✕ Fake / Unverified</span>
                    <p style="color:#9ca3af; margin-top:0.75rem; font-size:0.9rem;">
                        No matching articles found in any verified news source.
                        This claim does not appear in real news databases.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
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
                    bar_color, bar_width = get_bar_color(result["confidence"])
                    flags_html = render_flags(result["red_flags"])

                    st.markdown(f"""
                    <div class="card card-real">
                        <span class="pill pill-real">✓ Real — Found in verified sources</span>
                        <div style="margin-top:1rem; display:flex; gap:2rem;">
                            <div>
                                <div style="font-size:0.75rem;color:#6b7280;
                                            text-transform:uppercase;letter-spacing:0.08em;">
                                    Match Score
                                </div>
                                <div style="font-family:'Syne',sans-serif;
                                            font-size:1.6rem;font-weight:800;color:#34d399;">
                                    {score:.0f}%
                                </div>
                            </div>
                            <div>
                                <div style="font-size:0.75rem;color:#6b7280;
                                            text-transform:uppercase;letter-spacing:0.08em;">
                                    Trust Score
                                </div>
                                <div style="font-family:'Syne',sans-serif;
                                            font-size:1.6rem;font-weight:800;color:#63b3ed;">
                                    {result['confidence']}
                                </div>
                            </div>
                        </div>
                        <div style="margin-top:0.75rem;">
                            <div class="card-meta">Source: {best['source']}</div>
                            <div class="card-title">{best['title']}</div>
                        </div>
                        <div class="trust-bar-wrap">
                            <div class="trust-bar-fill"
                                 style="width:{bar_width}%;background:{bar_color};"></div>
                        </div>
                        <div style="margin-top:0.75rem;">{flags_html}</div>
                        <a href="{best['url']}" target="_blank"
                           style="font-size:0.8rem;color:#63b3ed;
                                  text-decoration:none;margin-top:0.5rem;display:inline-block;">
                            ↗ Read original article
                        </a>
                    </div>
                    """, unsafe_allow_html=True)

                    if len(matched) > 1:
                        st.markdown('<div class="section-label" style="margin-top:1.5rem;">Also Reported By</div>',
                                    unsafe_allow_html=True)
                        for art, s in matched[1:4]:
                            st.markdown(f"""
                            <div class="card" style="padding:1rem 1.2rem;">
                                <div class="card-meta">{art['source']} · {s:.0f}% match</div>
                                <div style="font-size:0.9rem;color:#e8e8f0;">{art['title'][:80]}…</div>
                                <a href="{art['url']}" target="_blank"
                                   style="font-size:0.78rem;color:#63b3ed;text-decoration:none;">
                                    ↗ Read
                                </a>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="card card-fake">
                        <span class="pill pill-fake">✕ Fake / Unverified</span>
                        <p style="color:#9ca3af; margin-top:0.75rem; font-size:0.9rem;">
                            Found {len(articles)} related articles, but none confirm your claim.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown('<div class="section-label" style="margin-top:1rem;">Best Related Matches (Don\'t Confirm Claim Explicitly)</div>',
                                unsafe_allow_html=True)
                    for art in articles[:3]:
                        match_s = next((s for a, s in scored_articles if a == art), 0)
                        st.markdown(f"""
                        <div class="card" style="padding:1rem 1.2rem;">
                            <div class="card-meta">{art['source']} · {match_s:.0f}% strict match</div>
                            <div style="font-size:0.9rem;color:#e8e8f0;">{art['title'][:80]}…</div>
                            <a href="{art['url']}" target="_blank"
                               style="font-size:0.78rem;color:#63b3ed;text-decoration:none;">
                                ↗ Read
                            </a>
                        </div>
                        """, unsafe_allow_html=True)

# ── Footer ──
st.markdown("""
<hr class="custom-divider">
<div style="text-align:center; color:#374151; font-size:0.78rem; padding-bottom:2rem;">
    TruthLens · Built with NewsAPI · Verify before you share
</div>
""", unsafe_allow_html=True)