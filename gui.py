import tkinter as tk
from tkinter import scrolledtext, ttk
from news_fetcher import fetch_latest_news
from detector import analyze_article
from datetime import datetime
import pandas as pd

# ─────────────────────────────────────────
# SAVE TO CSV
# ─────────────────────────────────────────
def save_to_csv(results, topic):
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
    return filename


# ─────────────────────────────────────────
# OUTPUT HELPER
# ─────────────────────────────────────────
def clear_output():
    output_box.configure(state="normal")
    output_box.delete(1.0, tk.END)

def write(text, color="white"):
    output_box.configure(state="normal")
    output_box.insert(tk.END, text + "\n", color)
    output_box.see(tk.END)
    root.update()


# ─────────────────────────────────────────
# MODE 1 — TOPIC SEARCH
# ─────────────────────────────────────────
def check_by_topic():
    clear_output()
    topic = entry.get().strip()
    count = int(count_var.get())

    if not topic:
        write("⚠️ Please enter a topic!", "orange")
        return

    write(f"🔍 Fetching {count} articles about '{topic}'...", "yellow")
    articles = fetch_latest_news(topic=topic, count=count)

    if not articles:
        write("❌ No articles found. Check your NewsAPI key!", "red")
        return

    write(f"✅ Found {len(articles)} articles. Analyzing...\n", "green")

    all_results = []
    real = suspicious = fake = 0

    for i, article in enumerate(articles, 1):
        result = analyze_article(article)
        all_results.append(result)

        verdict = result["verdict"]
        color = "green" if "REAL" in verdict else "orange" if "SUSPICIOUS" in verdict else "red"

        write("=" * 60, "gray")
        write(f"📰 [{i}] {article['title']}", "white")
        write(f"🔗 SOURCE     : {article['source']}", "cyan")
        write(f"🔍 VERDICT    : {verdict}", color)
        write(f"📊 TRUST SCORE: {result['confidence']}", "yellow")
        write(f"🚩 RED FLAGS  : {', '.join(result['red_flags'])}", "orange")
        write(f"🔗 URL        : {article['url']}", "cyan")

        if "REAL" in verdict: real += 1
        elif "SUSPICIOUS" in verdict: suspicious += 1
        else: fake += 1

    write("\n" + "=" * 60, "gray")
    write(f"📊 SUMMARY FOR '{topic.upper()}'", "white")
    write(f"  ✅ Real       : {real}", "green")
    write(f"  ⚠️  Suspicious  : {suspicious}", "orange")
    write(f"  ❌ Fake        : {fake}", "red")
    write(f"  📰 Total       : {len(articles)}", "white")

    filename = save_to_csv(all_results, topic)
    write(f"\n💾 Saved to: {filename}", "cyan")


# ─────────────────────────────────────────
# MODE 2 — URL CHECKER
# ─────────────────────────────────────────
def check_by_url():
    clear_output()
    url = entry.get().strip()

    if not url.startswith("http"):
        write("⚠️ Please paste a valid URL starting with http!", "orange")
        return

    write(f"🔗 Fetching article from URL...", "yellow")

    try:
        from newspaper import Article
        art = Article(url)
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
        verdict = result["verdict"]
        color = "green" if "REAL" in verdict else "orange" if "SUSPICIOUS" in verdict else "red"

        write("=" * 60, "gray")
        write(f"📰 TITLE      : {data['title']}", "white")
        write(f"🔗 SOURCE     : {data['source']}", "cyan")
        write(f"🔍 VERDICT    : {verdict}", color)
        write(f"📊 TRUST SCORE: {result['confidence']}", "yellow")
        write(f"🚩 RED FLAGS  : {', '.join(result['red_flags'])}", "orange")
        write("=" * 60, "gray")

        filename = save_to_csv([result], "url_check")
        write(f"\n💾 Saved to: {filename}", "cyan")

    except Exception as e:
        write(f"❌ Could not fetch article: {e}", "red")


