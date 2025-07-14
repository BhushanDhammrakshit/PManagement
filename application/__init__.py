from flask import Flask
from application.routes.user_routes import user_blueprint
from application.routes.tendor_api import tendor_api

app = Flask(__name__)

app.register_blueprint(user_blueprint)
app.register_blueprint(tendor_api)

from application.routes import route