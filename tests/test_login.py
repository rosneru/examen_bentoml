"""Tests for the /login endpoint."""

from datetime import UTC, datetime

import jwt
import pytest
from conftest import JWT_ALGORITHM, JWT_SECRET_KEY, VALID_CREDENTIALS, login


def test_login_returns_valid_jwt():
    response = login(**VALID_CREDENTIALS)
    assert response.status_code == 200

    token = response.json()['token']
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    assert payload['sub'] == VALID_CREDENTIALS['username']
    assert datetime.fromtimestamp(payload['exp'], UTC) > datetime.now(UTC)


@pytest.mark.parametrize(
    'username, password',
    [
        ('user123', 'wrong-password'),
        ('unknown-user', 'password123'),
        ('', ''),
    ],
)
def test_login_with_wrong_credentials_returns_401(username, password):
    response = login(username, password)
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid credentials'
