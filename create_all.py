from flask import Flask

from config import database_uri
from models import db

app = Flask(__name__, static_url_path='',
            static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
db.init_app(app)

with app.app_context():
    db.create_all()
