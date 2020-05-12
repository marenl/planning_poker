from flask_sqlalchemy import SQLAlchemy
from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///planning.db'
db = SQLAlchemy(app)


def init_db():
    db.create_all()
