from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY='dev',
    SQLALCHEMY_DATABASE_URI='sqlite:///planning.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)
CORS(app)
db = SQLAlchemy(app)

from .routes import planning
app.register_blueprint(planning)
db.create_all()
