import os
import time
from datetime import datetime

import pandas as pd
import requests
from requests.exceptions import RequestException
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

REQUEST_TIMEOUT = 10
MIN_DOX_SCORE = 0.15
RETRY_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 1.5

QUERIES = [
    "Hamedaxmj Felix",
    "Felix Seoul",
    "Stray Kids maison",
    "Felix Coree address",
]

DOX_CORPUS = [
    "Felix maison Seoul transports 25 minutes",
    "Hamedaxmj devant chez Felix Stray Kids",
    "adresse Felix quartier Coree du Sud",
    "Felix lives here Seoul house passants",
]

FRENCH_STOP_WORDS = {
    "le",
    "la",
    "les",
    "un",
    "une",
    "des",
    "et",
    "ou",
    "de",
    "du",
    "en",
    "dans",
    "au",
    "aux",
    "pour",
    "avec",
    "sur",
    "chez",
}
STOP_WORDS = ENGLISH_STOP_WORDS.union(FRENCH_STOP_WORDS)
STOP_WORDS = sorted(STOP_WORDS)


def require_api_key() -> str:
    """Stop execution early when the API key is missing or placeholder."""
    key = os.getenv("YOUTUBE_API_KEY")
    if not key or key == "DEMO_KEY_CHANGE_ME":
        raise SystemExit(
            "[KpopDoxHunter] Missing YouTube API key. "
            "Set YOUTUBE_API_KEY before running the scanner."
        )
    return key


def ml_dox_hunter():
    api_key = require_api_key()

    vectorizer = TfidfVectorizer(stop_words=STOP_WORDS, strip_accents="unicode")
    X_train = vectorizer.fit_transform(DOX_CORPUS)

    results = []
    request_failures = 0
    successful_fetch = False
    quota_blocked = False
    for query in QUERIES:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "key": api_key,
            "maxResults": 15,
        }

        data = None
        for attempt in range(1, RETRY_ATTEMPTS + 1):
            try:
                resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
                status = resp.status_code
                if status in (403, 429):
                    quota_blocked = True
                    request_failures += 1
                    print(
                        f"[WARN] Quota/forbidden for query '{query}' "
                        f"(status={status}, attempt {attempt}/{RETRY_ATTEMPTS})"
                    )
                    break

                resp.raise_for_status()
                data = resp.json()
                break
            except RequestException as exc:
                request_failures += 1
                print(
                    f"[WARN] Request failed for query '{query}' "
                    f"(attempt {attempt}/{RETRY_ATTEMPTS}): {exc}"
                )
                code = getattr(getattr(exc, "response", None), "status_code", None)
                if code in (403, 429):
                    quota_blocked = True
                    break
                if attempt < RETRY_ATTEMPTS:
                    time.sleep(RETRY_BACKOFF_SECONDS * attempt)
            except ValueError:
                request_failures += 1
                print(
                    f"[ERROR] Invalid JSON for query '{query}' "
                    f"(status={resp.status_code})"
                )
                break

        if quota_blocked:
            break
        if data is None or not isinstance(data, dict):
            continue

        if "items" not in data:
            print(
                f"[WARN] No 'items' in response for query '{query}' "
                f"(status={resp.status_code}, error={data.get('error')})"
            )
            continue

        if not data["items"]:
            continue
        successful_fetch = True

        for video in data["items"]:
            snippet = video.get("snippet", {})
            title = snippet.get("title") or ""
            description = snippet.get("description") or ""
            video_id = video.get("id", {}).get("videoId")
            if not video_id:
                continue  # skip incomplete items

            text = (title + " " + description).lower()
            vec = vectorizer.transform([text])
            dox_score = cosine_similarity(X_train, vec).max()
            results.append(
                {
                    "query": query,
                    "title": title[:100],
                    "video_id": video_id,
                    "dox_score": dox_score,
                    "timestamp": datetime.now(),
                }
            )

    df = pd.DataFrame(results)
    if df.empty:
        if not successful_fetch and request_failures:
            raise SystemExit("[KpopDoxHunter] All requests failed; no report generated.")
        print("[KpopDoxHunter] No results collected (check API key, quota, or queries).")
        return df

    if "dox_score" not in df.columns:
        print("[KpopDoxHunter] No 'dox_score' column in results, skipping ML filter.")
        return df

    df = df[df["dox_score"] >= MIN_DOX_SCORE].sort_values("dox_score", ascending=False)
    if df.empty:
        print(f"[KpopDoxHunter] No videos above the dox_score threshold ({MIN_DOX_SCORE}).")
        return df

    print(f"[KpopDoxHunter] Found {len(df)} suspicious videos.")

    os.makedirs("reports", exist_ok=True)
    filename = f"dox_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    filepath = os.path.join("reports", filename)

    df.to_csv(filepath, index=False)
    print(f"[KpopDoxHunter] ML scan saved {len(df)} hits to {filepath}")
    print(df[["title", "dox_score"]].head())
    if quota_blocked:
        raise SystemExit(
            "[KpopDoxHunter] Quota or forbidden responses detected; partial results saved."
        )
    return df


if __name__ == "__main__":
    hits = ml_dox_hunter()
