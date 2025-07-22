from flask import Flask, render_template, request
import requests
import logging
from urllib.parse import quote

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Проверенные рабочие инстансы Searx (с ротацией)
SEARX_INSTANCES = [
    "https://search.us.projectsegfau.lt",
    "https://searx.work",
    "https://searx.smnz.de"
]

# User-Agent для обхода блокировок
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def search_clearweb(query):
    encoded_query = quote(query)
    for instance in SEARX_INSTANCES:
        try:
            url = f"{instance}/search?q={encoded_query}&format=json&language=ru"
            response = requests.get(url, headers=HEADERS, timeout=5)
            response.raise_for_status()
            return parse_searx_results(response.json())
        except Exception as e:
            logging.error(f"Searx error ({instance}): {str(e)}")
    return []

def parse_searx_results(data):
    return [{
        'title': r.get('title', 'Без названия'),
        'url': r.get('url', '#'),
        'description': r.get('content', 'Описание отсутствует')
    } for r in data.get('results', [])[:10]]  # Лимит результатов

def search_darknet(query):
    try:
        response = requests.get(
            "https://darksearch.io/api/search",
            params={'query': query},
            timeout=5
        )
        response.raise_for_status()
        return parse_darksearch_results(response.json())
    except Exception as e:
        logging.error(f"DarkSearch error: {str(e)}")
        return []

def parse_darksearch_results(data):
    return [{
        'title': r.get('title', 'Без названия'),
        'url': r.get('link', '#'),
        'description': r.get('description', 'Описание отсутствует')
    } for r in data.get('data', [])[:10]]  # Лимит результатов

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return render_template('index.html')
    
    search_type = request.args.get('type', 'clear')
    results = search_darknet(query) if search_type == 'onion' else search_clearweb(query)
    
    return render_template(
        'results.html',
        query=query,
        results=results or [],
        search_type=search_type
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
