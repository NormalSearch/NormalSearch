from flask import Flask, render_template, request
import requests
import logging
from urllib.parse import quote
from bs4 import BeautifulSoup

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# User-Agent для обхода блокировок
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def search_clearweb(query):
    """Поиск через Ahmia (клирнет)"""
    try:
        url = f"https://ahmia.fi/search/?q={quote(query)}"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return parse_ahmia_results(response.text)
    except Exception as e:
        logging.error(f"Ahmia error: {str(e)}")
        return []

def parse_ahmia_results(html):
    """Парсинг результатов Ahmia"""
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    
    for result in soup.select('li.search-result'):
        title = result.select_one('h4')
        url = result.select_one('cite')
        desc = result.select_one('p')
        
        results.append({
            'title': title.get_text(strip=True) if title else 'Без названия',
            'url': url.get_text(strip=True) if url else '#',
            'description': desc.get_text(strip=True) if desc else 'Описание отсутствует'
        })
    
    return results[:10]  # Лимит результатов

def search_darknet(query):
    """Поиск через DarkSearch (даркнет)"""
    try:
        response = requests.get(
            "https://darksearch.io/api/search",
            params={'query': query},
            headers=HEADERS,
            timeout=10
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
    } for r in data.get('data', [])[:10]]

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
    app.run(host='0.0.0.0', port=5000, debug=True)
