from flask import Blueprint, jsonify
from application.services.azure_table import get_user_by_credentials, get_user_stocks_by_row_key
from flask import Blueprint, jsonify, request
from flask import render_template

user_blueprint = Blueprint("user", __name__)

#ahsdiofhowiehfnsdfnonfo
@user_blueprint.route('/user/profile', methods=['POST'])
def get_user_profile_and_stocks():
    """
    Retrieves user profile and stock holdings
    """
    try:
        #user_entity = get_user_by_row_key(userid)
        Email = request.form.get("email")
        Password = request.form.get("password")
        user_entity = get_user_by_credentials(Email, Password)
        user_stocks = get_user_stocks_by_row_key(user_entity.get("RowKey"))
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
        
        user = {
        "name": user_entity.get("UserName"),
        "email": user_entity.get("Email"),
        "phone": user_entity.get("ContactNo"),
        "gender": user_entity.get("Gender"),
        "location": user_entity.get("Location"),
        }
        
        return render_template("profile.html", user=user, stocks=stocks)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
