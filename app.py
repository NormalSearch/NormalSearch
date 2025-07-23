from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import quote

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Конфигурация
SEARX_INSTANCES = [
    "https://searx.space",
    "https://searx.nixnet.services",
    "https://search.garudalinux.org"
]

TOR_PROXIES = {
    'http': 'socks5h://localhost:9050',
    'https': 'socks5h://localhost:9050'
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def search_clearweb(query):
    """Поиск через Searx (клирнет)"""
    encoded_query = quote(query)
    for instance in SEARX_INSTANCES:
        try:
            url = f"{instance}/search?q={encoded_query}&format=json&language=ru"
            response = requests.get(url, headers=HEADERS, timeout=10)
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
    } for r in data.get('results', [])[:10]]

def search_darknet(query):
    """Поиск через Torch (даркнет)"""
    try:
        url = f"http://xmh57jrzrnw6insl.onion/search?query={quote(query)}"
        response = requests.get(url, proxies=TOR_PROXIES, timeout=30)
        response.raise_for_status()
        return parse_torch_results(response.text)
    except Exception as e:
        logging.error(f"Torch error: {str(e)}")
        return []

def parse_torch_results(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    for result in soup.select('div.result'):
        results.append({
            'title': result.select_one('h4').get_text(strip=True) if result.select_one('h4') else 'Без названия',
            'url': result.select_one('cite').get_text(strip=True) if result.select_one('cite') else '#',
            'description': result.select_one('p').get_text(strip=True) if result.select_one('p') else 'Описание отсутствует'
        })
    return results[:15]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
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
