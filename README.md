# 🛡️ KpopDoxHunter
**Anti-sasaeng scanner for K-pop idols** (Felix / Stray Kids use case)

## Live Demo (v2.0 – ML)
Example scan output:
- `2025-12-15 22:50` → `dox_report_20251215_2250.csv` (50 hits)
- `2025-12-15 23:12` → `dox_report_20251215_2312.csv` (60 hits) [file:e25282f5-aefa-47f7-a6cb-a4b1e48c1a6e]

Top scores (YouTube):
- `Je FUGUE SEUL en CORÉE DU SUD ... #1` → `dox_score ≈ 0.72`
- `JE TESTE LE PLUS GRAND PARC D'ATTRACTION DE COREE DU SUD` → `dox_score ≈ 0.69` [file:792220a8-e4f2-4577-861c-fbba0cb58109]

## Tech Stack
- Python 3 + `requests`, `pandas`, `scikit-learn`
- YouTube Data API v3 (search)
- TF-IDF + cosine similarity for doxxing score
- Flask dashboard (HTML table of latest CSV report)

## How to run

1. Clone the repo:
git clone https://github.com/NagisaSano/KpopDoxHunter.git
cd KpopDoxHunter

2. Install dependencies:
pip install -r requirements.txt # (or manually: requests, pandas, scikit-learn, flask)

3. Set your YouTube API key in `proto.py`:
API_KEY = "YOUR_API_KEY_HERE"

4. Run scan + dashboard:
run_all.bat # on Windows

Then open `http://127.0.0.1:5000` in your browser.

## Project goal
Detect and score potential doxxing/stalking content targeting K-pop idols (starting with Felix) across YouTube search results.

