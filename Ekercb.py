import streamlit as st
import requests
from bs4 import BeautifulSoup
import difflib  # Rugalmas kereséshez

# WordPress API URL (több cikk lekérése)
WORDPRESS_API_URL = "https://www.egyenisegepites.hu/wp-json/wp/v2/posts?per_page=50"

# HTML eltávolítása
def clean_html(text):
    return BeautifulSoup(text, "html.parser").get_text()

# WordPress API lekérése
def get_wordpress_articles():
    try:
        response = requests.get(WORDPRESS_API_URL)
        if response.status_code == 200:
            articles = response.json()
            st.write(f"🔎 {len(articles)} cikk lett letöltve az API-ból.")  # Ellenőrzéshez
            return articles
        else:
            st.error(f"⚠️ Hiba az API lekérdezésénél: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"⚠️ Hiba történt: {e}")
        return []

# Rugalmas keresési logika
def search_articles(user_query, articles):
    results = []
    query_words = user_query.lower().split()  # A kérdést szavakra bontjuk
    
    for article in articles:
        title = clean_html(article.get("title", {}).get("rendered", ""))
        content = clean_html(article.get("content", {}).get("rendered", ""))
        link = article.get("link", "")

        # Szórészleges keresés
        match_score = sum(1 for word in query_words if word in title.lower() or word in content.lower())

        if match_score > 0:
            results.append((match_score, f"📌 **[{title}]({link})**\n\n{content[:300]}..."))

    # A legrelevánsabb cikkek legyenek elöl
    results.sort(reverse=True, key=lambda x: x[0])

    if not results:
        return ["❌ Nincs találat. Az első 5 cikk az adatbázisból:\n\n" + "\n".join(f"- {clean_html(a.get('title', {}).get('rendered', ''))}" for a in articles[:5])]

    return [res[1] for res in results]

# Streamlit alkalmazás
st.title("📖 WordPress Chatbot")
st.write("Kérdezz a weboldal tartalma alapján!")

user_input = st.text_input("Írd be a kérdésed...")

if user_input:
    articles = get_wordpress_articles()
    search_results = search_articles(user_input, articles)
    for result in search_results:
        st.write(result)
