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

tendor_api = Blueprint('tendor_api', __name__)

import requests
from bs4 import BeautifulSoup
import re
import json

def escape_markdown_v2(text):
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(r"([" + re.escape(escape_chars) + r"])", r"\\\1", text)

def fetch_stock_news_summary():
    url = "https://economictimes.indiatimes.com/markets/stocks/news"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to fetch news HTML. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    mid_section = soup.find(class_="clearfix main_container")

    if not mid_section:
        print("❌ No 'main_container' section found.")
        return []

    text_content = mid_section.get_text(separator="\n", strip=True)

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

    ai_response = requests.post(openai_endpoint, headers=headers, json=payload)

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
@tendor_api.route('/tendors')
def show_stock_news():
    stock_data = fetch_stock_news_summary()
    return render_template('tendors.html', stocks=stock_data)


