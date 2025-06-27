from application import app
from flask import render_template

@app.route("/")
def index():
    return render_template('index.html', title = 'Home')

@app.route("/layout")
def layout():
    return render_template('layout.html', title = 'layout')

@app.route("/charts")
def charts():
    return render_template('charts.html', title = 'Charts')