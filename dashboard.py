from flask import Flask, render_template
import pandas as pd
import glob
import os

app = Flask(__name__)

@app.route('/')
def dashboard():
    csvs = glob.glob('reports/*.csv')
    if not csvs:
        return "No reports found in reports/ folder."

    # Tri par date de modification du fichier (le plus récent)
    latest_path = max(csvs, key=os.path.getmtime)

    latest = pd.read_csv(latest_path)
    return render_template('index.html', data=latest.head(10).to_html())

if __name__ == '__main__':
    app.run(debug=True)
