from unittest.mock import MagicMock
import socket
import ssl

import pytest

from app.main import create_app
from app import tls_check


@pytest.fixture
def client():
    return create_app({"TESTING": True}).test_client()


def test_frontend_and_assets(client):
    page = client.get("/")
    assert page.status_code == 200
    assert b'/static/app.js' in page.data
    assert client.get('/static/app.js').status_code == 200
    assert client.get('/static/style.css').status_code == 200
    assert client.get('/api/health').json == {"ok": True}


def test_scan_contract(client, monkeypatch):
    expected = {"host": "example.com", "ok": True, "protocol": "TLSv1.3",
                "cipher": "TLS_AES_256_GCM_SHA384", "expires": "2030-01-01", "days_left": 100}
    collector = MagicMock(return_value=expected)
    monkeypatch.setattr(tls_check, 'check', collector)
    response = client.post('/api/scan', json={"url": "example.com"})
    assert response.status_code == 200
    assert response.json == expected
    collector.assert_called_once_with('example.com')


@pytest.mark.parametrize('body', [{}, [], {"url": None}, {"url": 42}])
def test_invalid_json_fields(client, body):
    assert client.post('/api/scan', json=body).status_code == 400


def test_bad_body_formats(client):
    assert client.post('/api/scan', data='url=example.com').status_code == 415
    response = client.post('/api/scan', data='{', content_type='application/json')
    assert response.status_code == 400
    assert 'error' in response.json


@pytest.mark.parametrize('url', ['', 'http://example.com', 'https://a:b@example.com',
                                 'example.com:8000', 'https://', 'bad host'])
def test_invalid_targets_do_not_connect(client, monkeypatch, url):
    resolve = MagicMock()
    monkeypatch.setattr(socket, 'getaddrinfo', resolve)
    assert client.post('/api/scan', json={"url": url}).status_code == 400
    resolve.assert_not_called()


def test_normalize_host():
    assert tls_check.normalize_host(' https://Example.COM/path?q=1 ') == 'example.com'


@pytest.mark.parametrize('ip', ['127.0.0.1', '10.0.0.1', '169.254.169.254', '::1'])
def test_private_targets_never_connect(client, monkeypatch, ip):
    monkeypatch.setattr(socket, 'getaddrinfo', lambda *a, **k: [
        (socket.AF_INET, socket.SOCK_STREAM, 6, '', (ip, 443))])
    connect = MagicMock()
    monkeypatch.setattr(socket, 'socket', connect)
    assert client.post('/api/scan', json={"url": "example.com"}).status_code == 400
    connect.assert_not_called()


def test_tls_success_uses_validated_address(monkeypatch):
    monkeypatch.setattr(socket, 'getaddrinfo', lambda *a, **k: [
        (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34', 443))])
    raw = MagicMock()
    monkeypatch.setattr(socket, 'socket', MagicMock(return_value=raw))
    context = MagicMock()
    monkeypatch.setattr(ssl, 'create_default_context', lambda: context)
    tls = context.wrap_socket.return_value.__enter__.return_value
    tls.getpeercert.return_value = {'notAfter': 'Jan 01 00:00:00 2030 GMT'}
    tls.version.return_value = 'TLSv1.3'
    tls.cipher.return_value = ('TLS_AES_256_GCM_SHA384', 'TLSv1.3', 256)
    result = tls_check.check('example.com')
    assert result['ok'] is True
    assert result['expires'] == '2030-01-01'
    raw.__enter__.return_value.connect.assert_called_once_with(('93.184.216.34', 443))
    assert context.wrap_socket.call_args.kwargs['server_hostname'] == 'example.com'


def test_connection_failure(client, monkeypatch):
    def fail(*args, **kwargs):
        raise socket.gaierror('DNS unavailable')
    monkeypatch.setattr(socket, 'getaddrinfo', fail)
    response = client.post('/api/scan', json={"url": "example.com"})
    assert response.status_code == 200
    assert response.json['ok'] is False
    assert response.json['problem']
