import yfinance as yf
from flask import Blueprint, render_template, jsonify

heatmap_bp = Blueprint('heatmap', __name__)

# Nifty 50 and Bank Nifty symbols (partial for brevity, add all as needed)
NIFTY_50 = [
    "RELIANCE.NS",    "TCS.NS",    "INFY.NS",    "HCLTECH.NS",    "LT.NS",    "ITC.NS",    "BHARTIARTL.NS",    "ASIANPAINT.NS",    "BAJFINANCE.NS",
    "HINDUNILVR.NS",    "MARUTI.NS",    "TITAN.NS",    "ULTRACEMCO.NS",    "SUNPHARMA.NS",    "WIPRO.NS",    "BAJAJ-AUTO.NS",    "BAJAJFINSV.NS",
    "BHARATELEC.NS",    "CIPLA.NS",    "COALINDIA.NS",    "DRREDDY.NS",    "EICHERMOT.NS",    "ETERNAL.NS",    "GRASIM.NS",    "HEROMOTOCO.NS",    "HINDALCO.NS",
    "JIOFIN.NS",    "JSWSTEEL.NS",    "M&M.NS",    "NESTLEIND.NS",    "NTPC.NS",    "ONGC.NS",    "POWERGRID.NS",    "RELIANCE.NS",    "SBILIFE.NS",
    "SHRIRAMFIN.NS",    "TATACONSUM.NS",    "TATAMOTORS.NS",    "TATASTEEL.NS",    "TECHM.NS",    "TRENT.NS"
]

BANK_NIFTY = [
    "HDFCBANK.NS", "ICICIBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "AXISBANK.NS", "BANKBARODA.NS", "PNB.NS", "IDFCFIRSTB.NS", "FEDERALBNK.NS", "AUBANK.NS"
]


def get_stock_data(symbols):
    stock_data = []
    for symbol in symbols:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        try:
            change = round(info["regularMarketChangePercent"], 2)
            price = info["regularMarketPrice"]
            name = info["shortName"]
            sector = info.get("sector", "Other")
            logo_url = info.get("logo_url") or info.get("logoUrl")
        except KeyError:
            continue  # skip if data is missing
        stock_data.append({
            "name": name,
            "symbol": symbol,
            "price": price,
            "change": change,
            "sector": sector,
            "logo": logo_url
        })
    return stock_data

@heatmap_bp.route("/heatmap-data")
def heatmap_data():
    nifty_data = get_stock_data(NIFTY_50)
    banknifty_data = get_stock_data(BANK_NIFTY)
    return jsonify({"nifty": nifty_data, "banknifty": banknifty_data})

@heatmap_bp.route("/heatmap")
def heatmap():
    return render_template("heatmap.html")
