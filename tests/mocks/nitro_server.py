"""
Mock NetScaler NITRO API Server

This mock server simulates the NetScaler NITRO REST API for testing purposes.
It can be used standalone or via pytest fixtures.

Usage:
    # Standalone mode
    python -m tests.mocks.nitro_server --port 8080

    # In pytest tests
    from tests.mocks.nitro_server import MockNITROServer
    server = MockNITROServer(port=8080)
    server.start()
"""

import argparse
import json
import threading
from pathlib import Path
from typing import Dict, Optional

from flask import Flask, jsonify, request


class MockNITROServer:
    """Mock NITRO API Server"""

    # Resource-specific identifier field names
    # Most resources use "name", but some use different fields
    RESOURCE_ID_FIELDS = {
        "sslcertkey": "certkey",
        # Add more resource-specific mappings here if needed
    }

    def __init__(self, port: int = 8080, host: str = "127.0.0.1"):
        """
        Initialize mock server

        Args:
            port: Port to listen on
            host: Host to bind to
        """
        self.port = port
        self.host = host
        self.app = Flask(__name__)
        self.fixtures_dir = Path(__file__).parent / "fixtures"
        self.sessions: Dict[str, Dict] = {}  # Session cookie -> user info
        self.thread: Optional[threading.Thread] = None

        # Setup routes
        self._setup_routes()

    def _setup_routes(self):
        """Setup Flask routes"""

        @self.app.route("/nitro/v1/config/login", methods=["POST"])
        def login():
            """Handle login requests"""
            data = request.get_json()
            login_data = data.get("login", {})
            username = login_data.get("username")
            password = login_data.get("password")

            # Simple auth - accept nsroot/nsroot or any user/pass for testing
            if username and password:
                session_id = f"session_{len(self.sessions) + 1}"
                self.sessions[session_id] = {"username": username}

                response = jsonify({"errorcode": 0, "message": "Done", "sessionid": session_id})
                response.set_cookie("NITRO_AUTH_TOKEN", session_id)
                response.status_code = 201  # NetScaler returns 201 for successful login
                return response

            return jsonify({"errorcode": 444, "message": "Invalid username or password"}), 401

        @self.app.route("/nitro/v1/config/logout", methods=["POST"])
        def logout():
            """Handle logout requests"""
            session_id = request.cookies.get("NITRO_AUTH_TOKEN")
            if session_id in self.sessions:
                del self.sessions[session_id]
            return jsonify({"errorcode": 0, "message": "Done"})

        @self.app.route("/nitro/v1/config/<resource_type>", methods=["GET"])
        @self.app.route("/nitro/v1/config/<resource_type>/<resource_name>", methods=["GET"])
        def get_config(resource_type, resource_name=None):
            """Handle config GET requests"""
            return self._handle_get("config", resource_type, resource_name)

        @self.app.route("/nitro/v1/stat/<resource_type>", methods=["GET"])
        @self.app.route("/nitro/v1/stat/<resource_type>/<resource_name>", methods=["GET"])
        def get_stat(resource_type, resource_name=None):
            """Handle stat GET requests"""
            return self._handle_get("stat", resource_type, resource_name)

    def _handle_get(self, endpoint: str, resource_type: str, resource_name: Optional[str]):
        """
        Handle GET requests for config or stat endpoints

        Args:
            endpoint: 'config' or 'stat'
            resource_type: Type of resource (e.g., 'lbvserver')
            resource_name: Specific resource name (optional)
        """
        # Check authentication
        session_id = request.cookies.get("NITRO_AUTH_TOKEN")
        if session_id not in self.sessions:
            return jsonify({"errorcode": 444, "message": "Not authenticated"}), 401

        # Parse query arguments (e.g., args=filelocation:/nsconfig/license)
        args_param = request.args.get("args")
        query_params = self._parse_args(args_param) if args_param else {}

        # Load fixture
        fixture_data = self._load_fixture(endpoint, resource_type, resource_name, query_params)

        if fixture_data is None:
            return (
                jsonify({"errorcode": 258, "message": f"No such resource [{resource_type}]"}),
                404,
            )

        return jsonify(fixture_data)

    def _parse_args(self, args_str: str) -> Dict:
        """
        Parse NITRO args parameter

        Example: "filelocation:/nsconfig/license,filename:license.lic"
        Returns: {"filelocation": "/nsconfig/license", "filename": "license.lic"}
        """
        params = {}
        for part in args_str.split(","):
            if ":" in part:
                key, value = part.split(":", 1)
                params[key.strip()] = value.strip()
        return params

    def _load_fixture(
        self,
        endpoint: str,
        resource_type: str,
        resource_name: Optional[str],
        query_params: Dict,
    ) -> Optional[Dict]:
        """
        Load fixture data from JSON files

        Args:
            endpoint: 'config' or 'stat'
            resource_type: Type of resource
            resource_name: Specific resource name
            query_params: Parsed query parameters

        Returns:
            Fixture data or None if not found
        """
        # Special handling for systemfile with query params
        if resource_type == "systemfile" and query_params:
            return self._load_systemfile_fixture(query_params)

        # Build fixture path
        fixture_file = self.fixtures_dir / endpoint / f"{resource_type}.json"

        if not fixture_file.exists():
            return None

        with open(fixture_file, "r") as f:
            data = json.load(f)

        # If resource_name specified, filter results
        if resource_name and resource_type in data:
            # Get the correct identifier field for this resource type
            id_field = self.RESOURCE_ID_FIELDS.get(resource_type, "name")

            resources = data[resource_type]
            if isinstance(resources, list):
                # Filter list by identifier field
                filtered = [r for r in resources if r.get(id_field) == resource_name]
                if filtered:
                    # Always return as list for consistency (some commands expect list)
                    data[resource_type] = filtered
                else:
                    return None
            elif isinstance(resources, dict):
                # Single resource, check identifier field - wrap in list
                if resources.get(id_field) == resource_name:
                    data[resource_type] = [resources]
                else:
                    return None

        return data

    def _load_systemfile_fixture(self, query_params: Dict) -> Optional[Dict]:
        """
        Special handler for systemfile with filelocation/filename params

        Args:
            query_params: Dict with filelocation and optionally filename

        Returns:
            Fixture data for systemfile
        """
        filelocation = query_params.get("filelocation", "")
        filename = query_params.get("filename", "")

        # Load systemfile fixture
        fixture_file = self.fixtures_dir / "config" / "systemfile.json"
        if not fixture_file.exists():
            return None

        with open(fixture_file, "r") as f:
            data = json.load(f)

        # Filter by filelocation
        if "systemfile" in data and isinstance(data["systemfile"], list):
            files = data["systemfile"]

            # Filter by filelocation
            if filelocation:
                files = [f for f in files if f.get("filelocation") == filelocation]

            # Filter by filename
            if filename:
                files = [f for f in files if f.get("filename") == filename]

            # Always return as list for consistency
            data["systemfile"] = files

        return data

    def start(self, threaded: bool = True):
        """
        Start the mock server

        Args:
            threaded: If True, run in background thread. If False, block.
        """
        if threaded:
            self.thread = threading.Thread(
                target=lambda: self.app.run(host=self.host, port=self.port, debug=False),
                daemon=True,
            )
            self.thread.start()
        else:
            self.app.run(host=self.host, port=self.port, debug=True)

    def stop(self):
        """Stop the mock server (if running in thread)"""
        # Flask doesn't have a clean way to stop from thread
        # In tests, we rely on daemon threads being killed
        pass

    def get_url(self) -> str:
        """Get base URL of the server"""
        return f"http://{self.host}:{self.port}"


def main():
    """CLI entry point for standalone mode"""
    parser = argparse.ArgumentParser(description="Mock NetScaler NITRO API Server")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    args = parser.parse_args()

    server = MockNITROServer(port=args.port, host=args.host)
    print(f"Mock NITRO API Server starting on {server.get_url()}")
    print(f"Fixtures directory: {server.fixtures_dir}")
    print("\nEndpoints:")
    print(f"  POST {server.get_url()}/nitro/v1/config/login")
    print(f"  POST {server.get_url()}/nitro/v1/config/logout")
    print(f"  GET  {server.get_url()}/nitro/v1/config/<resource_type>")
    print(f"  GET  {server.get_url()}/nitro/v1/stat/<resource_type>")
    print("\nPress Ctrl+C to stop")

    try:
        server.start(threaded=False)
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    main()
