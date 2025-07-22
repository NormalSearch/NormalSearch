from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import quote

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Конфигурация Tor (если нужно использовать прокси)
TOR_PROXIES = {
    'http': 'socks5h://localhost:9050',
    'https': 'socks5h://localhost:9050'
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def search_clearweb(query):
    """Поиск в клирнете через Google Custom Search API"""
    # Здесь должна быть ваша реализация поиска в клирнете
    # Например, через Google API или другой сервис
    return []

def search_darknet(query):
    """Поиск в даркнете через Torch"""
    try:
        # URL Torch (работает только через Tor)
        url = f"http://xmh57jrzrnw6insl.onion/search?query={quote(query)}"
        
        # Запрос через Tor-прокси (должен быть запущен локально)
        response = requests.get(
            url,
            proxies=TOR_PROXIES,
            headers=HEADERS,
            timeout=30  # Увеличенный таймаут для Tor
        )
        response.raise_for_status()
        
        return parse_torch_results(response.text)
    except Exception as e:
        logging.error(f"Torch search error: {str(e)}")
        return []

def parse_torch_results(html):
    """Парсинг HTML-страницы Torch"""
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    
    for result in soup.select('div.result'):
        title = result.select_one('h4')
        url = result.select_one('cite')
        desc = result.select_one('p')
        
        results.append({
            'title': title.get_text(strip=True) if title else 'Без названия',
            'url': url.get_text(strip=True) if url else '#',
            'description': desc.get_text(strip=True) if desc else 'Описание отсутствует'
        })
    
    return results[:15]  # Лимит результатов

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return render_template('index.html')
    
    search_type = request.args.get('type', 'clear')
    
    if search_type == 'onion':
        results = search_darknet(query)
    else:
        results = search_clearweb(query)
    
    return render_template(
        'results.html',
        query=query,
        results=results or [],
        search_type=search_type
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
