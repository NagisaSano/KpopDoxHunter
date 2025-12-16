from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError
from flask import Flask, render_template

app = Flask(__name__)

REPORTS_DIR = Path("reports")


def get_latest_report():
    csv_files = sorted(REPORTS_DIR.glob("dox_report_*.csv"))
    if not csv_files:
        return None

    latest = csv_files[-1]
    try:
        df = pd.read_csv(latest)
    except (OSError, EmptyDataError) as exc:
        print(f"[WARN] Failed to read report '{latest}': {exc}")
        return None
    if df.empty:
        return None

    # Tri décroissant par score
    if "dox_score" in df.columns:
        df = df.sort_values("dox_score", ascending=False)

    # Format du score
    if "dox_score" in df.columns:
        df["dox_score_fmt"] = df["dox_score"].round(3)

    return df


@app.route("/")
def index():
    df = get_latest_report()
    if df is None:
        return render_template("index.html", df=None)

    return render_template("index.html", df=df)


if __name__ == "__main__":
    app.run(debug=False)
