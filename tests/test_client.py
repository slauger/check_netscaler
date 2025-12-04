"""
Tests for NITRO API client
"""

from unittest.mock import Mock, patch

import pytest
import requests

from check_netscaler.client import (
    NITROAPIError,
    NITROAuthenticationError,
    NITROClient,
    NITROConnectionError,
    NITROPermissionError,
    NITROResourceNotFoundError,
    NITROSession,
    NITROTimeoutError,
)


class TestNITROSession:
    """Test NITRO session management"""

    def test_session_initialization(self):
        """Test session can be initialized"""
        session = NITROSession(
            hostname="192.168.1.1",
            username="admin",
            password="secret",
        )

        assert session.hostname == "192.168.1.1"
        assert session.username == "admin"
        assert session.password == "secret"
        assert session.ssl is True
        assert session.port == 443
        assert session.is_logged_in is False

    def test_session_http_port(self):
        """Test HTTP uses port 80 by default"""
        session = NITROSession(
            hostname="192.168.1.1",
            username="admin",
            password="secret",
            ssl=False,
        )

        assert session.port == 80
        assert session.base_url == "http://192.168.1.1:80/nitro/v1"

    def test_session_custom_port(self):
        """Test custom port"""
        session = NITROSession(
            hostname="192.168.1.1",
            username="admin",
            password="secret",
            ssl=True,
            port=8443,
        )

        assert session.port == 8443
        assert session.base_url == "https://192.168.1.1:8443/nitro/v1"

    @patch("requests.Session.post")
    def test_login_success(self, mock_post):
        """Test successful login"""
        # Mock successful login response
        mock_cookie = Mock()
        mock_cookie.name = "NITRO_AUTH_TOKEN"
        mock_cookie.value = "abc123"

        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"sessionid": "test_session"}
        mock_response.headers = {"Set-Cookie": "NITRO_AUTH_TOKEN=abc123"}
        mock_response.cookies = [mock_cookie]
        mock_post.return_value = mock_response

        session = NITROSession(
            hostname="192.168.1.1",
            username="admin",
            password="secret",
        )
        session.login()

        assert session.is_logged_in is True
        assert session.session_id == "abc123"

        # Verify login request
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "login" in call_args[1]["json"]

    @patch("requests.Session.post")
    def test_login_authentication_failure(self, mock_post):
        """Test login with wrong credentials"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        session = NITROSession(
            hostname="192.168.1.1",
            username="admin",
            password="wrong",
        )

        with pytest.raises(NITROAuthenticationError, match="Authentication failed"):
            session.login()

    @patch("requests.Session.post")
    def test_login_timeout(self, mock_post):
        """Test login timeout"""
        mock_post.side_effect = requests.exceptions.Timeout("Connection timeout")

        session = NITROSession(
            hostname="192.168.1.1",
            username="admin",
            password="secret",
            timeout=1,
        )

        with pytest.raises(NITROTimeoutError, match="timed out"):
            session.login()

    @patch("requests.Session.post")
    def test_login_connection_error(self, mock_post):
        """Test login connection error"""
        mock_post.side_effect = requests.exceptions.ConnectionError("Cannot connect")

        session = NITROSession(
            hostname="192.168.1.1",
            username="admin",
            password="secret",
        )

        with pytest.raises(NITROConnectionError, match="Connection failed"):
            session.login()

    @patch("requests.Session.post")
    def test_logout(self, mock_post):
        """Test logout"""
        session = NITROSession(
            hostname="192.168.1.1",
            username="admin",
            password="secret",
        )
        session.is_logged_in = True
        session.logout()

        assert session.is_logged_in is False
        assert session.session_id is None

    @patch("requests.Session.post")
    def test_context_manager(self, mock_post):
        """Test session as context manager"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {}
        mock_response.headers = {}
        mock_response.cookies = []
        mock_post.return_value = mock_response

        with NITROSession(
            hostname="192.168.1.1",
            username="admin",
            password="secret",
        ) as session:
            assert session.is_logged_in is True

        # After context, should be logged out
        assert session.is_logged_in is False


