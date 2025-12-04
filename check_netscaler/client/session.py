"""
Session management for NITRO API
"""

from typing import Optional

import requests

from check_netscaler.client.exceptions import (
    NITROAuthenticationError,
    NITROConnectionError,
    NITROTimeoutError,
)


class NITROSession:
    """Manages authentication and session with NetScaler NITRO API"""

    def __init__(
        self,
        hostname: str,
        username: str,
        password: str,
        ssl: bool = True,
        port: Optional[int] = None,
        timeout: int = 15,
        verify_ssl: bool = True,
    ):
        """
        Initialize NITRO session

        Args:
            hostname: NetScaler hostname or IP address
            username: Username for authentication
            password: Password for authentication
            ssl: Use HTTPS (default: True)
            port: Custom port (default: 80 for HTTP, 443 for HTTPS)
            timeout: Request timeout in seconds
            verify_ssl: Verify SSL certificates (default: True)
        """
        self.hostname = hostname
        self.username = username
        self.password = password
        self.ssl = ssl
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        # Determine port
        if port:
            self.port = port
        else:
            self.port = 443 if ssl else 80

        # Build base URL
        protocol = "https" if ssl else "http"
        self.base_url = f"{protocol}://{hostname}:{self.port}/nitro/v1"

        # Session state
        self.session = requests.Session()
        self.session_id: Optional[str] = None
        self.is_logged_in = False

    def login(self) -> None:
        """
        Authenticate with NetScaler and establish session

        Raises:
            NITROAuthenticationError: If login fails
            NITROConnectionError: If connection fails
            NITROTimeoutError: If request times out
        """
        login_url = f"{self.base_url}/config/login"
        login_data = {
            "login": {
                "username": self.username,
                "password": self.password,
            }
        }

        try:
            response = self.session.post(
                login_url,
                json=login_data,
                timeout=self.timeout,
                verify=self.verify_ssl,
            )

            # Check HTTP status
            if response.status_code == 401:
                raise NITROAuthenticationError(f"Authentication failed for user '{self.username}'")

            if response.status_code != 201:
                raise NITROAuthenticationError(
                    f"Login failed with status {response.status_code}: {response.text}"
                )

            # Extract session ID from Set-Cookie header or response
            if "Set-Cookie" in response.headers:
                # Session ID is in cookie
                for cookie in response.cookies:
                    if cookie.name in ["NITRO_AUTH_TOKEN", "sessionid"]:
                        self.session_id = cookie.value
                        break

            self.is_logged_in = True

        except requests.exceptions.Timeout as e:
            raise NITROTimeoutError(f"Login request timed out: {e}") from e
        except requests.exceptions.ConnectionError as e:
            raise NITROConnectionError(f"Connection failed: {e}") from e
        except requests.exceptions.RequestException as e:
            raise NITROConnectionError(f"Request failed: {e}") from e

    def logout(self) -> None:
        """
        Logout from NetScaler and clear session

        Note: Logout failures are silently ignored to avoid
        masking the actual error if called during exception handling.
        """
        if not self.is_logged_in:
            return

        logout_url = f"{self.base_url}/config/logout"
        logout_data = {"logout": {}}

        try:
            self.session.post(
                logout_url,
                json=logout_data,
                timeout=self.timeout,
                verify=self.verify_ssl,
            )
        except Exception:
            # Silently ignore logout errors
            pass
        finally:
            self.is_logged_in = False
            self.session_id = None

    def __enter__(self):
        """Context manager entry"""
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.logout()
        return False
