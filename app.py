from flask import Flask, render_template, request
from googleapiclient.discovery import build
from duckduckgo_search import DDGS
import re

app = Flask(__name__)

# 🔹 YouTube API Key
YOUTUBE_API_KEY = "AIzaSyATord7pvsQzJ7D-ySlUpMwHq2pc3es8BQ"

# ---------------------------------------------------------------
# 🔸 Function: Search YouTube Videos
# ---------------------------------------------------------------
def search_youtube(query, max_results=5):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    request_youtube = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=max_results
    )
    response = request_youtube.execute()
    videos = []
    for item in response.get('items', []):
        videos.append({
            'title': item['snippet']['title'],
            'link': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
            'thumb': item['snippet']['thumbnails']['high']['url']
        })
    return videos

# ---------------------------------------------------------------
# 🔸 Function: Search PDFs & Question Papers (DuckDuckGo)
# ---------------------------------------------------------------
def search_duckduckgo_pdfs(query, max_results=10):
    ddgs = DDGS()
    results = list(ddgs.text(f"{query} filetype:pdf", max_results=max_results * 2))
    
    pdfs = []
    qpapers = []
    seen = set()

    for r in results:
        link = r.get("href", "")
        title = r.get("title", "")
        if not link or not title:
            continue
        if link in seen:
            continue
        seen.add(link)

        # Check if link is PDF
        if link.lower().endswith(".pdf") or "pdf" in link.lower():
            # Identify Question Papers
           if link.lower().endswith(".pdf") or ("pdf" in link.lower() and any(word in title.lower() for word in ["question", "paper", "exam", "qp", "test"])):
    # Decide if it's a question paper or regular PDF
            if any(word in title.lower() for word in ["question", "paper", "exam", "qp", "test"]):
             qpapers.append({"title": title, "link": link, "desc": "Question Paper"})
            pdfs.append({"title": title, "link": link, "desc": "PDF Document"})

        # Stop early if we have enough results
        if len(pdfs) >= max_results and len(qpapers) >= max_results:
            break

    return pdfs[:max_results], qpapers[:max_results]

# ---------------------------------------------------------------
# 🔸 Routes
# ---------------------------------------------------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/results')
def results():
    query = request.args.get('query')
    if not query:
        return "Please provide a search query."

    # Search PDFs, Question Papers, and YouTube Videos
    pdfs, qpapers = search_duckduckgo_pdfs(query)
    videos = search_youtube(query)

    return render_template('results.html', query=query, pdfs=pdfs, qpapers=qpapers, videos=videos)

# ---------------------------------------------------------------
# 🔸 Main
# ---------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
