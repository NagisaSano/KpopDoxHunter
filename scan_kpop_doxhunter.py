import os
import re
import html
import time
import unicodedata
from datetime import datetime
from typing import Dict, Tuple

import pandas as pd
import requests
from requests.exceptions import RequestException
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configuration
REQUEST_TIMEOUT = 10
MIN_DOX_SCORE = 0.25  # Raised threshold to reduce false positives
RETRY_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 1.5
MAX_PAGES_PER_QUERY = 2  # Pagination cap to reduce quota usage

QUERIES = [
    "Felix maison Seoul",
    "Felix address Seoul",
    "Stray Kids Felix house",
    "Felix home location",
]

# ===== CORPUS ENRICHI (30+ exemples) =====
DOX_CORPUS = [
    # Cas Hamedaxmj (references directes)
    "Felix maison Seoul transports 25 minutes",
    "Hamedaxmj devant chez Felix Stray Kids",
    "Felix qui vit ici je ne sais pas qui tu es",
    "passants m'ont dit Felix habite ici quartier",

    # Adresses et lieux precis
    "adresse Felix quartier Coree du Sud Seoul",
    "Felix lives here Seoul house neighborhood",
    "apartment building Felix Gangnam Itaewon",
    "Felix home address location Korea",
    "maison de Felix rue Seoul district",

    # Indications de proximite dangereuses
    "25 minutes de transport pour voir Felix",
    "proche de chez Felix walking distance",
    "devant l'immeuble de Felix spotted",
    "Felix sortir de sa maison waiting outside",
    "Felix apartment complex entrance door",

    # Termes de stalking
    "j'ai trouve ou habite Felix stalking",
    "spotted Felix leaving his house",
    "Felix private residence location coordinates",
    "Felix home leaked dox doxx information",
    "suivre Felix jusqu a chez lui follow home",

    # Contexte geographique precis
    "Seoul Gangnam dong gu ro Felix building",
    "GPS coordinates Felix house latitude longitude",
    "street view Felix apartment Google Maps",
    "Felix neighborhood tour walking video",
    "immeuble Felix vue de la rue street",

    # Variantes langues mixtes
    "Felix house tour maison visite domicile",
    "ou vit Felix where does Felix live address",
    "Felix casa apartamento direccion Seoul",
    "Felix wohnt hier Adresse Haus Korea",
]

# ===== STOP WORDS =====
FRENCH_STOP_WORDS = {
    "le", "la", "les", "un", "une", "des", "et", "ou", "de", "du", "en",
    "dans", "au", "aux", "pour", "avec", "sur", "chez", "qui", "que",
}
STOP_WORDS = ENGLISH_STOP_WORDS.union(FRENCH_STOP_WORDS)
STOP_WORDS = sorted(STOP_WORDS)

# ===== REGEX PATTERNS (detection explicite) =====
DOX_PATTERNS = {
    # Coordonnees GPS (lat, long)
    "coords_gps": re.compile(
        r"\b\d{1,3}\.\d{4,},?\s*\d{1,3}\.\d{4,}\b", re.IGNORECASE
    ),

    # Adresses coreennes (Seoul + suffixes dong/gu/ro)
    "adresse_coree": re.compile(
        r"\b(Seoul|Gangnam|Itaewon|Hongdae|Myeongdong|Yongsan|Mapo|Coree|Korea)\b.{0,50}\b(dong|gu|ro|gil|address|adresse|quartier|neighborhood)\b",
        re.IGNORECASE,
    ),

    # Motifs adresse internationale (numero + rue/route)
    "adresse_numero": re.compile(
        r"\b\d{1,4}\s+(street|st|avenue|ave|road|rd|rue|chemin|route|boulevard|blvd|apartment|apt|building)\b",
        re.IGNORECASE,
    ),

    # Indications de domicile (assoupli)
    "indication_domicile": re.compile(
        r"\b(vit|habite|lives?|house|maison|apartment|appartement|building|immeuble|fenetre|window|chez|home|residence)\b",
        re.IGNORECASE,
    ),

    # Distances precises (X minutes/km de)
    "distance_precise": re.compile(
        r"\b\d+\s+(minutes?|min|km|metres?|meters?)\b",
        re.IGNORECASE,
    ),

    # Termes de stalking explicites
    "stalking_terms": re.compile(
        r"\b(stalking?|suivre|follow|spotted?|devant|derriere|outside|entrance|porte|door|waiting|fenetre|window)\b",
        re.IGNORECASE,
    ),

    # Mots-cles dox directs
    "dox_keywords": re.compile(
        r"\b(address|adresse|location|GPS|coordinates|dox+|leak|private|residence|visit|visite)\b",
        re.IGNORECASE,
    ),

    # Infos perso additionnelles
    "infos_perso": re.compile(
        r"\b(phone|numero|email|mail|snap|instagram|insta|kakao)\b",
        re.IGNORECASE,
    ),
}


