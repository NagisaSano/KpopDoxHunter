import requests, re, time, json
from datetime import datetime
import pandas as pd  # ML data
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

API_KEY = "AIzaSyD..."  # Ta clé
PLATFORMS = {
    'youtube': f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={{}}&type=video&key={API_KEY}&maxResults=20",
    'twitter': "https://api.twitter.com/2/tweets/search/recent?query={}&max_results=20",  # Bearer token free
    'tiktok': "https://www.tiktok.com/api/search/general/full/?keyword={}",  # Scraping light
}

# Dataset ML entraînement (vrais dox patterns)
TRAINING_DATA = [
    "Felix maison Séoul 25min transports", "Hamedaxmj devant chez Felix", 
    "adresse Felix Stray Kids quartier", "Felix lives here Korea house"
]

def cataclysmic_scan():
    vectorizer = TfidfVectorizer()
    X_train = vectorizer.fit_transform(TRAINING_DATA)
    
    all_hits = []
    for platform, url in PLATFORMS.items():
        for query in ["Felix Séoul", "Hamedaxmj Felix", "Stray Kids maison", "Felix address Korea"]:
            try:
                if platform == 'youtube':
                    resp = requests.get(url.format(query)).json()
                    for v in resp['items']:
                        text = (v['snippet']['title'] + v['snippet']['description']).lower()
                        vec = vectorizer.transform([text])
                        dox_score = cosine_similarity(X_train, vec)[0].max()
                        if dox_score > 0.3:  # ML threshold
                            all_hits.append({
                                'platform': platform, 'title': v['snippet']['title'],
                                'id': v['id']['videoId'], 'score': dox_score
                            })
                time.sleep(0.1)  # Rate limit
            except: pass
    
    # Export CSV pro
    df = pd.DataFrame(all_hits)
    df.to_csv(f"kpop_dox_scan_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", index=False)
    print(f"🌋 CATACLYSMIC SCAN: {len(all_hits)} hits → kpop_dox_scan_*.csv")
    return df

df_hits = cataclysmic_scan()
print(df_hits.head())
