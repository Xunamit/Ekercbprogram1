import streamlit as st
import requests
from bs4 import BeautifulSoup

# WordPress API URL (50 cikk lekérése, hogy több találat legyen)
WORDPRESS_API_URL = "https://sajatweboldal.hu/wp-json/wp/v2/posts?per_page=500"

# HTML eltávolítása a cikkekből
def clean_html(text):
    return BeautifulSoup(text, "html.parser").get_text()

# WordPress API lekérése
def get_wordpress_articles():
    try:
        response = requests.get(WORDPRESS_API_URL)
        if response.status_code == 200:
            return response.json()  # JSON formátumban visszaadja a cikkeket
        else:
            return []
    except Exception as e:
        st.error(f"Hiba történt a cikkek lekérésekor: {e}")
        return []

# Keresés a cikkekben
def search_articles(user_query, articles):
    results = []
    for article in articles:
        title = clean_html(article.get("title", {}).get("rendered", ""))
        content = clean_html(article.get("content", {}).get("rendered", ""))
        link = article.get("link", "")  # Cikk linkje

        # Pontozás: ha a keresett szó a címben van, nagyobb súlyt kap
        score = 0
        if user_query.lower() in title.lower():
            score += 2
        if user_query.lower() in content.lower():
            score += 1

        if score > 0:
            results.append((score, f"📌 **[{title}]({link})**\n\n{content[:300]}..."))  # Link és kivonat megjelenítése

    # A legrelevánsabb cikkek jelenjenek meg először
    results.sort(reverse=True, key=lambda x: x[0])

    return [res[1] for res in results] if results else ["❌ Nincs találat erre a kérdésre."]

# Streamlit alkalmazás felépítése
st.title("📖 WordPress Chatbot")
st.write("Kérdezz a weboldal tartalma alapján!")

# Felhasználói kérdés beírása
user_input = st.text_input("Írd be a kérdésed...")

if user_input:
    articles = get_wordpress_articles()
    search_results = search_articles(user_input, articles)
    for result in search_results:
        st.write(result)


