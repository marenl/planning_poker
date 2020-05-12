from . import db


class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(120), nullable=True)

    def __repr__(self):
        return f'<Poll {self.name}>'

    @property
    def serialize(self):
        return dict(
            id=self.id,
            name=self.name,
            description=self.description,
        )


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voter = db.Column(db.String(80), nullable=False)
    points = db.Column(db.String(5), nullable=False)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)
    poll = db.relationship('Poll', backref=db.backref('votes', lazy=True))

    @property
    def serialize(self):
        return dict(
            id=self.id,
            voter=self.voter,
            points=self.points,
        )
