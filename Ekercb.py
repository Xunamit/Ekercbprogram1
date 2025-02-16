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
    query_lower = user_query.lower()

    for article in articles:
        title = clean_html(article.get("title", {}).get("rendered", ""))
        content = clean_html(article.get("content", {}).get("rendered", ""))
        link = article.get("link", "")

        score = 0  # Kezdő pontszám

        # **Legfontosabb: ha a teljes keresett kifejezés szerepel a címben, akkor kiemelt prioritás**
        if query_lower in title.lower():
            score += 5  # Nagyon magas prioritás

        # **Ha a keresett szó a címben szerepel, de nem pontos egyezéssel**
        elif any(word in title.lower() for word in query_lower.split()):
            score += 3  

        # **Ha csak a cikk tartalmában fordul elő, de nem a címben, akkor kisebb pontszám**
        elif query_lower in content.lower():
            score += 1  

        # Ha van relevancia, hozzáadjuk az eredményekhez
        if score > 0:
            results.append((score, f"📌 **[{title}]({link})**\n\n{content[:300]}..."))

    # **Csak a legjobb 5 találatot jelenítsük meg**
    results.sort(reverse=True, key=lambda x: x[0])
    results = results[:5]

    return [res[1] for res in results] if results else ["❌ Nincs találat a keresett témában."]


# Streamlit alkalmazás
st.title("📖 WordPress Chatbot")
st.write("Kérdezz a weboldal tartalma alapján!")

user_input = st.text_input("Írd be a kérdésed...")

if user_input:
    articles = get_wordpress_articles()
    search_results = search_articles(user_input, articles)
    for result in search_results:
        st.write(result)
