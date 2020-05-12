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