def normalize_text(text: str) -> str:
    """Unescape HTML, strip accents, lower, and collapse whitespace."""
    text = html.unescape(text or "")
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode()
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def compute_rule_score(text: str) -> Tuple[float, Dict[str, int]]:
    """Calcule un score base sur les patterns regex detectes."""
    matches = {}
    for pattern_name, regex in DOX_PATTERNS.items():
        count = len(regex.findall(text))
        matches[pattern_name] = count

    # Poids par categorie (plus grave = plus de points)
    weights = {
        "coords_gps": 0.40,         # GPS = CRITICAL
        "adresse_coree": 0.30,      # Adresse precise
        "adresse_numero": 0.25,     # Adresse structuree
        "dox_keywords": 0.20,       # Mots-cles dox
        "indication_domicile": 0.15,# Indication lieu
        "distance_precise": 0.10,   # Distance
        "stalking_terms": 0.10,     # Stalking
        "infos_perso": 0.10,        # Infos personnelles
    }

    rule_score = 0.0
    for key, count in matches.items():
        if count > 0:
            rule_score += weights.get(key, 0.05) * min(count, 3)  # cap a 3 occurrences

    rule_score = min(rule_score, 1.0)
    return rule_score, matches


def compute_severity(composite_score: float, rule_score: float) -> str:
    """Determine le niveau de gravite."""
    if composite_score >= 0.65 or rule_score >= 0.50:
        return "CRITICAL"
    elif composite_score >= 0.45 or rule_score >= 0.30:
        return "HIGH"
    elif composite_score >= 0.25:
        return "MEDIUM"
    else:
        return "LOW"


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
    seen_ids = set()

    for query in QUERIES:
        url = "https://www.googleapis.com/youtube/v3/search"
        page_token = None
        pages_fetched = 0

        while True:
            params = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "key": api_key,
                "maxResults": 15,
            }
            if page_token:
                params["pageToken"] = page_token

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
                break

            if "items" not in data:
                print(
                    f"[WARN] No 'items' in response for query '{query}' "
                    f"(status={resp.status_code}, error={data.get('error')})"
                )
                break

            if not data["items"]:
                break

            successful_fetch = True

            for video in data["items"]:
                snippet = video.get("snippet", {})
                raw_title = snippet.get("title") or ""
                raw_description = snippet.get("description") or ""
                video_id = video.get("id", {}).get("videoId")

                if not video_id or video_id in seen_ids:
                    continue

                seen_ids.add(video_id)

                title = normalize_text(raw_title)
                description = normalize_text(raw_description)
                text = f"{title} {description}".strip()

                vec = vectorizer.transform([text])
                ml_score = cosine_similarity(X_train, vec).max()

                rule_score, pattern_matches = compute_rule_score(text)

                composite_score = 0.40 * ml_score + 0.60 * rule_score

                severity = compute_severity(composite_score, rule_score)

                results.append(
                    {
                        "query": query,
                        "title": html.unescape(raw_title)[:100],
                        "video_id": video_id,
                        "ml_score": round(ml_score, 3),
                        "rule_score": round(rule_score, 3),
                        "dox_score": round(composite_score, 3),
                        "severity": severity,
                        "patterns": str(pattern_matches),
                        "timestamp": datetime.now(),
                    }
                )

            pages_fetched += 1
            page_token = data.get("nextPageToken")
            if not page_token or pages_fetched >= MAX_PAGES_PER_QUERY:
                break

        if quota_blocked:
            break

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
    print(df[["title", "dox_score", "severity"]].head(10))

    if quota_blocked:
        raise SystemExit(
            "[KpopDoxHunter] Quota or forbidden responses detected; partial results saved."
        )

    return df


if __name__ == "__main__":
    hits = ml_dox_hunter()
def normalize_text(text: str) -> str:
    """Unescape HTML, strip accents, lower, and collapse whitespace."""
    text = html.unescape(text or "")
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode()
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text
