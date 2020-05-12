import os
import tempfile

import pytest

from app import app
from db import init_db


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


def test_empty_db(client):
    """Start with a blank database."""

    rv = client.get('/')
    assert b'Hello, World!' in rv.data
