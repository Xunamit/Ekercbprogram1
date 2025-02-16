import streamlit as st
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

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
BASE_API_URL = "https://www.egyenisegepites.hu/wp-json/wp/v2/posts"

# HTML eltávolítása
def clean_html(text):
    return BeautifulSoup(text, "html.parser").get_text()

# Több cikk lekérése lapozással
def get_all_articles(max_pages=5, per_page=50):
    articles = []
    for page in range(1, max_pages + 1):
        api_url = f"{BASE_API_URL}?per_page={per_page}&page={page}"
        
        try:
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()  # Ha hiba van, azonnal kivételt dob
            
            new_articles = response.json()
            if not new_articles:
                break  
            articles.extend(new_articles)

        except requests.exceptions.RequestException as e:
            st.error(f"⚠️ API kapcsolat hiba: {e}")
            return []

    st.write(f"🔎 {len(articles)} cikk sikeresen betöltve.")
    return articles

# API végpont a chatbot számára
@app.get("/chatbot")
def chatbot_api(q: str = ""):
    user_query = q.lower()
    articles = get_all_articles()
    
    if not articles:
        return {"message": "Hiba történt a cikkek letöltésekor."}

    results = []
    for article in articles:
        title = clean_html(article.get("title", {}).get("rendered", ""))
        content = clean_html(article.get("content", {}).get("rendered", ""))
        link = article.get("link", "")

        score = 0

        # **Ha a keresett szó a cím elején szerepel, kiemelt prioritás**
        if title.lower().startswith(user_query):
            score += 5  
        
        # **Ha a keresett szó teljes egyezéssel szerepel a címben**
        elif user_query in title.lower():
            score += 4  

        # **Ha a keresett szó szerepel a tartalomban**
        elif user_query in content.lower():
            score += 2  

        # **Ha egyes szavak külön szerepelnek, kisebb pontszám**
        elif any(word in title.lower() for word in user_query.split()):
            score += 2  
        elif any(word in content.lower() for word in user_query.split()):
            score += 1  

        if score > 0:
            results.append({"title": title, "link": link, "excerpt": content[:300]})

    return results if results else {"message": "Nincs találat"}

# Streamlit felület
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
