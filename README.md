# KpopDoxHunter

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![License](https://img.shields.io/github/license/NagisaSano/KpopDoxHunter)
![Last Commit](https://img.shields.io/github/last-commit/NagisaSano/KpopDoxHunter)
![Stars](https://img.shields.io/github/stars/NagisaSano/KpopDoxHunter?style=social)

KpopDoxHunter is a small anti‑doxxing experiment for K‑pop idols. It queries the YouTube API with suspicious search phrases and uses a lightweight ML filter (TF‑IDF + cosine similarity) to flag videos that look like they contain potential doxxing content (addresses, home descriptions, etc.). 

The goal is not to be perfect, but to demonstrate:
- How to combine a public API (YouTube Data API) with a simple NLP pipeline.
- How to build a tiny “monitoring” dashboard around it using Flask and pandas.

---

## Why this project?

This tool was built after discovering a YouTube video that inadvertently exposed the presumed address of a K-pop idol. Instead of amplifying the issue, I created an automated scanner to:
- **Detect similar content** before it spreads widely
- **Demonstrate ethical use** of cybersecurity and ML skills
- **Provide a portfolio piece** showcasing API integration, NLP, and web development

This is an educational project exploring automated content monitoring for privacy protection.

---

## 📊 Dashboard Preview

![Dashboard showing suspicious videos](docs/dashboard_screenshot.png)

*Live Flask dashboard displaying videos sorted by doxxing risk score*

---

## Features

- Runs 4 predefined YouTube searches in French/English around Felix (Stray Kids) and doxxing‑style phrases. 
- Vectorizes titles + descriptions with TF‑IDF and scores them against a small “doxxing” corpus using cosine similarity. 
- Saves results to timestamped CSV files in `reports/` and serves the latest report via a simple Flask dashboard. 

Example report files included in the repo:
- `reports/dox_report_20251215_2250.csv`
- `reports/dox_report_20251215_2312.csv`  
These show 50–60 hits each for the predefined queries. 

---

## Tech stack

- **Python 3.12**
- **YouTube Data API v3**
- **pandas**, **numpy**
- **scikit‑learn** (TF‑IDF + cosine similarity)
- **Flask** (minimal dashboard) 

Installable via:

pip install -r requirements.txt

---

## Project structure

KpopDoxHunter/
scan_kpop_doxhunter.py # ML scanner: YouTube API + TF‑IDF + cosine + CSV output
dashboard.py # Flask app that serves the latest report
templates/
index.html # Simple HTML table for the report
reports/ # Generated CSV reports (ignored in .gitignore)
run_all.bat # Windows helper: run scan + dashboard
requirements.txt
.gitignore

---

## Setup & usage

### 1. Clone the repo

git clone https://github.com/NagisaSano/KpopDoxHunter.git
cd KpopDoxHunter

### 2. (Optional) Create a virtualenv

python -m venv .venv
..venv\Scripts\activate # Windows PowerShell

### 3. Install dependencies

python -m pip install -r requirements.txt

### 4. Configure your YouTube API key

The scanner expects your key in the `YOUTUBE_API_KEY` environment variable: 

**Windows (PowerShell):**

$env:YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY"

If the key is missing or invalid, the script will log warnings such as:

[WARN] No 'items' in response for query 'Hamedaxmj Felix' (status=400, error={...})
[KpopDoxHunter] No results collected (check your YouTube API key or quota).

### 5. Run scan + dashboard

On Windows:

.\run_all.bat

This will:
- Launch the ML scan (`scan_kpop_doxhunter.py`) and generate a report in `reports/`. 
- Start the Flask dashboard at `http://127.0.0.1:5000`, which serves the latest CSV as an HTML table. 

---

## Notes & limitations

- This is a **toy project** to explore the idea of automated doxxing detection; it is not meant as a production‑grade safety tool.   
- The “corpus” used for TF‑IDF is intentionally tiny and biased towards Felix / Stray Kids, just to keep the example simple. 
- The Flask server runs with `debug=True` and the built‑in development server (Werkzeug); use a proper WSGI server if you ever deploy it. 
