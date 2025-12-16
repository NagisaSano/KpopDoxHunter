# KpopDoxHunter

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![License](https://img.shields.io/github/license/NagisaSano/KpopDoxHunter)
![Last Commit](https://img.shields.io/github/last-commit/NagisaSano/KpopDoxHunter)
![Stars](https://img.shields.io/github/stars/NagisaSano/KpopDoxHunter?style=social)

---

**KpopDoxHunter** is a hybrid **Machine Learning + Regex** anti-doxxing detection system for K-pop idols.  
It queries the **YouTube Data API** with suspicious search phrases and uses **TF-IDF vectorization + 6 regex pattern classes** to flag videos potentially containing doxxing elements (addresses, GPS coordinates, stalking behaviors, etc.).

---

## 🧠 Why this project?

This tool was created after discovering a YouTube video that **inadvertently revealed the presumed address** of a K-pop idol.  
Instead of amplifying the problem, the goal was to:

- Detect similar content **before it spreads**
- Demonstrate **ethical use of cybersecurity + ML**
- Provide a **portfolio project** combining API, NLP, and web integration

This project explores **automated, privacy-oriented content monitoring** in an educational context.

---

## ⚙️ Features (v2.0 – Hybrid Detection)

- **30+ example corpus** of real doxxing scenarios (addresses, GPS leaks, stalking terms)
- **6 Regex categories**:
  1. GPS coordinates (`lat/long`)
  2. Korean addresses (`Seoul`, `dong/gu/ro`)
  3. Home indicators (`house`, `apartment`, `window`, `behind`)
  4. Distances (`X minutes/km from`)
  5. Stalking terms (`following`, `spotted`, `outside`)
  6. Dox keywords (`address`, `leak`, `private`, `location`)
- **Composite scoring** → `50% ML (TF-IDF)` + `50% Regex`
- **Severity levels** → `LOW / MEDIUM / HIGH / CRITICAL`
- **Flask dashboard** with color-coded severity badges
- Auto-saves timestamped reports in `reports/`

---

## 🧰 Tech Stack

- **Python 3.12**
- **YouTube Data API v3**
- **pandas**, **numpy**
- **scikit-learn** (TF-IDF + cosine similarity)
- **Flask** (web dashboard)

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🗂️ Project Structure

```
KpopDoxHunter/
├── scan_kpop_doxhunter.py     # Hybrid ML + regex scanner
├── dashboard.py               # Flask app (serves latest report)
├── templates/
│   └── index.html             # HTML table with severity colors
├── reports/                   # Generated CSV reports (git-ignored)
├── run_all.bat                # Windows helper script
├── requirements.txt
├── test_scan.py               # Unit tests
├── SECURITY.md
└── .gitignore
```

---

## 🚀 Setup & Usage

### 1. Clone the repo

```bash
git clone https://github.com/NagisaSano/KpopDoxHunter.git
cd KpopDoxHunter
```

### 2. (Optional) Create a virtual environment

```bash
python -m venv .venv
.\.venv\Scripts\activate  # on Windows
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure your YouTube API key

Set the key in your environment variables.

**Windows PowerShell:**

```bash
$env:YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY"
```

### 5. Run the full pipeline

```bash
.
un_all.bat
```

This will:
- Run `scan_kpop_doxhunter.py` → generate a CSV report in `reports/`
- Launch Flask dashboard → `http://127.0.0.1:5000`

---

### 📊 Example Output

```
[KpopDoxHunter] Found 14 suspicious videos.
[KpopDoxHunter] ML scan saved 14 hits to reports\dox_report_20251216_0126.csv
```

| title | dox_score | severity |
|-------|------------|-----------|
| Felix derrière sa fenêtre : 👁👄👁?? | 0.409 | HIGH |
| Je FUGUE SEUL en CORÉE DU SUD ... #1 | 0.424 | MEDIUM |

---

## 🔬 Detection Methodology

### 1. ML Component (TF-IDF + Cosine Similarity)
- 30+ training examples of doxxing content  
- Analyzes video `title + description`  
- Output → `ml_score` (0-1)

### 2. Regex Rules (6 Pattern Categories)
| Category | Example Pattern |
|-----------|-----------------|
| GPS | `\d{1,3}\.\d{4,},\s*\d{1,3}\.\d{4,}` |
| Address | `Seoul.*(dong|gu|ro)` |
| Home | `house|apartment|window|behind` |
| Distance | `\d+\s*(minutes?|km)\s*(de|from)` |
| Stalking | `following|spotted|waiting|outside` |
| Dox keywords | `address|leak|GPS|coordinates` |

Output → `rule_score` (0-1 weighted)

### 3. Composite Scoring

```
dox_score = 0.50 * ml_score + 0.50 * rule_score
```

### 4. Severity Levels

| Level | Condition |
|--------|------------|
| CRITICAL | dox_score ≥ 0.65 OR rule_score ≥ 0.50 |
| HIGH | dox_score ≥ 0.45 OR rule_score ≥ 0.30 |
| MEDIUM | dox_score ≥ 0.25 |
| LOW | dox_score < 0.25 |

---

## ⚠️ Notes & Limitations

- This is an **educational prototype**, not a production system.  
- Corpus currently biased towards **Felix / Stray Kids** data for testing.  
- Flask runs in `debug=True` (switch to WSGI for production).  
- Default threshold: `MIN_DOX_SCORE = 0.20` (adjustable).

---

## 📜 License

**MIT License** – see [LICENSE](LICENSE).

---

## 🛡️ Responsible Use

This project is intended for **ethical monitoring only**.  
Do **not** use it to:

- Harass or target individuals  
- Distribute private information  
- Violate YouTube’s Terms of Service  

Refer to [SECURITY.md](SECURITY.md) for reporting vulnerabilities or misuse.

---
