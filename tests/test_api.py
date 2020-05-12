import os
import tempfile

import pytest

from app import app, init_db


@pytest.fixture
def client():
    db_fd, tmp_file = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{tmp_file}'
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client

    os.close(db_fd)
    os.unlink(tmp_file)


def test_get_empty_polls(client):
    """Start with a blank database."""

    r = client.get('/poll')
    assert 200 == r.status_code
    assert [] == r.get_json()


def test_create_poll(client):

    r = client.post('/poll')
    assert 400 == r.status_code
    assert 'Name must be specified' == r.get_json()['error']

    data = {
        'name': 'Test Poll',
        'description': 'test to create poll'
    }
    r = client.post('/poll', json=data)
    assert 201 == r.status_code
    assert 'Test Poll' == r.get_json()['name']


def test_list_polls(client):
    for i in range(5):
        data = dict(name=f'Poll{i}')
        r = client.post('/poll', json=data)
        assert 201 == r.status_code

    r = client.get('/poll')
    assert 200 == r.status_code
    assert 5 == len(r.get_json())


def test_get_poll_that_does_not_exist(client):
    r = client.get('/poll/1000')
    assert 404, r.status_code


def test_get_poll(client):
    data = {
        'name': 'My test Poll',
        'description': 'test to create poll'
    }
    r = client.post('/poll', json=data)
    assert 201 == r.status_code

    poll_id = r.get_json()['id']
    r = client.get(f'/poll/{poll_id}')
    assert 200 == r.status_code
    assert 'My test Poll' == r.get_json()['name']


def test_get_vote_for_non_existing_poll(client):
    r = client.get('/poll/1000/vote')
    assert 404 == r.status_code


def test_create_vote_with_bad_data(client):
    # Create poll
    r = client.post('/poll', json=dict(name='My poll'))
    assert 201 == r.status_code
    poll_id = r.get_json()['id']

    r = client.post(f'/poll/{poll_id}/vote')
    assert 400 == r.status_code
    assert 'Voter and points must be specified' == r.get_json()['error']

    data = {
        'voter': 'Maren',
        'points': 'foo'
    }
    r = client.post(f'/poll/{poll_id}/vote', json=data)
    assert 400 == r.status_code
    assert 'Points are not in the correct format' == r.get_json()['error']


def test_poll_vote_flow(client):
    # Create poll
    r = client.post('/poll', json=dict(name='My poll'))
    assert 201 == r.status_code
    poll_id = r.get_json()['id']

    # List no votes
    r = client.get(f'/poll/{poll_id}/vote')
    assert 200 == r.status_code
    assert [] == r.get_json()

    # Create a vote
    data = {
        'voter': 'Maren',
        'points': '1/2'
    }
    r = client.post(f'/poll/{poll_id}/vote', json=data)
    assert 201 == r.status_code
    assert 'Maren' == r.get_json()['voter']

    # Create another
    data['voter'] = 'Pelle'
    r = client.post(f'/poll/{poll_id}/vote', json=data)
    assert 201 == r.status_code

    # List votes
    r = client.get(f'/poll/{poll_id}/vote')
    assert 200 == r.status_code
    assert 2 == len(r.get_json())


def test_update_vote_if_already_exists(client):
    # Create poll
    r = client.post('/poll', json=dict(name='My poll'))
    assert 201 == r.status_code
    poll_id = r.get_json()['id']

    # Create a vote
    data = {
        'voter': 'Kalle',
        'points': '3'
    }
    r = client.post(f'/poll/{poll_id}/vote', json=data)
    assert 201 == r.status_code

    # Update the vote
    data['points'] = '2'
    r = client.post(f'/poll/{poll_id}/vote', json=data)
    assert 200 == r.status_code

    # Check that there is still just one vote
    # List votes
    r = client.get(f'/poll/{poll_id}/vote')
    assert 200 == r.status_code
    assert 1 == len(r.get_json())
    assert '2' == r.get_json()[0]['points']
