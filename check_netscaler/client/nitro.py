"""
NITRO API client for NetScaler
"""

from typing import Any, Dict, Optional

import requests

from check_netscaler.client.exceptions import (
    NITROAPIError,
    NITROConnectionError,
    NITROPermissionError,
    NITROResourceNotFoundError,
    NITROTimeoutError,
)
from check_netscaler.client.session import NITROSession


class NITROClient:
    """Client for NetScaler NITRO REST API"""

    def __init__(
        self,
        hostname: str,
        username: str,
        password: str,
        ssl: bool = True,
        port: Optional[int] = None,
        timeout: int = 15,
        verify_ssl: bool = True,
        api_version: str = "v1",
    ):
        """
        Initialize NITRO API client

        Args:
            hostname: NetScaler hostname or IP address
            username: Username for authentication
            password: Password for authentication
            ssl: Use HTTPS (default: True)
            port: Custom port (default: 80 for HTTP, 443 for HTTPS)
            timeout: Request timeout in seconds
            verify_ssl: Verify SSL certificates (default: True)
            api_version: API version (default: v1)
        """
        self.session = NITROSession(
            hostname=hostname,
            username=username,
            password=password,
            ssl=ssl,
            port=port,
            timeout=timeout,
            verify_ssl=verify_ssl,
        )
        self.api_version = api_version

    def login(self) -> None:
        """Authenticate with NetScaler"""
        self.session.login()

    def logout(self) -> None:
        """Logout from NetScaler"""
        self.session.logout()

    def get(
        self,
        resource_type: str,
        resource_name: Optional[str] = None,
        endpoint: str = "stat",
        url_options: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Perform GET request to NITRO API

        Args:
            resource_type: Type of resource (e.g., 'lbvserver', 'service')
            resource_name: Specific resource name (optional)
            endpoint: API endpoint type ('stat' or 'config')
            url_options: Additional URL options (e.g., 'args=detail:true')

        Returns:
            API response as dictionary

        Raises:
            NITROAPIError: If API returns an error
            NITROResourceNotFoundError: If resource not found (404)
            NITROPermissionError: If insufficient permissions (403)
            NITROConnectionError: If connection fails
            NITROTimeoutError: If request times out
        """
        if not self.session.is_logged_in:
            raise NITROAPIError("Not logged in. Call login() first.")

        # Build URL
        url_parts = [self.session.base_url, endpoint, resource_type]
        if resource_name:
            url_parts.append(resource_name)

        url = "/".join(url_parts)

        if url_options:
            url = f"{url}?{url_options}"

        try:
            response = self.session.session.get(
                url,
                timeout=self.session.timeout,
                verify=self.session.verify_ssl,
            )

            # Handle HTTP errors
            if response.status_code == 404:
                raise NITROResourceNotFoundError(
                    f"Resource not found: {resource_type}"
                    + (f"/{resource_name}" if resource_name else "")
                )

            if response.status_code == 403:
                raise NITROPermissionError(f"Insufficient permissions to access {resource_type}")

            if response.status_code >= 400:
                raise NITROAPIError(
                    f"API error {response.status_code}: {response.text}",
                    error_code=response.status_code,
                )

            # Parse JSON response
            data = response.json()

            # Check for NITRO error in response
            if "errorcode" in data and data["errorcode"] != 0:
                error_msg = data.get("message", "Unknown error")
                error_code = data.get("errorcode")
                raise NITROAPIError(
                    f"NITRO API error {error_code}: {error_msg}",
                    error_code=error_code,
                    response=data,
                )

            return data

        except requests.exceptions.Timeout as e:
            raise NITROTimeoutError(f"Request timed out: {e}") from e
        except requests.exceptions.ConnectionError as e:
            raise NITROConnectionError(f"Connection failed: {e}") from e
        except requests.exceptions.RequestException as e:
            raise NITROConnectionError(f"Request failed: {e}") from e

    def get_stat(
        self,
        resource_type: str,
        resource_name: Optional[str] = None,
        url_options: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get statistics for a resource

        Args:
            resource_type: Type of resource
            resource_name: Specific resource name (optional)
            url_options: Additional URL options

        Returns:
            Statistics data
        """
        return self.get(resource_type, resource_name, endpoint="stat", url_options=url_options)

    def get_config(
        self,
        resource_type: str,
        resource_name: Optional[str] = None,
        url_options: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get configuration for a resource

        Args:
            resource_type: Type of resource
            resource_name: Specific resource name (optional)
            url_options: Additional URL options

        Returns:
            Configuration data
        """
        return self.get(resource_type, resource_name, endpoint="config", url_options=url_options)

    def __enter__(self):
        """Context manager entry"""
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.logout()
        return False
