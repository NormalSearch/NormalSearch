from flask import Flask, render_template, request
import requests

app = Flask(name)

# Поиск в клирнете через Searx (публичный инстанс)
def search_clearweb(query):
    try:
        response = requests.get(
            "https://searx.be/search",
            params={
                "q": query,
                "format": "json",
                "language": "ru"
            },
            timeout=10
        ).json()
        return [{
            "title": r.get("title", "Без названия"),
            "url": r.get("url", "#"),
            "description": r.get("content", "Описание отсутствует")
        } for r in response.get("results", [])]
    except Exception as e:
        print(f"Ошибка Searx: {e}")
        return []

# Поиск в даркнете через DarkSearch.io
def search_darknet(query):
    try:
        response = requests.get(
            f"https://darksearch.io/api/search?query={query}",
            timeout=10
        ).json()
        return [{
            "title": r.get("title", "Без названия"),
            "url": r.get("link", "#"),
            "description": r.get("description", "Описание отсутствует")
        } for r in response.get("data", [])]
    except Exception as e:
        print(f"Ошибка DarkSearch: {e}")
        return []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    search_type = request.args.get("type", "clear")

    if not query:
        return render_template("index.html")

    results = search_darknet(query) if search_type == "onion" else search_clearweb(query)
    return render_template("results.html", query=query, results=results, search_type=search_type)

if name == "main":
    app.run(host="0.0.0.0", port=5000, debug=True)
