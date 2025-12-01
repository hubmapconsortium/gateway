import json
from http import HTTPStatus
from unittest.mock import patch, MagicMock
from app import _get_status_info
import requests

def make_response(status, headers, text):
    mock = MagicMock()
    mock.status_code = status
    mock.headers = headers
    mock.text = text
    def json_loader():
        return json.loads(text)
    mock.json.side_effect = json_loader
    return mock

@patch("requests.get")
def test_json_response(mock_get):
    mock_get.return_value = make_response(
        status=200,
        headers={"Content-Type": "application/json"},
        text='{"service": "ok"}'
    )

    result = _get_status_info("http://example.com")
    assert result == {"service": "ok"}

@patch("requests.get")
def test_text_html_with_json(mock_get):
    mock_get.return_value = make_response(
        status=200,
        headers={"Content-Type": "text/html"},
        text='{"service": "ok"}'
    )

    result = _get_status_info("http://example.com")
    assert result == {"service": "ok"}

@patch("requests.get")
def test_text_plain_with_json(mock_get):
    mock_get.return_value = make_response(
        status=200,
        headers={"Content-Type": "text/plain"},
        text='{"a": 1}'
    )

    result = _get_status_info("http://example.com")
    assert result == {"a": 1}

@patch("requests.get")
def test_text_body_ok(mock_get):
    mock_get.return_value = make_response(
        status=200,
        headers={"Content-Type": "text/plain"},
        text='ok'
    )

    result = _get_status_info("http://example.com")
    assert result == {"text": "ok"}

@patch("requests.get")
def test_text_non_json_unrecognized(mock_get):
    mock_get.return_value = make_response(
        status=200,
        headers={"Content-Type": "text/plain"},
        text='Not JSON content'
    )

    result = _get_status_info("http://example.com")
    assert result == {
        "error": "Unexpected response text 'Not JSON content' for HTTP 200"
    }

@patch("requests.get")
def test_unsupported_content_type(mock_get):
    mock_get.return_value = make_response(
        status=200,
        headers={"Content-Type": "application/xml"},
        text='<xml></xml>'
    )

    result = _get_status_info("http://example.com")
    assert result == {"error": "Unable to determine status from header content type"}

@patch("requests.get")
def test_connect_timeout(mock_get):
    mock_get.side_effect = requests.exceptions.ConnectTimeout()

    result = _get_status_info("http://example.com")
    assert result == {"connection_timeout": True, "read_timeout": None}

@patch("requests.get")
def test_read_timeout(mock_get):
    mock_get.side_effect = requests.exceptions.ReadTimeout()

    result = _get_status_info("http://example.com")
    assert result == {"connection_timeout": False, "read_timeout": True}

@patch("requests.get")
def test_generic_request_exception(mock_get):
    mock_get.side_effect = requests.exceptions.RequestException("Network issue")

    result = _get_status_info("http://example.com")
    assert result == {"error": "Network issue"}
