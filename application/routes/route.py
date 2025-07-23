from application import app
from flask import render_template, request, redirect, session
from azure.data.tables import TableServiceClient, TableEntity
import uuid
from application.services.azure_table import user_table_client, stocks_table_client
from application.routes.stock_analysis_api import stock_analysis_api
from application.routes.heatmap import heatmap_bp

app.secret_key = 'your_super_secret_key'  # Needed for session
app.register_blueprint(stock_analysis_api)
app.register_blueprint(heatmap_bp)

@app.route("/login", methods=['GET', 'POST'])
def logIn():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Query user from Azure Table
        query_filter = f"Email eq '{email}' and Password eq '{password}'"
        users = list(user_table_client.query_entities(query_filter=query_filter))
        if users:
            user = users[0]
            session['name'] = user.get("UserName", "User")
            session['email'] = user.get("Email", "")
            return redirect('/home')
        else:
            return render_template('logIn.html', error="Invalid credentials")
    return render_template('logIn.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        gender = request.form['gender']
        location = request.form['location']
        password = request.form['password']
        row_key = str(uuid.uuid4())
        user_entity = {
            "PartitionKey": "PartitionKey",
            "RowKey": row_key,
            "UserName": name,
            "Email": email,
            "ContactNo": phone,
            "Gender": gender,
            "Location": location,
            "Password": password
        }
        try:
            user_table_client.create_entity(entity=user_entity)
        except Exception as e:
            return f"Error saving to Azure Table Storage: {str(e)}", 500
        return redirect('/login')
    return render_template('signup.html')

@app.route("/layout")
def layout():
    name = session.get('name', "User")
    email = session.get('email', "test@gmail.com")
    return render_template('layout.html', name=name, email=email, title="Profile Management")

@app.route("/home")
def home():
    if 'name' not in session or 'email' not in session:
        return redirect('/login')
    name = session['name']
    email = session['email']
    return render_template('home.html', name=name, email=email, title="Home")

@app.route("/algoHelper")
def algoHelper():
    if 'name' not in session or 'email' not in session:
        return redirect('/login')
    name = session['name']
    email = session['email']
    return render_template('algoHelper.html', name=name, email=email, title="Algo Helper")

@app.route("/portfolioMaker")
def portfolioMaker():
    if 'name' not in session or 'email' not in session:
        return redirect('/login')
    name = session['name']
    email = session['email']
    return render_template('portfolioMaker.html', name=name, email=email, title="Portfolio Maker")

@app.route("/portfolioAnalysis")
def portfolioAnalysis():
    if 'name' not in session or 'email' not in session:
        return redirect('/login')
    name = session['name']
    email = session['email']
    # Fetch user info to get user_id (RowKey)
    user = list(user_table_client.query_entities(query_filter=f"Email eq '{email}'"))
    if not user:
        return render_template('portfolioAnalysis.html', name=name, email=email, title="Portfolio Analysis", stocks=[])
    user_id = user[0].get('RowKey')
    # Fetch stocks for this user
    stocks = list(stocks_table_client.query_entities(query_filter=f"UserId eq '{user_id}'"))

    # Clean up EntityProperty/Edm.Int64 fields for template rendering
    def clean_value(val):
        # Azure Table SDK v12+ returns EntityProperty for int fields, or dict for JSON
        try:
            # Handle Azure EntityProperty (repr: EntityProperty(value=300, edm_type=<EdmType.INT64: 'Edm.Int64'>))
            if hasattr(val, 'value'):
                return val.value
            # Handle dict with '_' key (from JSON serialization)
            if isinstance(val, dict) and '_' in val:
                return val['_']
        except Exception:
            pass
        return val

    def clean_stock(stock):
        for key in ['Quantity', 'PurchasePrice', 'CurrentPrice']:
            if key in stock:
                stock[key] = clean_value(stock[key])
        return stock

    stocks = [clean_stock(dict(s)) for s in stocks]
    return render_template('portfolioAnalysis.html', name=name, email=email, title="Portfolio Analysis", stocks=stocks)

@app.route("/tenders")
def tenders():
    if 'name' not in session or 'email' not in session:
        return redirect('/login')
    name = session['name']
    email = session['email']
    return render_template('tenders.html', name=name, email=email, title="Tenders")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route("/portfolio/add", methods=["POST"])
def add_to_portfolio():
    if 'name' not in session or 'email' not in session:
        return redirect('/login')
    # Get form data
    stock_name = request.form.get('stock_name')
    quantity = request.form.get('quantity')
    purchase_price = request.form.get('purchase_price')
    purchase_date = request.form.get('purchase_date')
    current_price = request.form.get('current_price')
    sector = request.form.get('sector')
    exchange = request.form.get('exchange')
    row_key = str(uuid.uuid4())
    entity = {
        "PartitionKey": "PartitionKey",
        "RowKey": row_key,
        "StockName": stock_name,
        "Quantity": int(quantity),
        "PurchasePrice": float(purchase_price),
        "PurchaseDate": purchase_date,
        "CurrentPrice": float(current_price),
        "Sector": sector,
        "Exchange": exchange
    }
    try:
        stocks_table_client.create_entity(entity=entity)
    except Exception as e:
        return f"Error saving to Azure Table Storage: {str(e)}", 500
    # Show success popup on redirect
    return redirect('/portfolioMaker?success=1')