"""Shared fixtures for the API tests.

The tests run against a running instance of the service (local
`bentoml serve` or the Docker container). The base URL can be changed
with the environment variable API_URL.
"""

import os

import pytest
import requests

API_URL = os.environ.get('API_URL', 'http://localhost:3000')

# Must match the secret and algorithm used in src/service.py
JWT_SECRET_KEY = (
    '2914d5d479572c037672403f6a02c105bddd92457dc851adbfd8f94eb3648cac'
)
JWT_ALGORITHM = 'HS256'

VALID_CREDENTIALS = {'username': 'user123', 'password': 'password123'}

STRONG_STUDENT = {
    'gre_score': 335,
    'toefl_score': 118,
    'university_rating': 5,
    'sop': 4.5,
    'lor': 4.5,
    'cgpa': 9.6,
    'research': True,
}

WEAK_STUDENT = {
    'gre_score': 300,
    'toefl_score': 99,
    'university_rating': 1,
    'sop': 2.0,
    'lor': 2.5,
    'cgpa': 7.5,
    'research': False,
}


@pytest.fixture(scope='session', autouse=True)
def api_is_running():
    try:
        requests.get(f'{API_URL}/readyz', timeout=5).raise_for_status()
    except requests.RequestException as exc:
        pytest.exit(f'API not reachable at {API_URL}: {exc}', returncode=1)


def login(username: str, password: str) -> requests.Response:
    return requests.post(
        f'{API_URL}/login',
        json={'credentials': {'username': username, 'password': password}},
        timeout=10,
    )


def predict(input_data: dict, token: str | None = None) -> requests.Response:
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    return requests.post(
        f'{API_URL}/predict',
        json={'input_data': input_data},
        headers=headers,
        timeout=10,
    )


@pytest.fixture(scope='session')
def token() -> str:
    response = login(**VALID_CREDENTIALS)
    response.raise_for_status()
    return response.json()['token']
