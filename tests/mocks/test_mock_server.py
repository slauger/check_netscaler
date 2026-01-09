"""
Integration tests for Mock NITRO API Server
"""

import pytest
import requests


def test_mock_server_starts(mock_nitro_server):
    """Test that mock server starts successfully"""
    assert mock_nitro_server is not None
    assert mock_nitro_server.port > 0


def test_login_success(mock_nitro_server):
    """Test successful login"""
    url = f"{mock_nitro_server.get_url()}/nitro/v1/config/login"
    data = {"login": {"username": "nsroot", "password": "nsroot"}}

    response = requests.post(url, json=data)

    assert response.status_code == 200
    assert response.json()["errorcode"] == 0
    assert "NITRO_AUTH_TOKEN" in response.cookies


def test_login_failure(mock_nitro_server):
    """Test failed login with invalid credentials"""
    url = f"{mock_nitro_server.get_url()}/nitro/v1/config/login"
    data = {"login": {"username": "wrong", "password": ""}}

    response = requests.post(url, json=data)

    assert response.status_code == 401


def test_get_lbvserver_config(mock_nitro_server):
    """Test getting lbvserver config data"""
    # Login first
    login_url = f"{mock_nitro_server.get_url()}/nitro/v1/config/login"
    login_data = {"login": {"username": "nsroot", "password": "nsroot"}}
    login_resp = requests.post(login_url, json=login_data)
    cookies = login_resp.cookies

    # Get lbvserver config
    url = f"{mock_nitro_server.get_url()}/nitro/v1/config/lbvserver"
    response = requests.get(url, cookies=cookies)

    assert response.status_code == 200
    data = response.json()
    assert "lbvserver" in data
    assert isinstance(data["lbvserver"], list)
    assert len(data["lbvserver"]) == 3  # lb_web, lb_ssl, lb_down


def test_get_lbvserver_stat(mock_nitro_server):
    """Test getting lbvserver stat data"""
    # Login
    login_url = f"{mock_nitro_server.get_url()}/nitro/v1/config/login"
    login_data = {"login": {"username": "nsroot", "password": "nsroot"}}
    login_resp = requests.post(login_url, json=login_data)
    cookies = login_resp.cookies

    # Get lbvserver stats
    url = f"{mock_nitro_server.get_url()}/nitro/v1/stat/lbvserver"
    response = requests.get(url, cookies=cookies)

    assert response.status_code == 200
    data = response.json()
    assert "lbvserver" in data
    assert isinstance(data["lbvserver"], list)


def test_get_specific_resource(mock_nitro_server):
    """Test getting a specific named resource"""
    # Login
    login_url = f"{mock_nitro_server.get_url()}/nitro/v1/config/login"
    login_data = {"login": {"username": "nsroot", "password": "nsroot"}}
    login_resp = requests.post(login_url, json=login_data)
    cookies = login_resp.cookies

    # Get specific lbvserver by name
    url = f"{mock_nitro_server.get_url()}/nitro/v1/config/lbvserver/lb_web"
    response = requests.get(url, cookies=cookies)

    assert response.status_code == 200
    data = response.json()
    assert "lbvserver" in data
    lb = data["lbvserver"]
    assert lb["name"] == "lb_web"


def test_systemfile_with_args(mock_nitro_server):
    """Test systemfile with query args (license check)"""
    # Login
    login_url = f"{mock_nitro_server.get_url()}/nitro/v1/config/login"
    login_data = {"login": {"username": "nsroot", "password": "nsroot"}}
    login_resp = requests.post(login_url, json=login_data)
    cookies = login_resp.cookies

    # Get license files
    url = f"{mock_nitro_server.get_url()}/nitro/v1/config/systemfile"
    params = {"args": "filelocation:/nsconfig/license"}
    response = requests.get(url, params=params, cookies=cookies)

    assert response.status_code == 200
    data = response.json()
    assert "systemfile" in data
    files = data["systemfile"]
    assert isinstance(files, list)
    assert any(f["filename"].endswith(".lic") for f in files)


def test_ntp_status(mock_nitro_server):
    """Test NTP status response format"""
    # Login
    login_url = f"{mock_nitro_server.get_url()}/nitro/v1/config/login"
    login_data = {"login": {"username": "nsroot", "password": "nsroot"}}
    login_resp = requests.post(login_url, json=login_data)
    cookies = login_resp.cookies

    # Get NTP status
    url = f"{mock_nitro_server.get_url()}/nitro/v1/config/ntpstatus"
    response = requests.get(url, cookies=cookies)

    assert response.status_code == 200
    data = response.json()
    assert "ntpstatus" in data
    assert "response" in data["ntpstatus"]
    assert "*192.168.1.1" in data["ntpstatus"]["response"]  # Synchronized peer


def test_unauthenticated_request(mock_nitro_server):
    """Test that unauthenticated requests are rejected"""
    url = f"{mock_nitro_server.get_url()}/nitro/v1/config/lbvserver"
    response = requests.get(url)

    assert response.status_code == 401


def test_resource_not_found(mock_nitro_server):
    """Test 404 for non-existent resource type"""
    # Login
    login_url = f"{mock_nitro_server.get_url()}/nitro/v1/config/login"
    login_data = {"login": {"username": "nsroot", "password": "nsroot"}}
    login_resp = requests.post(login_url, json=login_data)
    cookies = login_resp.cookies

    # Try to get non-existent resource
    url = f"{mock_nitro_server.get_url()}/nitro/v1/config/nonexistent"
    response = requests.get(url, cookies=cookies)

    assert response.status_code == 404
