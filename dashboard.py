from flask import Flask, render_template
import pandas as pd
import glob

app = Flask(__name__)

@app.route('/')
def dashboard():
    csvs = glob.glob('reports/*.csv')
    latest = pd.read_csv(max(csvs, key=lambda x: pd.to_datetime(x.split('_')[-1].split('.')[0])))
    return render_template('index.html', data=latest.head(10).to_html())

if __name__ == '__main__':
    app.run(debug=True)
