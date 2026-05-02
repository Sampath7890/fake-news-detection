# Fake News Detection

A Python project that checks how trustworthy a news article looks using lightweight rule-based signals.

## Features

- Analyze latest news articles by topic (via NewsAPI)
- Check a single article URL
- Verify whether a claim appears across real news sources
- Rule-based trust scoring with red-flag explanations
- Save analysis results to CSV
- Optional Streamlit web UI

## Project Structure

- `main.py` — CLI app with menu for topic/URL/claim checks
- `app.py` — Streamlit UI
- `news_fetcher.py` — NewsAPI fetch logic
- `detector.py` — Rule-based fake-news detection engine
- `url_checker.py` / `gui.py` — helper/alternate interfaces

## Requirements

- Python 3.9+
- A NewsAPI key

Install dependencies (example):

```bash
pip install pandas requests python-dotenv newspaper3k streamlit
```

## Configuration

Create a `.env` file in the project root:

```env
NEWSAPI_KEY=your_newsapi_key_here
```

## Run

### CLI

```bash
python main.py
```

### Streamlit UI

```bash
streamlit run app.py
```

## How scoring works

`detector.py` starts from a base score and adjusts it using checks such as:

- Source credibility
- Clickbait/fake keyword presence
- Sensational punctuation/all-caps title patterns
- Missing/very short content
- Missing description
- Unusually long title

Final verdict bands:

- `✅ REAL` (70–100)
- `⚠️ SUSPICIOUS` (40–69)
- `❌ FAKE` (0–39)

## Notes

- This tool is heuristic-based and should not be treated as definitive fact-checking.
- Results depend on article text quality and source metadata.
