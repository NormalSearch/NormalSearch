from flask import Flask, render_template, request
import requests
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Важно: двойное подчёркивание в __name__
app = Flask(__name__)

# Конфигурация для Searx (публичные инстансы)
SEARX_INSTANCES = [
    "https://search.us.projectsegfau.lt"
    "https://searx.work"
    "https://searx.smnz.de"
]

def search_clearweb(query):
    for instance in SEARX_INSTANCES:
        try:
            response = requests.get(
                f"{instance}/search",
                params={
                    "q": query,
                    "format": "json",
                    "language": "ru"
                },
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            return [{
                "title": r.get("title", "Без названия"),
                "url": r.get("url", "#"),
                "description": r.get("content", "Описание отсутствует")
            } for r in data.get("results", [])]
        except Exception as e:
            logger.error(f"Ошибка в Searx ({instance}): {str(e)}")
    return []

def search_darknet(query):
    try:
        response = requests.get(
            "https://darksearch.io/api/search",
            params={"query": query},
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        return [{
            "title": r.get("title", "Без названия"),
            "url": r.get("link", "#"),
            "description": r.get("description", "Описание отсутствует")
        } for r in data.get("data", [])]
    except Exception as e:
        logger.error(f"Ошибка в DarkSearch: {str(e)}")
        return []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return render_template("index.html")
    
    search_type = request.args.get("type", "clear")
    results = search_darknet(query) if search_type == "onion" else search_clearweb(query)
    
    return render_template(
        "results.html",
        query=query,
        results=results,
        search_type=search_type
    )

# Важно: двойное подчёркивание в __name__
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
