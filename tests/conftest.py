"""
Pytest configuration and shared fixtures
"""

import pytest


@pytest.fixture
def sample_args():
    """Sample CLI arguments for testing"""
    return ["-H", "192.168.1.1", "-C", "state"]


@pytest.fixture
def sample_args_with_auth():
    """Sample CLI arguments with authentication"""
    return ["-H", "192.168.1.1", "-C", "state", "-u", "admin", "-p", "secret", "-s"]
