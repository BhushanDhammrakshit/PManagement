from flask import Flask
from application.routes.user_routes import user_blueprint
from application.routes.tender_api import tender_api

app = Flask(__name__)

app.register_blueprint(user_blueprint)
app.register_blueprint(tender_api)

from application.routes import route