import streamlit as st
import requests
from bs4 import BeautifulSoup

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
                break  # Ha nincs több cikk, leállunk
            articles.extend(new_articles)
        else:
            st.error(f"⚠️ Hiba az API lekérdezésénél: {response.status_code}")
            break  # Ha hiba van, ne próbálkozzon tovább
        
    st.write(f"🔎 Összesen {len(articles)} cikk lett letöltve az API-ból.")  
    return articles

# Keresési logika - teljes kifejezés előnyben!
def search_articles(user_query, articles):
    results = []
    query_lower = user_query.lower()

    for article in articles:
        title = clean_html(article.get("title", {}).get("rendered", ""))
        content = clean_html(article.get("content", {}).get("rendered", ""))
        link = article.get("link", "")

        score = 0

        # **Teljes kifejezés előnyben**
        if query_lower in title.lower():
            score += 5  # Ha a teljes keresett kifejezés a címben szerepel, az kiemelt prioritású
        elif query_lower in content.lower():
            score += 3  # Ha a teljes kifejezés a tartalomban szerepel, az közepes prioritású
        
        # **Ha egyes szavak külön szerepelnek, kisebb pontszám**
        elif any(word in title.lower() for word in query_lower.split()):
            score += 2  
        elif any(word in content.lower() for word in query_lower.split()):
            score += 1  

        if score > 0:
            results.append((score, f"📌 **[{title}]({link})**\n\n{content[:300]}..."))

    results.sort(reverse=True, key=lambda x: x[0])
    results = results[:5]  # Max. 5 releváns találat

    return [res[1] for res in results] if results else ["❌ Nincs találat a keresett témában."]

# Streamlit alkalmazás
st.title("📖 WordPress Chatbot")
st.write("Kérdezz a weboldal tartalma alapján!")

user_input = st.text_input("Írd be a kérdésed...")

if user_input:
    articles = get_all_articles(max_pages=5, per_page=50)  # 5x50 = max. 250 cikket keres át
    search_results = search_articles(user_input, articles)
    for result in search_results:
        st.write(result)

