"""
Tests for hwinfo command
"""

from argparse import Namespace
from unittest.mock import Mock

from check_netscaler.commands.hwinfo import HWInfoCommand
from check_netscaler.constants import STATE_OK, STATE_UNKNOWN


class TestHWInfoCommand:
    """Test hwinfo check command"""

    def create_mock_client(self):
        """Create a mock NITRO client"""
        client = Mock()
        client.get_config = Mock()
        return client

    def create_args(self):
        """Create mock arguments"""
        return Namespace(
            command="hwinfo",
            separator=".",
        )

    def test_complete_hardware_info(self):
        """Test with complete hardware and version information"""
        client = self.create_mock_client()

        # Mock responses for both API calls
        def mock_get_config(objecttype):
            if objecttype == "nshardware":
                return {
                    "nshardware": {
                        "hwdescription": "NetScaler VPX",
                        "sysid": "NS10.1",
                        "manufactureyear": "2024",
                        "manufacturemonth": "12",
                        "manufactureday": "04",
                        "cpufrequncy": "2400",
                        "serialno": "ABC123456789",
                    }
                }
            elif objecttype == "nsversion":
                return {
                    "nsversion": {
                        "version": "NS13.1: Build 48.47.nc, Date: Dec 15 2023",
                    }
                }

        client.get_config.side_effect = mock_get_config

        args = self.create_args()
        command = HWInfoCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "Platform: NetScaler VPX NS10.1" in result.message
        assert "Manufactured on: 2024/12/04" in result.message
        assert "CPU: 2400MHz" in result.message
        assert "Serial no: ABC123456789" in result.message
        assert "Build Version: NS13.1: Build 48.47.nc" in result.message

    def test_hardware_as_list(self):
        """Test when hardware is returned as a list"""
        client = self.create_mock_client()

        def mock_get_config(objecttype):
            if objecttype == "nshardware":
                return {
                    "nshardware": [
                        {
                            "hwdescription": "NetScaler VPX",
                            "sysid": "NS10.1",
                            "manufactureyear": "2024",
                            "manufacturemonth": "12",
                            "manufactureday": "04",
                            "cpufrequncy": "2400",
                            "serialno": "ABC123",
                        }
                    ]
                }
            elif objecttype == "nsversion":
                return {"nsversion": [{"version": "NS13.1"}]}

        client.get_config.side_effect = mock_get_config

        args = self.create_args()
        command = HWInfoCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "Platform: NetScaler VPX NS10.1" in result.message

    def test_minimal_hardware_info(self):
        """Test with minimal hardware information"""
        client = self.create_mock_client()

        def mock_get_config(objecttype):
            if objecttype == "nshardware":
                return {
                    "nshardware": {
                        "hwdescription": "NetScaler VPX",
                    }
                }
            elif objecttype == "nsversion":
                return {"nsversion": {"version": "NS13.1"}}

        client.get_config.side_effect = mock_get_config

        args = self.create_args()
        command = HWInfoCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "Platform: NetScaler VPX" in result.message
        assert "Build Version: NS13.1" in result.message
        # Optional fields should not appear
        assert "Manufactured on:" not in result.message
        assert "CPU:" not in result.message
        assert "Serial no:" not in result.message

    def test_missing_hardware_data(self):
        """Test when nshardware is not in API response"""
        client = self.create_mock_client()
        client.get_config.return_value = {}

        args = self.create_args()
        command = HWInfoCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "nshardware data not found" in result.message

    def test_missing_version_data(self):
        """Test when nsversion is not in API response"""
        client = self.create_mock_client()

        def mock_get_config(objecttype):
            if objecttype == "nshardware":
                return {
                    "nshardware": {
                        "hwdescription": "NetScaler VPX",
                    }
                }
            elif objecttype == "nsversion":
                return {}

        client.get_config.side_effect = mock_get_config

        args = self.create_args()
        command = HWInfoCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "nsversion data not found" in result.message

    def test_empty_hardware_list(self):
        """Test when nshardware list is empty"""
        client = self.create_mock_client()

        def mock_get_config(objecttype):
            if objecttype == "nshardware":
                return {"nshardware": []}
            elif objecttype == "nsversion":
                return {"nsversion": {"version": "NS13.1"}}

        client.get_config.side_effect = mock_get_config

        args = self.create_args()
        command = HWInfoCommand(client, args)
        result = command.execute()

        # Empty list means empty dict, should still work with minimal info
        assert result.status == STATE_OK
        assert "Platform: Unknown" in result.message

    def test_empty_version_list(self):
        """Test when nsversion list is empty"""
        client = self.create_mock_client()

        def mock_get_config(objecttype):
            if objecttype == "nshardware":
                return {"nshardware": {"hwdescription": "NetScaler VPX"}}
            elif objecttype == "nsversion":
                return {"nsversion": []}

        client.get_config.side_effect = mock_get_config

        args = self.create_args()
        command = HWInfoCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "Build Version: Unknown" in result.message

    def test_api_error_hardware(self):
        """Test when API returns an error for hardware"""
        from check_netscaler.client.exceptions import NITROAPIError

        client = self.create_mock_client()
        client.get_config.side_effect = NITROAPIError("API Error")

        args = self.create_args()
        command = HWInfoCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Error retrieving hardware info" in result.message

    def test_unexpected_exception(self):
        """Test handling of unexpected exceptions"""
        client = self.create_mock_client()
        client.get_config.side_effect = Exception("Unexpected error")

        args = self.create_args()
        command = HWInfoCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Unexpected error" in result.message

    def test_semicolon_separator_in_output(self):
        """Test that output uses semicolon separator"""
        client = self.create_mock_client()

        def mock_get_config(objecttype):
            if objecttype == "nshardware":
                return {
                    "nshardware": {
                        "hwdescription": "NetScaler VPX",
                        "serialno": "ABC123",
                    }
                }
            elif objecttype == "nsversion":
                return {"nsversion": {"version": "NS13.1"}}

        client.get_config.side_effect = mock_get_config

        args = self.create_args()
        command = HWInfoCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        # Check that semicolons are used as separators
        assert "; " in result.message
