"""Tests for the /predict endpoint."""

import pytest
from conftest import STRONG_STUDENT, WEAK_STUDENT, predict


@pytest.mark.parametrize('token', [None, 'invalid-token'])
def test_predict_without_valid_token_returns_401(token):
    response = predict(STRONG_STUDENT, token=token)
    assert response.status_code == 401


def test_predict_returns_valid_prediction(token):
    response = predict(STRONG_STUDENT, token=token)
    assert response.status_code == 200

    prediction = response.json()['prediction']
    assert len(prediction) == 1
    assert isinstance(prediction[0], float)
    assert 0.0 <= prediction[0] <= 1.0


def test_stronger_student_gets_higher_chance(token):
    strong = predict(STRONG_STUDENT, token=token).json()['prediction'][0]
    weak = predict(WEAK_STUDENT, token=token).json()['prediction'][0]
    assert strong > weak


@pytest.mark.parametrize(
    'input_data',
    [
        {**STRONG_STUDENT, 'gre_score': 'abc'},  # wrong type
        {k: v for k, v in STRONG_STUDENT.items() if k != 'cgpa'},  # missing
        {},  # empty
    ],
    ids=['wrong-type', 'missing-field', 'empty'],
)
def test_predict_with_invalid_input_returns_error(token, input_data):
    response = predict(input_data, token=token)
    assert response.status_code == 400
