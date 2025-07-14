from application import app
from flask import render_template, request, redirect, session
from azure.data.tables import TableServiceClient, TableEntity
import uuid
from application.services.azure_table import user_table_client

app.secret_key = 'your_super_secret_key'  # Needed for session

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
    return render_template('portfolioAnalysis.html', name=name, email=email, title="Portfolio Analysis")

@app.route("/tendors")
def tendors():
    if 'name' not in session or 'email' not in session:
        return redirect('/login')
    name = session['name']
    email = session['email']
    return render_template('tendors.html', name=name, email=email, title="Tendors")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')