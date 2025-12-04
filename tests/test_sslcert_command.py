"""
Tests for sslcert command
"""

from argparse import Namespace
from unittest.mock import Mock

from check_netscaler.commands.sslcert import SSLCertCommand
from check_netscaler.constants import STATE_CRITICAL, STATE_OK, STATE_UNKNOWN, STATE_WARNING


class TestSSLCertCommand:
    """Test sslcert check command"""

    def create_mock_client(self):
        """Create a mock NITRO client"""
        client = Mock()
        client.get_config = Mock()
        return client

    def create_args(self, **kwargs):
        """Create mock arguments"""
        defaults = {
            "command": "sslcert",
            "objecttype": "sslcertkey",
            "warning": "30",
            "critical": "10",
            "separator": ".",
            "filter": None,
            "limit": None,
        }
        defaults.update(kwargs)
        return Namespace(**defaults)

    def test_all_certificates_ok(self):
        """Test when all certificates have sufficient lifetime"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "sslcertkey": [
                {"certkey": "cert1", "daystoexpiration": 90},
                {"certkey": "cert2", "daystoexpiration": 60},
                {"certkey": "cert3", "daystoexpiration": 45},
            ]
        }

        args = self.create_args()
        command = SSLCertCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "3 certificate(s) OK" in result.message
        assert "warn=30d" in result.message
        assert "crit=10d" in result.message

    def test_certificate_warning(self):
        """Test when certificate is within warning threshold"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "sslcertkey": [
                {"certkey": "cert1", "daystoexpiration": 90},
                {"certkey": "cert2", "daystoexpiration": 25},  # Warning
            ]
        }

        args = self.create_args()
        command = SSLCertCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING
        assert "WARNING" in result.message
        assert "cert2 expires in 25 days" in result.message

    def test_certificate_critical(self):
        """Test when certificate is within critical threshold"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "sslcertkey": [
                {"certkey": "cert1", "daystoexpiration": 90},
                {"certkey": "cert2", "daystoexpiration": 5},  # Critical
            ]
        }

        args = self.create_args()
        command = SSLCertCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "CRITICAL" in result.message
        assert "cert2 expires in 5 days" in result.message

    def test_certificate_expired(self):
        """Test when certificate is already expired"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "sslcertkey": [
                {"certkey": "expired-cert", "daystoexpiration": 0},
            ]
        }

        args = self.create_args()
        command = SSLCertCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "CRITICAL" in result.message
        assert "expired-cert expired" in result.message

    def test_certificate_negative_days(self):
        """Test when certificate has negative days (expired)"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "sslcertkey": [
                {"certkey": "very-expired", "daystoexpiration": -10},
            ]
        }

        args = self.create_args()
        command = SSLCertCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "very-expired expired" in result.message

    def test_mixed_certificate_states(self):
        """Test with mix of OK, WARNING, and CRITICAL certificates"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "sslcertkey": [
                {"certkey": "cert-ok", "daystoexpiration": 90},
                {"certkey": "cert-warn", "daystoexpiration": 25},
                {"certkey": "cert-crit", "daystoexpiration": 5},
                {"certkey": "cert-expired", "daystoexpiration": 0},
            ]
        }

        args = self.create_args()
        command = SSLCertCommand(client, args)
        result = command.execute()

        # Critical takes precedence
        assert result.status == STATE_CRITICAL
        assert "CRITICAL" in result.message
        assert "cert-crit expires in 5 days" in result.message
        assert "cert-expired expired" in result.message
        assert "WARNING" in result.message
        assert "cert-warn expires in 25 days" in result.message
        # Long output should contain details
        assert len(result.long_output) == 3  # 2 critical, 1 warning

    def test_custom_thresholds(self):
        """Test with custom warning and critical thresholds"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "sslcertkey": [
                {"certkey": "cert1", "daystoexpiration": 50},
            ]
        }

        args = self.create_args(warning="60", critical="20")
        command = SSLCertCommand(client, args)
        result = command.execute()

        # 50 days is below warning threshold of 60
        assert result.status == STATE_WARNING
        assert "cert1 expires in 50 days" in result.message

    def test_at_warning_threshold(self):
        """Test certificate exactly at warning threshold"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "sslcertkey": [
                {"certkey": "cert1", "daystoexpiration": 30},
            ]
        }

        args = self.create_args()
        command = SSLCertCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING

    def test_at_critical_threshold(self):
        """Test certificate exactly at critical threshold"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "sslcertkey": [
                {"certkey": "cert1", "daystoexpiration": 10},
            ]
        }

        args = self.create_args()
        command = SSLCertCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL

    def test_filter_certificates(self):
        """Test filtering out certificates by regex"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "sslcertkey": [
                {"certkey": "prod-cert", "daystoexpiration": 5},  # Would be critical
                {"certkey": "test-cert", "daystoexpiration": 90},
            ]
        }

        # Filter out test certificates
        args = self.create_args(filter="^test-")
        command = SSLCertCommand(client, args)
        result = command.execute()

        # Only prod-cert should be checked
        assert result.status == STATE_CRITICAL
        assert "prod-cert" in result.message
        assert "test-cert" not in result.message

    def test_limit_certificates(self):
        """Test limiting to specific certificates by regex"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "sslcertkey": [
                {"certkey": "prod-cert", "daystoexpiration": 5},  # Critical
                {"certkey": "test-cert", "daystoexpiration": 5},  # Critical but filtered
            ]
        }

        # Only check prod certificates
        args = self.create_args(limit="^prod-")
        command = SSLCertCommand(client, args)
        result = command.execute()

        # Only prod-cert should be checked
        assert result.status == STATE_CRITICAL
        assert "prod-cert" in result.message
        assert "test-cert" not in result.message

    def test_single_certificate_as_dict(self):
        """Test when API returns single certificate as dict"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "sslcertkey": {"certkey": "cert1", "daystoexpiration": 90}
        }

        args = self.create_args()
        command = SSLCertCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK

    def test_no_certificates_found(self):
        """Test when no certificates are found"""
        client = self.create_mock_client()
        client.get_config.return_value = {"sslcertkey": []}

        args = self.create_args()
        command = SSLCertCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "No SSL certificates found" in result.message

    def test_missing_sslcertkey_data(self):
        """Test when sslcertkey is not in API response"""
        client = self.create_mock_client()
        client.get_config.return_value = {}

        args = self.create_args()
        command = SSLCertCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "sslcertkey data not found" in result.message

    def test_certificate_without_expiration(self):
        """Test certificate without daystoexpiration field"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "sslcertkey": [
                {"certkey": "cert1", "daystoexpiration": 90},
                {"certkey": "cert2"},  # No daystoexpiration
            ]
        }

        args = self.create_args()
        command = SSLCertCommand(client, args)
        result = command.execute()

        # Should only check cert1
        assert result.status == STATE_OK
        assert "1 certificate(s) OK" in result.message

    def test_invalid_warning_threshold(self):
        """Test with invalid warning threshold"""
        client = self.create_mock_client()

        args = self.create_args(warning="invalid")
        command = SSLCertCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Invalid warning threshold" in result.message

    def test_invalid_critical_threshold(self):
        """Test with invalid critical threshold"""
        client = self.create_mock_client()

        args = self.create_args(critical="invalid")
        command = SSLCertCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Invalid critical threshold" in result.message

    def test_invalid_filter_regex(self):
        """Test with invalid filter regex"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "sslcertkey": [{"certkey": "cert1", "daystoexpiration": 90}]
        }

        args = self.create_args(filter="[invalid(")
        command = SSLCertCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Invalid filter regex" in result.message

    def test_invalid_limit_regex(self):
        """Test with invalid limit regex"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "sslcertkey": [{"certkey": "cert1", "daystoexpiration": 90}]
        }

        args = self.create_args(limit="[invalid(")
        command = SSLCertCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Invalid limit regex" in result.message

    def test_api_error(self):
        """Test when API returns an error"""
        from check_netscaler.client.exceptions import NITROAPIError

        client = self.create_mock_client()
        client.get_config.side_effect = NITROAPIError("API Error")

        args = self.create_args()
        command = SSLCertCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Error checking SSL certificates" in result.message

    def test_unexpected_exception(self):
        """Test handling of unexpected exceptions"""
        client = self.create_mock_client()
        client.get_config.side_effect = Exception("Unexpected error")

        args = self.create_args()
        command = SSLCertCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Unexpected error" in result.message

    def test_default_thresholds(self):
        """Test that default thresholds are used when not specified"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "sslcertkey": [
                {"certkey": "cert1", "daystoexpiration": 90},
            ]
        }

        args = self.create_args(warning=None, critical=None)
        command = SSLCertCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        # Default thresholds are 30/10
        assert "warn=30d" in result.message
        assert "crit=10d" in result.message

    def test_invalid_daystoexpiration_value(self):
        """Test certificate with invalid daystoexpiration value"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "sslcertkey": [
                {"certkey": "cert1", "daystoexpiration": 90},
                {"certkey": "cert2", "daystoexpiration": "invalid"},
            ]
        }

        args = self.create_args()
        command = SSLCertCommand(client, args)
        result = command.execute()

        # Should skip cert2 and only check cert1
        assert result.status == STATE_OK
        assert "1 certificate(s) OK" in result.message
