from flask import Blueprint, request, jsonify
from application.config import OPENAI_API_KEY, OPENAI_ENDPOINT
from application.constants import SYSTEM_PROMPT
import requests
import json

stock_analysis_api = Blueprint('stock_analysis_api', __name__)

@stock_analysis_api.route('/api/stock_analysis', methods=['POST'])
def stock_analysis():
    data = request.get_json()
    stock = data.get('stock')
    if not stock:
        return jsonify({'error': 'No stock provided'}), 400

    # Compose prompt for GPT
    prompt = f"""
    Provide a detailed analysis for the following stock:
    Stock Name: {stock.get('StockName')}
    Sector: {stock.get('Sector', 'N/A')}
    Exchange: {stock.get('Exchange', 'N/A')}
    Current Price: {stock.get('CurrentPrice', 'N/A')}
    Purchase Price: {stock.get('PurchasePrice', 'N/A')}
    Quantity: {stock.get('Quantity', 'N/A')}
    Purchase Date: {stock.get('PurchaseDate', 'N/A')}

    1. Give a summary of the stock and its recent performance.
    2. Advise if the stock is better for long-term or short-term holding, with reasoning based on current market trends.
    3. Comment on FII/DII (Foreign/ Domestic Institutional Investors) activity: are they buying or selling this stock?
    4. Add any other relevant analysis or advice for the user.
    Present the answer in a user-friendly, readable format.
    """

    payload = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 800
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    response = requests.post(OPENAI_ENDPOINT, headers=headers, json=payload)
    if response.status_code != 200:
        return jsonify({'error': 'OpenAI API error', 'details': response.text}), 500
    message = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
    return jsonify({'analysis': message})
