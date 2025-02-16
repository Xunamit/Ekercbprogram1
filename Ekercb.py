import streamlit as st
import requests
from bs4 import BeautifulSoup
import json

from flask import Flask, request, jsonify

app = Flask(__name__)

# WordPress API alap URL
BASE_API_URL = "https://www.egyenisegepites.hu/wp-json/wp/v2/posts"

# HTML eltávolítása
def clean_html(text):
    return BeautifulSoup(text, "html.parser").get_text()

# Több cikk lekérése lapozással
def get_all_articles(max_pages=5, per_page=50):
    articles = []
    for page in range(1, max_pages + 1):
        api_url = f"{BASE_API_URL}?per_page={per_page}&page={page}"
        response = requests.get(api_url)
        
        if response.status_code == 200:
            new_articles = response.json()
            if not new_articles:
                break
            articles.extend(new_articles)
        else:
            return []
    return articles

# Keresési funkció API számára
@app.route("/chatbot", methods=["GET"])
def chatbot_api():
    user_query = request.args.get("q", "").lower()
    articles = get_all_articles()
    results = []

    for article in articles:
        title = clean_html(article.get("title", {}).get("rendered", ""))
        content = clean_html(article.get("content", {}).get("rendered", ""))
        link = article.get("link", "")

        score = 0
        if user_query in title.lower():
            score += 5
        elif user_query in content.lower():
            score += 3
        
        if score > 0:
            results.append({"title": title, "link": link, "excerpt": content[:300]})

    if not results:
        return jsonify({"message": "Nincs találat"}), 404

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)

        
