from flask import Flask
from application.routes.user_routes import user_blueprint

app = Flask(__name__)

app.register_blueprint(user_blueprint)
