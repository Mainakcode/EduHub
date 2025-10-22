from flask import Flask, render_template, request
from googleapiclient.discovery import build
import re
import requests

app = Flask(__name__)

# 🔹 YouTube API Key
YOUTUBE_API_KEY = "AIzaSyATord7pvsQzJ7D-ySlUpMwHq2pc3es8BQ"

# 🔹 Google CSE API Key & Search Engine ID
GOOGLE_API_KEY = "AIzaSyCI_hiHNONAhvaVHuO47XfAXw-hEPjJ3gE"        # Replace with your CSE API key
GOOGLE_CSE_ID = "63c69e74a07a5420b"                 # Replace with your CSE ID

# ---------------------------------------------------------------
# 🔸 Function: Search YouTube Videos
# ---------------------------------------------------------------
def search_youtube(query, max_results=10):
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
# 🔸 Function: Search PDFs & Question Papers (Google CSE)
# ---------------------------------------------------------------
def search_google_pdfs(query, max_results=5):
    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    # Add filetype:pdf to query to get PDFs only
    query_pdf = f"{query} filetype:pdf"
    res = service.cse().list(q=query_pdf, cx=GOOGLE_CSE_ID, num=max_results).execute()

    pdfs = []
    qpapers = []

    for item in res.get('items', []):
        title = item.get('title')
        link = item.get('link')

        if not title or not link:
            continue

        # Identify Question Papers
        if any(word in title.lower() for word in ["question", "paper", "exam", "qp", "test"]):
            qpapers.append({"title": title, "link": link, "desc": "Question Paper"})
        else:
            pdfs.append({"title": title, "link": link, "desc": "PDF Document"})

    return pdfs, qpapers

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
    pdfs, qpapers = search_google_pdfs(query)
    videos = search_youtube(query)

    return render_template('results.html', query=query, pdfs=pdfs, qpapers=qpapers, videos=videos)

# ---------------------------------------------------------------
# 🔸 Main
# ---------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
