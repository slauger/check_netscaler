"""
Tests for debug command
"""

import json
from argparse import Namespace
from unittest.mock import Mock

from check_netscaler.commands.debug import DebugCommand
from check_netscaler.constants import STATE_OK, STATE_UNKNOWN


class TestDebugCommand:
    """Test debug check command"""

    def create_mock_client(self):
        """Create a mock NITRO client"""
        client = Mock()
        client.get_stat = Mock()
        client.get_config = Mock()
        return client

    def create_args(self, **kwargs):
        """Create mock arguments"""
        defaults = {
            "command": "debug",
            "objecttype": "system",
            "objectname": None,
            "endpoint": "stat",
            "separator": ".",
        }
        defaults.update(kwargs)
        return Namespace(**defaults)

    def test_debug_stat_endpoint(self):
        """Test debug with stat endpoint"""
        client = self.create_mock_client()
        test_data = {
            "system": {
                "cpuusagepcnt": 50,
                "memusagepcnt": 60,
            }
        }
        client.get_stat.return_value = test_data

        args = self.create_args()
        command = DebugCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "Debug output for system" in result.message
        # Check that JSON is in the output
        assert '"cpuusagepcnt": 50' in result.message
        assert '"memusagepcnt": 60' in result.message
        client.get_stat.assert_called_once_with("system", None)

    def test_debug_config_endpoint(self):
        """Test debug with config endpoint"""
        client = self.create_mock_client()
        test_data = {
            "nsconfig": {
                "configchanged": False,
            }
        }
        client.get_config.return_value = test_data

        args = self.create_args(endpoint="config", objecttype="nsconfig")
        command = DebugCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "Debug output for nsconfig" in result.message
        assert '"configchanged": false' in result.message
        client.get_config.assert_called_once_with("nsconfig", None)

    def test_debug_with_objectname(self):
        """Test debug with specific object name"""
        client = self.create_mock_client()
        test_data = {
            "lbvserver": {
                "name": "test-vserver",
                "state": "UP",
            }
        }
        client.get_stat.return_value = test_data

        args = self.create_args(objecttype="lbvserver", objectname="test-vserver")
        command = DebugCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "Debug output for lbvserver" in result.message
        assert '"name": "test-vserver"' in result.message
        client.get_stat.assert_called_once_with("lbvserver", "test-vserver")

    def test_debug_default_endpoint(self):
        """Test that stat is the default endpoint"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"system": {}}

        args = self.create_args(endpoint=None)
        command = DebugCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        # Should call get_stat, not get_config
        client.get_stat.assert_called_once()
        client.get_config.assert_not_called()

    def test_debug_no_objecttype(self):
        """Test debug without objecttype parameter"""
        client = self.create_mock_client()

        args = self.create_args(objecttype=None)
        command = DebugCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "requires --objecttype parameter" in result.message

    def test_debug_invalid_endpoint(self):
        """Test debug with invalid endpoint"""
        client = self.create_mock_client()

        args = self.create_args(endpoint="invalid")
        command = DebugCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Invalid endpoint" in result.message

    def test_debug_json_formatting(self):
        """Test that JSON is properly formatted"""
        client = self.create_mock_client()
        test_data = {
            "service": [
                {"name": "svc1", "state": "UP"},
                {"name": "svc2", "state": "DOWN"},
            ]
        }
        client.get_stat.return_value = test_data

        args = self.create_args(objecttype="service")
        command = DebugCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        # Verify it's valid JSON by parsing it
        # Extract JSON from message
        json_start = result.message.find("\n") + 1
        json_str = result.message[json_start:]
        parsed = json.loads(json_str)
        assert parsed == test_data

    def test_debug_sorted_keys(self):
        """Test that JSON keys are sorted"""
        client = self.create_mock_client()
        test_data = {
            "system": {
                "zebra": 1,
                "alpha": 2,
                "beta": 3,
            }
        }
        client.get_stat.return_value = test_data

        args = self.create_args()
        command = DebugCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        # Keys should appear in alphabetical order
        message = result.message
        alpha_pos = message.find('"alpha"')
        beta_pos = message.find('"beta"')
        zebra_pos = message.find('"zebra"')
        assert alpha_pos < beta_pos < zebra_pos

    def test_debug_complex_nested_data(self):
        """Test debug with complex nested data structure"""
        client = self.create_mock_client()
        test_data = {
            "lbvserver": [
                {
                    "name": "vserver1",
                    "state": "UP",
                    "stats": {
                        "totalhits": 1000,
                        "totalrequests": 500,
                    },
                }
            ]
        }
        client.get_stat.return_value = test_data

        args = self.create_args(objecttype="lbvserver")
        command = DebugCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        # Should contain nested data
        assert '"totalhits": 1000' in result.message
        assert '"totalrequests": 500' in result.message

    def test_debug_api_error(self):
        """Test when API returns an error"""
        from check_netscaler.client.exceptions import NITROAPIError

        client = self.create_mock_client()
        client.get_stat.side_effect = NITROAPIError("API Error")

        args = self.create_args()
        command = DebugCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Error fetching debug data" in result.message

    def test_debug_unexpected_exception(self):
        """Test handling of unexpected exceptions"""
        client = self.create_mock_client()
        client.get_stat.side_effect = Exception("Unexpected error")

        args = self.create_args()
        command = DebugCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Unexpected error" in result.message

    def test_debug_empty_response(self):
        """Test debug with empty API response"""
        client = self.create_mock_client()
        client.get_stat.return_value = {}

        args = self.create_args()
        command = DebugCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "{}" in result.message

    def test_debug_large_response(self):
        """Test debug with large response"""
        client = self.create_mock_client()
        # Create a response with many items
        test_data = {
            "service": [{"name": f"service{i}", "state": "UP", "port": 80 + i} for i in range(100)]
        }
        client.get_stat.return_value = test_data

        args = self.create_args(objecttype="service")
        command = DebugCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        # Should contain all 100 services
        assert '"name": "service0"' in result.message
        assert '"name": "service99"' in result.message
