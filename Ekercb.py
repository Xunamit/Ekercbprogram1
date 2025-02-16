import requests
import streamlit as st
from bs4 import BeautifulSoup
from fastapi import FastAPI

app = FastAPI()

BASE_API_URL = "https://www.egyenisegepites.hu/wp-json/wp/v2/posts"

def clean_html(text):
    return BeautifulSoup(text, "html.parser").get_text()

def search_articles(user_query, articles):
    results = []
    query_lower = user_query.lower()

    for article in articles:
        title = clean_html(article.get("title", {}).get("rendered", ""))
        content = clean_html(article.get("content", {}).get("rendered", ""))
        link = article.get("link", "")

        score = 0

        # **Ha a keresett szó a cím elején szerepel, kiemelt prioritás**
        if title.lower().startswith(query_lower):
            score += 5  
        
        # **Ha a keresett szó teljes egyezéssel szerepel a címben**
        elif query_lower in title.lower():
            score += 4  

        # **Ha a keresett szó szerepel a tartalomban**
        elif query_lower in content.lower():
            score += 2  

        # **Ha egyes szavak külön szerepelnek, kisebb pontszám**
        elif any(word in title.lower() for word in query_lower.split()):
            score += 2  
        elif any(word in content.lower() for word in query_lower.split()):
            score += 1  

        if score > 0:
            results.append((score, f"📌 **[{title}]({link})**\n\n{content[:300]}..."))

    # **Legalább 5 találatot adjon vissza, ha van ennyi**
    results.sort(reverse=True, key=lambda x: x[0])
    results = results[:5]  

    return [res[1] for res in results] if results else ["❌ Nincs találat a keresett témában."]


st.title("📖 WordPress Chatbot")
st.write("Kérdezz a weboldal tartalma alapján!")

user_input = st.text_input("Írd be a kérdésed...")

if user_input:
    articles = get_all_articles()
    if not articles:
        st.write("⚠️ Nem sikerült lekérni a cikkeket.")
    else:
        response = chatbot_api(user_input)
        if "message" in response:
            st.write(f"❌ {response['message']}")
        else:
            for res in response:
                st.write(f"📌 **[{res['title']}]({res['link']})**\n\n{res['excerpt']}...")



