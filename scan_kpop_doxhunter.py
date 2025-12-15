import os
import requests, re, pandas as pd, numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime

API_KEY = os.getenv("YOUTUBE_API_KEY", "DEMO_KEY_CHANGE_ME")
QUERIES = ["Hamedaxmj Felix", "Felix Séoul", "Stray Kids maison", "Felix Corée address"]

DOX_CORPUS = [
    "Felix maison Séoul transports 25 minutes", "Hamedaxmj devant chez Felix Stray Kids",
    "adresse Felix quartier Corée du Sud", "Felix lives here Seoul house passants"
]

def ml_dox_hunter():
    vectorizer = TfidfVectorizer(stop_words='english')
    X_train = vectorizer.fit_transform(DOX_CORPUS)

    results = []
    for query in QUERIES:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'key': API_KEY,
            'maxResults': 15
        }

        resp = requests.get(url, params=params)
        try:
            data = resp.json()
        except Exception:
            print(f"[ERROR] Invalid JSON for query '{query}' (status={resp.status_code})")
            continue

        if 'items' not in data:
            print(f"[WARN] No 'items' in response for query '{query}' (status={resp.status_code}, error={data.get('error')})")
            continue

        for video in data['items']:
            text = (video['snippet']['title'] + ' ' + video['snippet']['description']).lower()
            vec = vectorizer.transform([text])
            dox_score = cosine_similarity(X_train, vec).max()
            results.append({
                'query': query,
                'title': video['snippet']['title'][:100],
                'video_id': video['id']['videoId'],
                'dox_score': dox_score,
                'timestamp': datetime.now()
            })

    df = pd.DataFrame(results)
    if df.empty:
        print("[KpopDoxHunter] No results collected (check your YouTube API key or quota).")
        return df  # DataFrame vide avec 0 ligne mais colonnes automatiques

    if 'dox_score' not in df.columns:
        print("[KpopDoxHunter] No 'dox_score' column in results, skipping ML filter.")
        return df

    df = df[df['dox_score'] > 0.1].sort_values('dox_score', ascending=False)
    print(f"[KpopDoxHunter] Found {len(df)} suspicious videos.")

    # Ensure "reports" directory exists
    os.makedirs("reports", exist_ok=True)

    filename = f"dox_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    filepath = os.path.join("reports", filename)

    df.to_csv(filepath, index=False)
    print(f"🌋 V8 ML SCAN: {len(df)} hits → {filepath}")
    print(df[['title', 'dox_score']].head())
    return df

if __name__ == "__main__":
    hits = ml_dox_hunter()
