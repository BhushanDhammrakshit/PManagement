from application import app
from flask import render_template
from flask import request, redirect, render_template
from azure.data.tables import TableServiceClient, TableEntity
import uuid
from application.services.azure_table import user_table_client

@app.route("/login")
def logIn():
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
        # Save to DB or Azure Table here...

                # Generate unique row key (e.g. UUID)
        row_key = str(uuid.uuid4())

        # Create entity
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
    return render_template('layout.html', name="User", email="test@gmail.com", title="Profile Management")

@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/algoHelper")
def algoHelper():
    return render_template('algoHelper.html')

@app.route("/portfolioMaker")
def portfolioMaker():
    return render_template('portfolioMaker.html')

@app.route("/portfolioAnalysis")
def portfolioAnalysis():
    return render_template('portfolioAnalysis.html')

@app.route("/tendors")
def tendors():
    return render_template('tendors.html')