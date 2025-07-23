from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import quote

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Конфигурация Ahmia
AHMIA_URL = "https://ahmia.fi/search/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'en-US,en;q=0.5'
}

def search_darknet(query):
    """Поиск через Ahmia.fi с улучшенным парсингом"""
    try:
        # Формируем URL запроса
        search_url = f"{AHMIA_URL}?q={quote(query)}"
        logging.info(f"Requesting: {search_url}")
        
        response = requests.get(search_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        
        # Парсим HTML-ответ
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        for result in soup.select('li.search-result'):
            try:
                title = result.select_one('h4').get_text(strip=True)
                url = result.select_one('cite').get_text(strip=True)
                desc = result.select_one('p').get_text(strip=True)
                
                # Фильтруем только .onion сайты
                if '.onion' in url.lower():
                    results.append({
                        'title': title or 'Без названия',
                        'url': url or '#',
                        'description': desc or 'Описание отсутствует'
                    })
            except Exception as e:
                logging.warning(f"Error parsing result: {str(e)}")
                continue
        
        return results[:15]  # Ограничиваем количество результатов
        
    except Exception as e:
        logging.error(f"Ahmia search error: {str(e)}", exc_info=True)
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
        if not results:
            return render_template(
                'results.html',
                query=query,
                error="Не удалось найти .onion сайты по вашему запросу",
                search_type=search_type
            )
    else:
        results = []  # Здесь можно добавить поиск по клирнету
    
    return render_template(
        'results.html',
        query=query,
        results=results,
        search_type=search_type
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
