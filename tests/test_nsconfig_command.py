"""
Tests for nsconfig command
"""

from argparse import Namespace
from unittest.mock import Mock

from check_netscaler.commands.nsconfig import NSConfigCommand
from check_netscaler.constants import STATE_OK, STATE_UNKNOWN, STATE_WARNING


class TestNSConfigCommand:
    """Test nsconfig check command"""

    def create_mock_client(self):
        """Create a mock NITRO client"""
        client = Mock()
        client.get_config = Mock()
        return client

    def create_args(self):
        """Create mock arguments"""
        return Namespace(
            command="nsconfig",
            separator=".",
        )

    def test_no_unsaved_changes(self):
        """Test when there are no unsaved changes"""
        client = self.create_mock_client()
        client.get_config.return_value = {"nsconfig": {"configchanged": False}}

        args = self.create_args()
        command = NSConfigCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "No unsaved" in result.message
        client.get_config.assert_called_once_with("nsconfig")

    def test_unsaved_changes(self):
        """Test when there are unsaved changes"""
        client = self.create_mock_client()
        client.get_config.return_value = {"nsconfig": {"configchanged": True}}

        args = self.create_args()
        command = NSConfigCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING
        assert "Unsaved configuration changes" in result.message

    def test_configchanged_field_missing(self):
        """Test when configchanged field is not present"""
        client = self.create_mock_client()
        client.get_config.return_value = {"nsconfig": {}}  # No configchanged field

        args = self.create_args()
        command = NSConfigCommand(client, args)
        result = command.execute()

        # Should assume unsaved changes (warning)
        assert result.status == STATE_WARNING
        assert "Unsaved configuration changes" in result.message

    def test_nsconfig_as_list(self):
        """Test when nsconfig is returned as a list"""
        client = self.create_mock_client()
        client.get_config.return_value = {"nsconfig": [{"configchanged": False}]}

        args = self.create_args()
        command = NSConfigCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK

    def test_nsconfig_list_with_changes(self):
        """Test when nsconfig list has unsaved changes"""
        client = self.create_mock_client()
        client.get_config.return_value = {"nsconfig": [{"configchanged": True}]}

        args = self.create_args()
        command = NSConfigCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING

    def test_empty_nsconfig_list(self):
        """Test when nsconfig list is empty"""
        client = self.create_mock_client()
        client.get_config.return_value = {"nsconfig": []}

        args = self.create_args()
        command = NSConfigCommand(client, args)
        result = command.execute()

        # Empty list means no configchanged field
        assert result.status == STATE_WARNING

    def test_nsconfig_not_in_response(self):
        """Test when nsconfig is not in API response"""
        client = self.create_mock_client()
        client.get_config.return_value = {}

        args = self.create_args()
        command = NSConfigCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "not found" in result.message

    def test_api_error(self):
        """Test when API returns an error"""
        from check_netscaler.client.exceptions import NITROAPIError

        client = self.create_mock_client()
        client.get_config.side_effect = NITROAPIError("API Error")

        args = self.create_args()
        command = NSConfigCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Error checking nsconfig" in result.message

    def test_unexpected_exception(self):
        """Test handling of unexpected exceptions"""
        client = self.create_mock_client()
        client.get_config.side_effect = Exception("Unexpected error")

        args = self.create_args()
        command = NSConfigCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Unexpected error" in result.message

    def test_configchanged_false_string(self):
        """Test when configchanged is string 'false' (edge case)"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "nsconfig": {"configchanged": "false"}  # String, not boolean
        }

        args = self.create_args()
        command = NSConfigCommand(client, args)
        result = command.execute()

        # Non-empty string is truthy in Python
        assert result.status == STATE_WARNING

    def test_configchanged_zero(self):
        """Test when configchanged is 0 (falsy)"""
        client = self.create_mock_client()
        client.get_config.return_value = {"nsconfig": {"configchanged": 0}}

        args = self.create_args()
        command = NSConfigCommand(client, args)
        result = command.execute()

        # 0 is falsy, should be OK
        assert result.status == STATE_OK
