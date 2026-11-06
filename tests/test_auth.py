"""JWT authentication tests (middleware protecting /predict)."""

from datetime import UTC, datetime, timedelta

import jwt
import requests
from conftest import (
    API_URL,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
    STRONG_STUDENT,
    predict,
)


def make_token(expires_in: timedelta, secret: str = JWT_SECRET_KEY) -> str:
    payload = {'sub': 'user123', 'exp': datetime.now(UTC) + expires_in}
    return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)


def test_missing_token_fails():
    response = predict(STRONG_STUDENT)
    assert response.status_code == 401
    assert response.json()['detail'] == 'Missing authentication token'


def test_invalid_token_fails():
    response = predict(STRONG_STUDENT, token='not-a-jwt')
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid token'


def test_token_with_wrong_signature_fails():
    token = make_token(timedelta(hours=1), secret='wrong-secret' * 4)
    response = predict(STRONG_STUDENT, token=token)
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid token'


def test_expired_token_fails():
    token = make_token(timedelta(minutes=-1))
    response = predict(STRONG_STUDENT, token=token)
    assert response.status_code == 401
    assert response.json()['detail'] == 'Token has expired'


def test_token_without_bearer_prefix_fails(token):
    response = requests.post(
        f'{API_URL}/predict',
        json={'input_data': STRONG_STUDENT},
        headers={'Authorization': token},
        timeout=10,
    )
    assert response.status_code == 401


def test_valid_token_succeeds(token):
    response = predict(STRONG_STUDENT, token=token)
    assert response.status_code == 200
