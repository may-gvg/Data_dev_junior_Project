from app import app, read_csv
from unittest.mock import Mock


def test_homepage(monkeypatch):
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200


def test_readcsv(monkeypatch):
    requests_mock = Mock()
    response = requests_mock.return_value
    csv = read_csv()
    assert len(csv) > 0


def test_return_home(monkeypatch):
    with app.test_client() as client:
        response = client.get('/')
        assert b'Dashboard' in response.data
