"""
Tests for constants module
"""

from check_netscaler.constants import (
    DEFAULT_API_VERSION,
    DEFAULT_PASSWORD,
    DEFAULT_TIMEOUT,
    DEFAULT_USERNAME,
    STATE_CRITICAL,
    STATE_NAMES,
    STATE_OK,
    STATE_UNKNOWN,
    STATE_WARNING,
)


class TestExitCodes:
    """Test Nagios/Icinga exit codes"""

    def test_exit_codes_values(self):
        """Test that exit codes have correct values"""
        assert STATE_OK == 0
        assert STATE_WARNING == 1
        assert STATE_CRITICAL == 2
        assert STATE_UNKNOWN == 3

    def test_state_names(self):
        """Test state name mappings"""
        assert STATE_NAMES[STATE_OK] == "OK"
        assert STATE_NAMES[STATE_WARNING] == "WARNING"
        assert STATE_NAMES[STATE_CRITICAL] == "CRITICAL"
        assert STATE_NAMES[STATE_UNKNOWN] == "UNKNOWN"

    def test_all_states_have_names(self):
        """Test that all exit codes have corresponding names"""
        for code in [STATE_OK, STATE_WARNING, STATE_CRITICAL, STATE_UNKNOWN]:
            assert code in STATE_NAMES


class TestDefaults:
    """Test default values"""

    def test_default_credentials(self):
        """Test default username and password"""
        assert DEFAULT_USERNAME == "nsroot"
        assert DEFAULT_PASSWORD == "nsroot"

    def test_default_timeout(self):
        """Test default timeout value"""
        assert DEFAULT_TIMEOUT == 15
        assert isinstance(DEFAULT_TIMEOUT, int)

    def test_default_api_version(self):
        """Test default API version"""
        assert DEFAULT_API_VERSION == "v1"
