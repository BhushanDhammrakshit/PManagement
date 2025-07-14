import datetime
import requests
from bs4 import BeautifulSoup
from flask import Blueprint, render_template
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import re

tendor_api = Blueprint('tendor_api', __name__)

# ---------- ETenders (using Selenium) ----------
def fetch_etenders():
    url = "https://etenders.gov.in/eprocure/app?page=FrontEndLatestActiveTenders"
    tenders = []
    one_week_ago = datetime.datetime.now() - datetime.timedelta(days=7)

    try:
        print(f"\n[ETENDERS] Launching browser for: {url}")
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(options=options)
        driver.get(url)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()

        rows = soup.select('table[class*="table"] tbody tr')
        print(f"[ETENDERS] Found {len(rows)} rows in table")

        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 5:
                title = cols[0].get_text(strip=True)
                org = cols[1].get_text(strip=True)
                end_date_str = cols[4].get_text(strip=True)

                # Skip headers mistakenly read as data
                if "bid opening" in end_date_str.lower():
                    continue

                # Remove time if present (e.g., "12-Jul-2025 12:30 PM" → "12-Jul-2025")
                end_date_clean = end_date_str.split()[0]

                try:
                    end_date = datetime.datetime.strptime(end_date_clean, "%d-%b-%Y")
                    if end_date >= one_week_ago:
                        tenders.append({
                            "title": title,
                            "org": org,
                            "end_date": end_date_str
                        })
                except Exception as e:
                    print(f"[ETENDERS] Date error: {e}")
        print(f"[ETENDERS] Collected {len(tenders)} recent tenders")
    except Exception as e:
        print(f"[ETENDERS] Error: {e}")
    return tenders


# ---------- BSE Announcements ----------
def fetch_bse_announcements():
    url = "https://api.bseindia.com/BseIndiaAPI/api/AnnGetData/w?strCat=-1&strPrevDate=&strScrip=&strSearch=project order contract agreement award tender&strToDate=&strType=search"
    announcements = []
    one_week_ago = datetime.datetime.now() - datetime.timedelta(days=7)

    try:
        print(f"\n[BSE] Requesting: {url}")
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, timeout=10)

        # Fix for bad JSON (BSE sometimes returns invalid JS prefix or garbage lines)
        text = response.text.strip()

        # Extract only the JSON body
        json_match = re.search(r'(\{.*\})', text, re.DOTALL)
        if not json_match:
            print("[BSE] Could not extract valid JSON")
            return []

        json_data = json.loads(json_match.group(1))
        data = json_data.get("Table", [])
        print(f"[BSE] Received {len(data)} records")

        for item in data:
            try:
                ann_date = datetime.datetime.strptime(item["NEWS_DT"], "%d %b %Y")
                if ann_date >= one_week_ago:
                    announcements.append({
                        "title": item["NEWS_SUB"],
                        "org": item["SCRIP_CD"],
                        "end_date": item["NEWS_DT"],
                        "link": item.get("ATTACHMENTNAME", "")
                    })
            except Exception as e:
                print(f"[BSE] Date parse error: {e}")
        print(f"[BSE] Collected {len(announcements)} recent announcements")
    except Exception as e:
        print(f"[BSE] Error: {e}")

    return announcements


# ---------- Flask Route ----------
@tendor_api.route('/tendors')
def show_tendors():
    etenders = fetch_etenders()
    bse_announcements = fetch_bse_announcements()
    all_tendors = etenders + bse_announcements

    print(f"\n[SUMMARY] Total tenders: {len(all_tendors)}")
    for t in all_tendors:
        print(f"- {t['title']} | {t['org']} | {t['end_date']}")
    return render_template('tendors.html', tendors=all_tendors)
