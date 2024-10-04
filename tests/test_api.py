import json

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.main import validate_date


@pytest.mark.parametrize("date, expected_bool",
                         [('31.01.2021', True),
                          ('01.31.2021', False),
                          ('01.31/2021', False),
                          ('первое апреля', False)
                          ])
def test_valid_date(date, expected_bool):
    assert validate_date(date) == expected_bool


client = TestClient(app)


def test_main_url_bad():
    response = client.get('/bad')
    assert response.status_code == 404


def test_post():
    deposit = {
        "date": "01.01.2021",
        "periods": 3,
        "amount": 10000,
        "rate": 6
    }
    response = client.post('/', data=json.dumps(deposit))
    assert response.status_code == 200
    assert response.json() == {
        "31.01.2021": 10050,
        "28.02.2021": 10100.25,
        "31.03.2021": 10150.75
    }


def test_post_calculation():
    deposit = {
        "date": "31.01.2021",
        "periods": 3,
        "amount": 10000,
        "rate": 6
    }
    response = client.post("/", data=json.dumps(deposit))
    assert response.status_code == 200
    assert response.json() == {
        "31.01.2021": 10050,
        "28.02.2021": 10100.25,
        "31.03.2021": 10150.75
    }


def test_post_wrong_date():
    deposit = {
        "date": "01.31.2021",
        "periods": 3,
        "amount": 10000,
        "rate": 6
    }
    response = client.post('/', data=json.dumps(deposit))
    assert response.status_code == 422
    assert response.json() == { "detail": [
    {
      "type": "value_error",
      "loc": [
        "body",
        "date"
      ],
      "msg": "Value error, Date must be in the format DD.MM.YYYY",
      "input": deposit["date"],
      "ctx": {
        "error": {}
      }
    }
  ]}


def test_post_wrong_period():
    deposit = {
        "date": "31.01.2021",
        "periods": 61,
        "amount": 10000,
        "rate": 6
    }
    response = client.post('/', data=json.dumps(deposit))
    assert response.status_code == 422
    assert response.json() == {"detail": [
    {
      "type": "less_than_equal",
      "loc": [
        "body",
        "periods"
      ],
      "msg": "Input should be less than or equal to 60",
      "input": deposit["periods"],
      "ctx": {
        "le": 60
      }
    }
  ]}


def test_post_wrong_amount():
    deposit = {
        "date": "31.01.2021",
        "periods": 3,
        "amount": 7777,
        "rate": 6
    }

    response = client.post('/', data=json.dumps(deposit))
    assert response.status_code == 422
    assert response.json() == {"detail": [
    {
      "type": "greater_than_equal",
      "loc": ["body","amount"],
      "msg": "Input should be greater than or equal to 10000",
      "input": deposit["amount"],
      "ctx": {
        "ge": 10000
      }
    }
  ]}


def test_post_wrong_rate():
    deposit = {
        "date": "31.01.2021",
        "periods": 3,
        "amount": 10000,
        "rate": 10
    }
    response = client.post('/', data=json.dumps(deposit))
    assert response.json() == {"detail": [
    {
      "type": "less_than_equal",
      "loc": [
        "body",
        "rate"
      ],
      "msg": "Input should be less than or equal to 8",
      "input": deposit["rate"],
      "ctx": {
        "le": 8
      }
    }
  ]}