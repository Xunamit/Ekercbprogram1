import streamlit as st
import requests

# WordPress weboldal URL-je (a "/wp-json/wp/v2/posts" végpont a cikkek lekérdezéséhez)
WORDPRESS_API_URL = "https://www.egyenisegepites.hu/wp-json/wp/v2/posts"

# WordPress API-ból cikkek lekérése
def get_wordpress_articles():
    response = requests.get(WORDPRESS_API_URL)
    if response.status_code == 200:
        return response.json()  # JSON formátumban visszaadja a cikkeket
    else:
        return []

# Keresés a cikkekben a felhasználó kérdése alapján
def search_articles(user_query, articles):
    relevant_articles = []
    for article in articles:
        title = article.get("title", {}).get("rendered", "")
        content = article.get("content", {}).get("rendered", "")
        
        if user_query.lower() in content.lower() or user_query.lower() in title.lower():
            relevant_articles.append(f"**{title}**\n\n{content[:300]}...")  # Az első 300 karaktert jeleníti meg
        
    return relevant_articles if relevant_articles else ["Nincs találat a kérdésedre."]

# Streamlit felület
st.title("📖 WordPress Chatbot")
st.write("Kérdezz bármit a weboldal tartalma alapján!")

user_input = st.text_input("Írd be a kérdésed...")

if user_input:
    articles = get_wordpress_articles()
    search_results = search_articles(user_input, articles)
    for result in search_results:
        st.write(result)

from bs4 import BeautifulSoup

def clean_html(text):
    return BeautifulSoup(text, "html.parser").get_text()

def search_articles(user_query, articles):
    relevant_articles = []
    for article in articles:
        title = clean_html(article.get("title", {}).get("rendered", ""))
        content = clean_html(article.get("content", {}).get("rendered", ""))
        
        if user_query.lower() in content.lower() or user_query.lower() in title.lower():
            relevant_articles.append(f"**{title}**\n\n{content[:300]}...")  # Az első 300 karaktert jeleníti meg
        
    return relevant_articles if relevant_articles else ["Nincs találat a kérdésedre."]

def search_articles(user_query, articles):
    results = []
    for article in articles:
        title = clean_html(article.get("title", {}).get("rendered", ""))
        content = clean_html(article.get("content", {}).get("rendered", ""))
        
        # Pontozás: ha a keresett szó a címben van, nagyobb súlyt kap
        score = 0
        if user_query.lower() in title.lower():
            score += 2
        if user_query.lower() in content.lower():
            score += 1
        
        if score > 0:
            results.append((score, f"**{title}**\n\n{content[:300]}..."))

    # A legrelevánsabb cikkek jelenjenek meg először
    results.sort(reverse=True, key=lambda x: x[0])
    
    return [res[1] for res in results] if results else ["Nincs találat a kérdésedre."]

