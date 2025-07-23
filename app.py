import requests
from flask import Flask, render_template, request, redirect
import urllib.parse

app = Flask(__name__)

# Конфигурация поисковиков
SEARCH_APIS = {
    "duckduckgo": "https://api.duckduckgo.com/?q={query}&format=json&no_html=1",
    "ahmia": "https://ahmia.fi/search/?q={query}",
    "darksearch": "https://darksearch.io/api/search?query={query}&page=1",
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    engine = request.args.get('engine', 'ahmia')
    
    if not query:
        return redirect('/')
    
    results = []
    
    try:
        if engine == 'darksearch':
            response = requests.get(SEARCH_APIS[engine].format(query=query))
            data = response.json()
            results = [{
                'title': item.get('title', 'Без названия'),
                'link': item.get('link', '#'),
                'description': item.get('description', 'Нет описания')
            } for item in data.get('data', [])[:10]]
        
        elif engine == 'duckduckgo':
            response = requests.get(SEARCH_APIS[engine].format(query=query))
            data = response.json()
            results = [{
                'title': item.get('Text', ''),
                'link': item.get('FirstURL', ''),
                'description': item.get('Result', '')
            } for item in data.get('RelatedTopics', []) if 'FirstURL' in item][:10]
        
        else:  # Ahmia (пример без реального парсинга)
            results = [{
                'title': f"Onion сайт #{i}",
                'link': f"http://example{i}.onion",
                'description': f"Результат {i} для '{query}'"
            } for i in range(1, 11)]
    
    except Exception as e:
        print(f"Ошибка: {e}")
    
    return render_template('search.html', 
                         query=query, 
                         results=results, 
                         engine=engine)

if __name__ == '__main__':
    app.run(debug=True)
