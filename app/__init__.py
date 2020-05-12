from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

POINTS_CHOICES = ['0', '1/2', '1', '2', '3', '5', '8', '13']

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY='dev',
    SQLALCHEMY_DATABASE_URI='sqlite:///planning.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)
db = SQLAlchemy(app)


def init_db():
    db.create_all()


init_db()


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


@app.route('/poll', methods=['GET', 'POST'])
def api_polls():
    if request.method == 'POST':
        data = request.get_json()
        if not data or not data['name']:
            return dict(error='Name must be specified'), 400
        new_poll = Poll(name=data['name'], description=data.get('description', ''))
        db.session.add(new_poll)
        db.session.commit()
        return jsonify(new_poll.serialize), 201
    else:
        all_polls = Poll.query.all()
        return jsonify([p.serialize for p in all_polls])


@app.route('/poll/<poll_id>')
def api_poll(poll_id):
    result = db.session.query(Poll).filter_by(id=poll_id)
    if not result.count():
        return dict(error='No poll with that id'), 404
    return jsonify(result[0].serialize)


@app.route('/poll/<poll_id>/vote', methods=['GET', 'POST'])
def api_vote(poll_id):
    result = db.session.query(Poll).filter_by(id=poll_id)
    if not result.count():
        return dict(error='No poll with that id'), 404

    if request.method == 'POST':
        data = request.get_json()
        if not data or not data['voter'] or not data['points']:
            return dict(error='Voter and points must be specified'), 400
        if data['points'] not in POINTS_CHOICES:
            return dict(error='Points are not in the correct format'), 400

        # Check if the vote already exists first
        result = db.session.query(Vote).filter_by(voter=data['voter'], poll_id=poll_id)
        if result.count():
            vote = result[0]
            vote.points = data['points']
            status = 200
        else:
            vote = Vote(voter=data['voter'], points=data['points'], poll_id=poll_id)
            status = 201
            db.session.add(vote)

        db.session.commit()
        return jsonify(vote.serialize), status
    else:
        result = db.session.query(Vote).filter_by(poll_id=poll_id)
        return jsonify([v.serialize for v in result])
