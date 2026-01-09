"""
Pytest configuration and shared fixtures
"""

import time

import pytest


@pytest.fixture
def sample_args():
    """Sample CLI arguments for testing"""
    return ["-H", "192.168.1.1", "-C", "state"]


@pytest.fixture
def sample_args_with_auth():
    """Sample CLI arguments with authentication"""
    return ["-H", "192.168.1.1", "-C", "state", "-u", "admin", "-p", "secret", "-s"]


@pytest.fixture
def mock_nitro_server():
    """
    Pytest fixture for Mock NITRO API Server

    Usage:
        def test_something(mock_nitro_server):
            url = mock_nitro_server.get_url()
            # Test against mock server...
    """
    import socket

    from tests.mocks.nitro_server import MockNITROServer

    # Find a free port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]

    server = MockNITROServer(port=port)
    server.start(threaded=True)

    # Give server time to start
    time.sleep(1)

    yield server

    server.stop()