# ─────────────────────────────────────────
# MODE 3 — CLAIM VERIFIER
# ─────────────────────────────────────────
def check_by_claim():
    clear_output()
    claim = entry.get().strip()

    if not claim:
        write("⚠️ Please enter a news claim!", "orange")
        return

    write(f"🔍 Searching for: '{claim}'...", "yellow")
    articles = fetch_latest_news(topic=claim, count=10)

    write("=" * 60, "gray")
    write(f"📰 YOUR CLAIM : {claim}", "white")
    write("=" * 60, "gray")

    if not articles:
        write("🔍 VERDICT    : ❌ FAKE / UNVERIFIED", "red")
        write("💬 REASON     : No matching news found in any real source.", "white")
        return

    claim_words = set(claim.lower().split())
    matched = []

    for article in articles:
        words = set((article["title"] or "").lower().split()) | \
                set((article["description"] or "").lower().split())
        score = len(claim_words & words) / len(claim_words) * 100 if claim_words else 0
        if score >= 40:
            matched.append((article, score))

    matched.sort(key=lambda x: x[1], reverse=True)

    if matched:
        best, score = matched[0]
        result = analyze_article(best)
        write("🔍 VERDICT    : ✅ REAL — Found in verified sources!", "green")
        write(f"📊 MATCH SCORE: {score:.0f}%", "yellow")
        write(f"🔗 SOURCE     : {best['source']}", "cyan")
        write(f"📰 FOUND AS   : {best['title']}", "white")
        write(f"🔗 URL        : {best['url']}", "cyan")
        write(f"🚩 RED FLAGS  : {', '.join(result['red_flags'])}", "orange")

        if len(matched) > 1:
            write(f"\n📌 Also reported by {len(matched)-1} other source(s):", "white")
            for art, s in matched[1:4]:
                write(f"   • {art['source']} ({s:.0f}%) — {art['title'][:55]}...", "cyan")
    else:
        write("🔍 VERDICT    : ❌ FAKE / UNVERIFIED", "red")
        write("💬 REASON     : Claim not found in any verified source.", "white")
        write("\n📌 Related articles (don't confirm your claim):", "white")
        for art in articles[:3]:
            write(f"   • {art['source']} — {art['title'][:55]}...", "cyan")

    write("=" * 60, "gray")


# ─────────────────────────────────────────
# BUILD GUI WINDOW
# ─────────────────────────────────────────
root = tk.Tk()
root.title("🗞️ Fake News Detector")
root.geometry("800x620")
root.configure(bg="#1e1e2e")
root.resizable(True, True)

# ── Title ──
tk.Label(root, text="🗞️ Fake News Detector",
         font=("Arial", 20, "bold"),
         bg="#1e1e2e", fg="white").pack(pady=12)

# ── Input Box ──
tk.Label(root, text="Enter Topic / URL / Claim:",
         font=("Arial", 11), bg="#1e1e2e", fg="#aaaaaa").pack()

entry = tk.Entry(root, width=70, font=("Arial", 12),
                 bg="#2e2e3e", fg="white", insertbackground="white")
entry.pack(pady=6, ipady=6, padx=20)

# ── Article Count ──
count_frame = tk.Frame(root, bg="#1e1e2e")
count_frame.pack()
tk.Label(count_frame, text="Articles to fetch:",
         font=("Arial", 10), bg="#1e1e2e", fg="#aaaaaa").pack(side=tk.LEFT, padx=5)
count_var = tk.StringVar(value="5")
count_spin = ttk.Spinbox(count_frame, from_=1, to=10,
                          textvariable=count_var, width=5, font=("Arial", 11))
count_spin.pack(side=tk.LEFT)

# ── Buttons ──
btn_frame = tk.Frame(root, bg="#1e1e2e")
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="1️⃣  Search by TOPIC",
          font=("Arial", 11, "bold"), bg="#4CAF50", fg="white",
          padx=12, pady=6, command=check_by_topic).grid(row=0, column=0, padx=8)

tk.Button(btn_frame, text="2️⃣  Check a URL",
          font=("Arial", 11, "bold"), bg="#2196F3", fg="white",
          padx=12, pady=6, command=check_by_url).grid(row=0, column=1, padx=8)

tk.Button(btn_frame, text="3️⃣  Verify a CLAIM",
          font=("Arial", 11, "bold"), bg="#FF9800", fg="white",
          padx=12, pady=6, command=check_by_claim).grid(row=0, column=2, padx=8)

# ── Output Box ──
output_box = scrolledtext.ScrolledText(root, width=90, height=20,
                                        font=("Courier", 10),
                                        bg="#0d0d1a", fg="white",
                                        state="normal")
output_box.pack(pady=10, padx=15)

# Color Tags
output_box.tag_config("green",  foreground="#4CAF50")
output_box.tag_config("red",    foreground="#f44336")
output_box.tag_config("orange", foreground="#FF9800")
output_box.tag_config("cyan",   foreground="#00BCD4")
output_box.tag_config("yellow", foreground="#FFEB3B")
output_box.tag_config("gray",   foreground="#555555")
output_box.tag_config("white",  foreground="#ffffff")

# ── Footer ──
tk.Label(root, text="💾 Results auto-saved to CSV after each check",
         font=("Arial", 9), bg="#1e1e2e", fg="#555555").pack(pady=4)

write("👋 Welcome! Enter a topic, URL, or claim above and click a button.", "cyan")

root.mainloop()