# KpopDoxHunter

Hybrid ML + regex anti-doxxing detector for K-pop idols. It runs suspicious YouTube queries, scores titles/descriptions with TF-IDF plus explicit regex patterns (GPS, addresses, stalking terms), and serves the latest results via a color-coded Flask dashboard.

---

## Why this project?

After stumbling on a video leaking an idol’s presumed address, the goal was to:
- Detect similar content quickly (before it spreads)
- Demonstrate ethical use of API + NLP + lightweight rules
- Provide a small portfolio project mixing API, ML, and a web dashboard

---

## Features (v2.0)

- 30+ doxxing examples for TF-IDF semantic matching
- 6 regex categories: GPS, Korean address, home indicators, distances, stalking terms, dox keywords
- Composite scoring: 50% ML + 50% regex, severity badges (LOW/MEDIUM/HIGH/CRITICAL)
- Flask dashboard with sortable table and severity colors
- Timestamped CSV reports in `reports/`

---

## Tech stack

- Python 3.12
- YouTube Data API v3
- pandas, numpy
- scikit-learn (TF-IDF + cosine similarity)
- Flask (dashboard)

Install dependencies:
```
pip install -r requirements.txt
```

---

## Project structure

```
KpopDoxHunter/
├─ scan_kpop_doxhunter.py   # Hybrid ML + regex scanner
├─ dashboard.py             # Flask app (serves latest report)
├─ templates/
│  └─ index.html            # Dashboard HTML with severity colors
├─ reports/                 # Generated CSV reports (git-ignored)
├─ run_all.bat              # Windows helper script
├─ requirements.txt
├─ tests/test_scan.py       # Unit tests
└─ SECURITY.md
```

---

## Setup & usage

1) Clone the repo
```
git clone https://github.com/NagisaSano/KpopDoxHunter.git
cd KpopDoxHunter
```

2) (Optional) Virtualenv
```
python -m venv .venv
.\.venv\Scripts\activate  # Windows
```

3) Install deps
```
python -m pip install -r requirements.txt
```

4) Configure your YouTube API key (read at runtime)
```
$env:YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY"   # PowerShell
```

5) Run scan + dashboard
```
.\run_all.bat
```
This runs the scanner, writes a CSV in `reports/`, then serves the dashboard at `http://127.0.0.1:5000`.

6) Run tests
```
python -m unittest discover -s tests -p "test*.py" -v
```

---

## Notes & limitations

- Educational prototype; corpus biased toward Felix/Stray Kids.
- Threshold `MIN_DOX_SCORE` defaults to 0.25 (adjust in `scan_kpop_doxhunter.py`).
- Flask runs with `debug=False`; use a real WSGI server if you deploy.
- On 403/429 (quota), partial results are saved then the scan stops with a clear error.

---

## Detection methodology

- **ML (TF-IDF + cosine)**: semantic similarity against 30+ doxxing examples → `ml_score`
- **Regex rules**: 6 pattern categories (GPS, address, home terms, distance, stalking, dox keywords) → `rule_score`
- **Composite**: `dox_score = 0.5 * ml_score + 0.5 * rule_score`
- **Severity**: LOW / MEDIUM / HIGH / CRITICAL based on `dox_score` or `rule_score` thresholds

---

## Responsible use

For ethical monitoring only. Do not use this to harass, target individuals, leak private information, or violate YouTube’s Terms of Service. See `SECURITY.md` for reporting issues.
