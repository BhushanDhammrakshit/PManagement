import datetime
import requests
from bs4 import BeautifulSoup
from flask import Blueprint, render_template
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import re
from application.constants import SYSTEM_PROMPT
from application.config import OPENAI_API_KEY, OPENAI_ENDPOINT
import requests
from bs4 import BeautifulSoup
import re
import json

# Simple in-memory cache for stock summaries
_stock_summary_cache = {
    'data': None,
    'timestamp': None
}

CACHE_EXPIRY_SECONDS = 3600  # 1 hour

tender_api = Blueprint('tendor_api', __name__)

# Function to get cached stock summary
# This is a simple in-memory cache.
def get_cached_stock_summary():
    now = datetime.datetime.utcnow()
    if (
        _stock_summary_cache['data'] is not None and
        _stock_summary_cache['timestamp'] is not None and
        (now - _stock_summary_cache['timestamp']).total_seconds() < CACHE_EXPIRY_SECONDS
    ):
        return _stock_summary_cache['data']
    return None

# Function to set cached stock summary 
def set_cached_stock_summary(data):
    _stock_summary_cache['data'] = data
    _stock_summary_cache['timestamp'] = datetime.datetime.utcnow()

# Function to escape markdown characters
# This is used to ensure that the text is safe for rendering in HTML.
def escape_markdown_v2(text):
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(r"([" + re.escape(escape_chars) + r"])", r"\\\1", text)

# Function to fetch stock news summary, using cache if available.
# This function fetches the stock news, processes it, and returns a summary.
def fetch_stock_news_summary():

    cached = get_cached_stock_summary()
    if cached is not None:
        return cached
    summary_rows = fetch_and_parse_stock_news()
    set_cached_stock_summary(summary_rows)
    return summary_rows

# Function to fetch data from the website
# This function fetches the HTML content from the stock news website.
def fetch_data_from_website():

    url = "https://economictimes.indiatimes.com/markets/stocks/news"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to fetch news HTML. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    mid_section = soup.find(class_="clearfix main_container")

    if not mid_section:
        print("❌ No 'main_container' section found.")
        return None

    text_content = mid_section.get_text(separator="\n", strip=True)
    return text_content

# Function to generate OpenAI response
# This function creates the payload for OpenAI API.
def generate_openAI_response(text_content):
    # OpenAI API call
    openai_api_key = OPENAI_API_KEY
    openai_endpoint = OPENAI_ENDPOINT
    system_prompt = SYSTEM_PROMPT

    payload = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text_content}
        ],
        "temperature": 0.7,
        "max_tokens": 1500
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }

    return requests.post(openai_endpoint, headers=headers, json=payload)

# Function to fetch and parse stock news
# This function fetches the stock news, processes it, and returns a summary.
def fetch_and_parse_stock_news():

    text_content = fetch_data_from_website()
    if not text_content:
        return []

    ai_response = generate_openAI_response(text_content) 

    if ai_response.status_code != 200:
        print("❌ OpenAI API error:", ai_response.status_code, ai_response.text)
        return []

    message = ai_response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
    print("✅ Fetched OpenAI Summary\n", message)

    try:
        parsed_data = json.loads(message)
    except json.JSONDecodeError as e:
        print("❌ JSON parse error:", e)
        return []

    summary_rows = []
    for item in parsed_data:
        if all(k in item for k in ["stock", "classification", "reason"]):
            summary_rows.append({
                "stock": item["stock"],
                "sentiment": item["classification"].lower(),
                "summary": item["reason"]
            })
    return summary_rows


# ---------- Flask Route ----------
@tender_api.route('/tenders')
def show_stock_news():
    stock_data = fetch_stock_news_summary()
    return render_template('tenders.html', stocks=stock_data)


