from flask_sqlalchemy import SQLAlchemy

from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

POINTS_CHOICES = ['0', '1/2', '1', '2', '3', '5', '8', '13']


class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(120), nullable=True)

    def __repr__(self):
        return f'<Poll {self.name}>'


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voter = db.Column(db.String(80), nullable=False)
    points = db.Column(db.String(5), nullable=False)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)
    poll = db.relationship('Poll', backref=db.backref('votes', lazy=True))