class TestNITROClient:
    """Test NITRO API client"""

    def test_client_initialization(self):
        """Test client can be initialized"""
        client = NITROClient(
            hostname="192.168.1.1",
            username="admin",
            password="secret",
        )

        assert client.session.hostname == "192.168.1.1"
        assert client.api_version == "v1"

    @patch("requests.Session.post")
    @patch("requests.Session.get")
    def test_get_stat(self, mock_get, mock_post):
        """Test get_stat method"""
        # Mock login
        mock_login_response = Mock()
        mock_login_response.status_code = 201
        mock_login_response.json.return_value = {}
        mock_login_response.headers = {}
        mock_login_response.headers = {}
        mock_login_response.cookies = []
        mock_post.return_value = mock_login_response

        # Mock GET request
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"lbvserver": [{"name": "test", "state": "UP"}]}
        mock_get.return_value = mock_get_response

        client = NITROClient(
            hostname="192.168.1.1",
            username="admin",
            password="secret",
        )
        client.login()

        result = client.get_stat("lbvserver")

        assert "lbvserver" in result
        mock_get.assert_called_once()

    @patch("requests.Session.post")
    @patch("requests.Session.get")
    def test_get_config(self, mock_get, mock_post):
        """Test get_config method"""
        # Mock login
        mock_login_response = Mock()
        mock_login_response.status_code = 201
        mock_login_response.json.return_value = {}
        mock_login_response.headers = {}
        mock_login_response.cookies = []
        mock_post.return_value = mock_login_response

        # Mock GET request
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"lbvserver": [{"name": "test", "ipv46": "10.0.0.1"}]}
        mock_get.return_value = mock_get_response

        client = NITROClient(
            hostname="192.168.1.1",
            username="admin",
            password="secret",
        )
        client.login()

        result = client.get_config("lbvserver")

        assert "lbvserver" in result

    @patch("requests.Session.post")
    @patch("requests.Session.get")
    def test_get_with_resource_name(self, mock_get, mock_post):
        """Test GET with specific resource name"""
        # Mock login
        mock_login_response = Mock()
        mock_login_response.status_code = 201
        mock_login_response.json.return_value = {}
        mock_login_response.headers = {}
        mock_login_response.cookies = []
        mock_post.return_value = mock_login_response

        # Mock GET request
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"lbvserver": [{"name": "my_vserver", "state": "UP"}]}
        mock_get.return_value = mock_get_response

        client = NITROClient(
            hostname="192.168.1.1",
            username="admin",
            password="secret",
        )
        client.login()

        client.get_stat("lbvserver", "my_vserver")

        # Verify URL contains resource name
        call_url = mock_get.call_args[0][0]
        assert "my_vserver" in call_url

    @patch("requests.Session.post")
    @patch("requests.Session.get")
    def test_get_not_found(self, mock_get, mock_post):
        """Test GET with 404 response"""
        # Mock login
        mock_login_response = Mock()
        mock_login_response.status_code = 201
        mock_login_response.json.return_value = {}
        mock_login_response.headers = {}
        mock_login_response.cookies = []
        mock_post.return_value = mock_login_response

        # Mock 404 response
        mock_get_response = Mock()
        mock_get_response.status_code = 404
        mock_get.return_value = mock_get_response

        client = NITROClient(
            hostname="192.168.1.1",
            username="admin",
            password="secret",
        )
        client.login()

        with pytest.raises(NITROResourceNotFoundError, match="not found"):
            client.get_stat("nonexistent")

    @patch("requests.Session.post")
    @patch("requests.Session.get")
    def test_get_permission_denied(self, mock_get, mock_post):
        """Test GET with 403 response"""
        # Mock login
        mock_login_response = Mock()
        mock_login_response.status_code = 201
        mock_login_response.json.return_value = {}
        mock_login_response.headers = {}
        mock_login_response.cookies = []
        mock_post.return_value = mock_login_response

        # Mock 403 response
        mock_get_response = Mock()
        mock_get_response.status_code = 403
        mock_get.return_value = mock_get_response

        client = NITROClient(
            hostname="192.168.1.1",
            username="admin",
            password="secret",
        )
        client.login()

        with pytest.raises(NITROPermissionError, match="Insufficient permissions"):
            client.get_stat("restricted_resource")

    @patch("requests.Session.post")
    def test_get_not_logged_in(self, mock_post):
        """Test GET without login"""
        client = NITROClient(
            hostname="192.168.1.1",
            username="admin",
            password="secret",
        )

        with pytest.raises(NITROAPIError, match="Not logged in"):
            client.get_stat("lbvserver")

    @patch("requests.Session.post")
    @patch("requests.Session.get")
    def test_context_manager(self, mock_get, mock_post):
        """Test client as context manager"""
        mock_login_response = Mock()
        mock_login_response.status_code = 201
        mock_login_response.json.return_value = {}
        mock_login_response.headers = {}
        mock_login_response.cookies = []
        mock_post.return_value = mock_login_response

        with NITROClient(
            hostname="192.168.1.1",
            username="admin",
            password="secret",
        ) as client:
            assert client.session.is_logged_in is True

        # After context, should be logged out
        assert client.session.is_logged_in is False
