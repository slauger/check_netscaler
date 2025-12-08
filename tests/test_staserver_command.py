"""
Tests for staserver command
"""

from argparse import Namespace
from unittest.mock import Mock

from check_netscaler.commands.staserver import STAServerCommand
from check_netscaler.constants import STATE_CRITICAL, STATE_OK, STATE_UNKNOWN, STATE_WARNING


class TestSTAServerCommand:
    """Test staserver check command"""

    def create_mock_client(self):
        """Create a mock NITRO client"""
        client = Mock()
        client.get_config = Mock()
        client.get_stat = Mock()
        return client

    def create_args(self, **kwargs):
        """Create mock arguments"""
        defaults = {
            "command": "staserver",
            "objecttype": None,
            "objectname": None,
            "endpoint": "config",
            "separator": ".",
            "filter": None,
            "limit": None,
        }
        defaults.update(kwargs)
        return Namespace(**defaults)

    def test_all_staservers_available(self):
        """Test when all STA servers are available"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "vpnglobal_staserver_binding": [
                {"staserver": "sta1.example.com", "staauthid": "auth123"},
                {"staserver": "sta2.example.com", "staauthid": "auth456"},
            ]
        }

        args = self.create_args()
        command = STAServerCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "sta1.example.com OK (auth123)" in result.message
        assert "sta2.example.com OK (auth456)" in result.message

    def test_one_staserver_unavailable(self):
        """Test when one STA server is unavailable"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "vpnglobal_staserver_binding": [
                {"staserver": "sta1.example.com", "staauthid": "auth123"},
                {"staserver": "sta2.example.com", "staauthid": ""},  # Unavailable
            ]
        }

        args = self.create_args()
        command = STAServerCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING
        assert "sta1.example.com OK" in result.message
        assert "sta2.example.com unavailable" in result.message

    def test_all_staservers_unavailable(self):
        """Test when all STA servers are unavailable"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "vpnglobal_staserver_binding": [
                {"staserver": "sta1.example.com", "staauthid": ""},
                {"staserver": "sta2.example.com", "staauthid": ""},
            ]
        }

        args = self.create_args()
        command = STAServerCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "sta1.example.com unavailable" in result.message
        assert "sta2.example.com unavailable" in result.message

    def test_global_staservers_no_objectname(self):
        """Test global STA servers (no objectname specified)"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "vpnglobal_staserver_binding": [
                {"staserver": "sta1.example.com", "staauthid": "auth123"},
            ]
        }

        args = self.create_args(objectname=None)
        command = STAServerCommand(client, args)
        result = command.execute()

        # Should query vpnglobal_staserver_binding
        assert result.status == STATE_OK
        client.get_config.assert_called_once_with("vpnglobal_staserver_binding", None)

    def test_vserver_staservers_with_objectname(self):
        """Test vServer-specific STA servers (objectname specified)"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "vpnvserver_staserver_binding": [
                {"staserver": "sta1.example.com", "staauthid": "auth123"},
            ]
        }

        args = self.create_args(objectname="test-vpn")
        command = STAServerCommand(client, args)
        result = command.execute()

        # Should query vpnvserver_staserver_binding with objectname
        assert result.status == STATE_OK
        client.get_config.assert_called_once_with("vpnvserver_staserver_binding", "test-vpn")

    def test_custom_objecttype(self):
        """Test with custom objecttype specified"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "custom_binding": [
                {"staserver": "sta1.example.com", "staauthid": "auth123"},
            ]
        }

        args = self.create_args(objecttype="custom_binding")
        command = STAServerCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        client.get_config.assert_called_once_with("custom_binding", None)

    def test_single_staserver_as_dict(self):
        """Test when single STA server is returned as dict instead of list"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "vpnglobal_staserver_binding": {"staserver": "sta1.example.com", "staauthid": "auth123"}
        }

        args = self.create_args()
        command = STAServerCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "sta1.example.com OK" in result.message

    def test_no_staservers_found(self):
        """Test when no STA servers are found"""
        client = self.create_mock_client()
        client.get_config.return_value = {"vpnglobal_staserver_binding": []}

        args = self.create_args()
        command = STAServerCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "no staserver found" in result.message

    def test_objecttype_not_found(self):
        """Test when objecttype is not in API response"""
        client = self.create_mock_client()
        client.get_config.return_value = {}

        args = self.create_args()
        command = STAServerCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "not found in API response" in result.message

    def test_filter_staservers(self):
        """Test filtering out STA servers by regex"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "vpnglobal_staserver_binding": [
                {"staserver": "sta1.prod.example.com", "staauthid": ""},  # Would be unavailable
                {"staserver": "sta2.test.example.com", "staauthid": "auth123"},
            ]
        }

        # Filter out test servers
        args = self.create_args(filter=r"\.test\.")
        command = STAServerCommand(client, args)
        result = command.execute()

        # Only prod server should be checked, and it's unavailable
        assert result.status == STATE_CRITICAL
        assert "sta1.prod.example.com" in result.message
        assert "sta2.test.example.com" not in result.message

    def test_limit_staservers(self):
        """Test limiting to specific STA servers by regex"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "vpnglobal_staserver_binding": [
                {"staserver": "sta1.prod.example.com", "staauthid": "auth123"},
                {"staserver": "sta2.test.example.com", "staauthid": ""},  # Would be unavailable
            ]
        }

        # Only check prod servers
        args = self.create_args(limit=r"\.prod\.")
        command = STAServerCommand(client, args)
        result = command.execute()

        # Only prod server should be checked
        assert result.status == STATE_OK
        assert "sta1.prod.example.com" in result.message
        assert "sta2.test.example.com" not in result.message

    def test_staauthid_none(self):
        """Test when staauthid is None (not just empty string)"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "vpnglobal_staserver_binding": [
                {"staserver": "sta1.example.com", "staauthid": None},
            ]
        }

        args = self.create_args()
        command = STAServerCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "unavailable" in result.message

    def test_staauthid_missing(self):
        """Test when staauthid field is missing"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "vpnglobal_staserver_binding": [
                {"staserver": "sta1.example.com"},  # No staauthid field
            ]
        }

        args = self.create_args()
        command = STAServerCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "unavailable" in result.message

    def test_stat_endpoint(self):
        """Test with stat endpoint"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "vpnglobal_staserver_binding": [
                {"staserver": "sta1.example.com", "staauthid": "auth123"},
            ]
        }

        args = self.create_args(endpoint="stat")
        command = STAServerCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        client.get_stat.assert_called_once()
        client.get_config.assert_not_called()

    def test_invalid_endpoint(self):
        """Test with invalid endpoint"""
        client = self.create_mock_client()

        args = self.create_args(endpoint="invalid")
        command = STAServerCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Invalid endpoint" in result.message

    def test_invalid_filter_regex(self):
        """Test with invalid filter regex"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "vpnglobal_staserver_binding": [
                {"staserver": "sta1.example.com", "staauthid": "auth123"},
            ]
        }

        args = self.create_args(filter="[invalid(")
        command = STAServerCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Invalid filter regex" in result.message

    def test_invalid_limit_regex(self):
        """Test with invalid limit regex"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "vpnglobal_staserver_binding": [
                {"staserver": "sta1.example.com", "staauthid": "auth123"},
            ]
        }

        args = self.create_args(limit="[invalid(")
        command = STAServerCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Invalid limit regex" in result.message

    def test_api_error(self):
        """Test when API returns an error"""
        from check_netscaler.client.exceptions import NITROAPIError

        client = self.create_mock_client()
        client.get_config.side_effect = NITROAPIError("API Error")

        args = self.create_args()
        command = STAServerCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Error checking staserver" in result.message

    def test_unexpected_exception(self):
        """Test handling of unexpected exceptions"""
        client = self.create_mock_client()
        client.get_config.side_effect = Exception("Unexpected error")

        args = self.create_args()
        command = STAServerCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Unexpected error" in result.message

    def test_message_format(self):
        """Test that message format is correct"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "vpnglobal_staserver_binding": [
                {"staserver": "sta1.example.com", "staauthid": "auth123"},
                {"staserver": "sta2.example.com", "staauthid": ""},
            ]
        }

        args = self.create_args()
        command = STAServerCommand(client, args)
        result = command.execute()

        # Message should start with "staserver:"
        assert result.message.startswith("staserver:")
        # Should use semicolons as separators
        assert ";" in result.message

    def test_mixed_availability(self):
        """Test with mix of available and unavailable servers"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "vpnglobal_staserver_binding": [
                {"staserver": "sta1.example.com", "staauthid": "auth123"},
                {"staserver": "sta2.example.com", "staauthid": ""},
                {"staserver": "sta3.example.com", "staauthid": "auth789"},
                {"staserver": "sta4.example.com", "staauthid": ""},
            ]
        }

        args = self.create_args()
        command = STAServerCommand(client, args)
        result = command.execute()

        # Some available, some not - should be WARNING
        assert result.status == STATE_WARNING
        assert "sta1.example.com OK" in result.message
        assert "sta2.example.com unavailable" in result.message
        assert "sta3.example.com OK" in result.message
        assert "sta4.example.com unavailable" in result.message
