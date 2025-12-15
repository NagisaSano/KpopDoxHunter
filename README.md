# 🛡️ KpopDoxHunter - ML Anti-Sasaeng Scanner

**Protège idols K-pop vs doxxing** (Felix StrayKids use case)

## 🚀 Live Demo V2.0
[2025-12-15 22:50] ML SCAN: 50 hits → dox_report_20251215_2250.csv
Hamedaxmj Felix Corée: 0.72 score (🚨 HIGH RISK)

## Tech Stack Senior
- **YouTube Data API v3** (10k/jour)
- **scikit-learn TF-IDF + Cosine Similarity** (ML dox scoring)
- **Pandas** CSV exports timestamped
- **4 queries multi-angle** (Hamedaxmj, Felix Séoul, Stray Kids maison)

## Results V2.0
| Query | Top Hit | ML Score |
|-------|---------|----------|
| Hamedaxmj Felix | "Je FUGUE SEUL en CORÉE..." | **0.724** 🚨 |
| Stray Kids maison | "[SKZ LOG] Stray Kids..." | **0.615** ⚠️ |

**Next**: Telegram alerts + GitHub Actions 24/7
