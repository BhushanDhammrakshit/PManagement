from flask import Blueprint, jsonify
from application.services.azure_table import get_user_by_row_key, get_user_stocks_by_row_key

user_blueprint = Blueprint("user", __name__)


@user_blueprint.route('/user/<string:userid>', methods=['GET'])
def get_user_profile_and_stocks(userid):
    """
    Retrieves user profile and stock holdings
    """
    try:
        user_entity = get_user_by_row_key(userid)
        user_stocks = get_user_stocks_by_row_key(userid)
        print(user_entity)
        print(user_stocks)
        stocks = []
        for stock in user_stocks:
            stocks.append({
                "StockName": stock.get("StockName"),
                "Quantity": stock.get("Quantity"),
                "PurchasePrice": stock.get("PurchasePrice"),
                "PurchaseDate": stock.get("PurchaseDate"),
                "Exchange": stock.get("Exchange"),
                "Sector": stock.get("Sector"),
            })
        
        return jsonify({
            "user": {
                "name": user_entity.get("UserName"),
                "email": user_entity.get("Email"),
                "phone": user_entity.get("ContactNo"),
                "Gender": user_entity.get("Gender"),
                "Location": user_entity.get("Location"),
            },
            "stocks": stocks
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#get_user_profile_and_stocks("ahsdiofhowiehfnsdfnonfo")
