from application import app
from flask import render_template

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/layout")
def layout():
    return render_template('layout.html', name="User", email="test@gmail.com", title="Profile Management")

@app.route("/charts")
def charts():
    return render_template('charts.html')