import streamlit as st
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from starlette.requests import Request

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS engedélyezése (hogy a WordPress hívhassa az API-t)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WordPress API alap URL
BASE_API_URL = "https://sajatweboldal.hu/wp-json/wp/v2/posts"

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

# API végpont a chatbot számára
@app.get("/chatbot")
def chatbot_api(q: str = ""):
    user_query = q.lower()
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
        return {"message": "Nincs találat"}

    return results

# Streamlit felület
st.title("📖 WordPress Chatbot")
st.write("Kérdezz a weboldal tartalma alapján!")

user_input = st.text_input("Írd be a kérdésed...")

if user_input:
    st.write("🔎 Keresés folyamatban...")
    response = chatbot_api(user_input)
    if "message" in response:
        st.write("❌ Nincs találat")
    else:
        for res in response:
            st.write(f"📌 **[{res['title']}]({res['link']})**\n\n{res['excerpt']}...")
