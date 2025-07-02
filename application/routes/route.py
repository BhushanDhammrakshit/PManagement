from application import app
from flask import render_template

@app.route("/")
def index():
    return render_template('index.html')

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