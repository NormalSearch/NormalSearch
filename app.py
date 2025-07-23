from flask import Flask, render_template, request
import requests
import logging
from urllib.parse import quote

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Конфигурация DarkSearch
DARKSEARCH_API = "https://darksearch.io/api/search"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json'
}

def search_darknet(query):
    """Поиск через DarkSearch API"""
    try:
        response = requests.get(
            DARKSEARCH_API,
            params={
                'query': quote(query),
                'page': 1
            },
            headers=HEADERS,
            timeout=15  # Таймаут 15 секунд
        )
        response.raise_for_status()
        
        data = response.json()
        return [{
            'title': r.get('title', 'Без названия'),
            'url': r.get('link', '#'),
            'description': r.get('description', 'Описание отсутствует')
        } for r in data.get('data', [])[:10]]  # Первые 10 результатов
        
    except Exception as e:
        logging.error(f"DarkSearch error: {str(e)}")
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'clear')
    
    if search_type == 'onion':
        results = search_darknet(query)
    else:
        results = []  # Ваша реализация поиска в клирнете
    
    return render_template(
        'results.html',
        query=query,
        results=results or [],
        search_type=search_type
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
