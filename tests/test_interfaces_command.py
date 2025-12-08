"""
Tests for interfaces command
"""

from argparse import Namespace
from unittest.mock import Mock

from check_netscaler.commands.interfaces import InterfacesCommand
from check_netscaler.constants import STATE_CRITICAL, STATE_OK, STATE_UNKNOWN


class TestInterfacesCommand:
    """Test interfaces check command"""

    def create_mock_client(self):
        """Create a mock NITRO client"""
        client = Mock()
        client.get_config = Mock()
        client.get_stat = Mock()
        return client

    def create_args(self, **kwargs):
        """Create mock arguments"""
        defaults = {
            "command": "interfaces",
            "endpoint": None,
            "separator": ".",
            "filter": None,
            "limit": None,
        }
        defaults.update(kwargs)
        return Namespace(**defaults)

    def test_all_interfaces_up(self):
        """Test when all interfaces are UP"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "interface": [
                {
                    "devicename": "0/1",
                    "linkstate": "1",
                    "intfstate": "1",
                    "state": "ENABLED",
                    "actspeed": "1000",
                    "actualmtu": "1500",
                    "vlan": "1",
                    "intftype": "Ethernet",
                    "rxbytes": "123456",
                    "txbytes": "789012",
                    "rxerrors": "0",
                    "txerrors": "0",
                }
            ]
        }

        args = self.create_args()
        command = InterfacesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "device: 0/1" in result.message
        assert "speed: 1000" in result.message
        assert "MTU: 1500" in result.message
        assert "ENABLED" in result.message
        # Check perfdata
        assert "0/1.rxbytes" in result.perfdata
        assert result.perfdata["0/1.rxbytes"] == 123456.0

    def test_interface_linkstate_down(self):
        """Test interface with linkstate DOWN"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "interface": [
                {
                    "devicename": "0/1",
                    "linkstate": "0",  # DOWN
                    "intfstate": "1",
                    "state": "ENABLED",
                    "actspeed": "Auto",
                    "actualmtu": "1500",
                    "vlan": "1",
                    "intftype": "Ethernet",
                }
            ]
        }

        args = self.create_args()
        command = InterfacesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert 'linkstate "DOWN"' in result.message

    def test_interface_intfstate_down(self):
        """Test interface with intfstate DOWN"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "interface": [
                {
                    "devicename": "0/1",
                    "linkstate": "1",
                    "intfstate": "0",  # DOWN
                    "state": "ENABLED",
                    "actspeed": "1000",
                    "actualmtu": "1500",
                    "vlan": "1",
                    "intftype": "Ethernet",
                }
            ]
        }

        args = self.create_args()
        command = InterfacesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert 'intfstate "DOWN"' in result.message

    def test_interface_disabled(self):
        """Test interface with state DISABLED"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "interface": [
                {
                    "devicename": "0/1",
                    "linkstate": "1",
                    "intfstate": "1",
                    "state": "DISABLED",
                    "actspeed": "Auto",
                    "actualmtu": "1500",
                    "vlan": "1",
                    "intftype": "Ethernet",
                }
            ]
        }

        args = self.create_args()
        command = InterfacesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert 'state "DISABLED"' in result.message

    def test_multiple_interfaces_all_ok(self):
        """Test multiple interfaces, all OK"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "interface": [
                {
                    "devicename": "0/1",
                    "linkstate": "1",
                    "intfstate": "1",
                    "state": "ENABLED",
                    "actspeed": "1000",
                    "actualmtu": "1500",
                    "vlan": "1",
                    "intftype": "Ethernet",
                },
                {
                    "devicename": "0/2",
                    "linkstate": "1",
                    "intfstate": "1",
                    "state": "ENABLED",
                    "actspeed": "1000",
                    "actualmtu": "1500",
                    "vlan": "2",
                    "intftype": "Ethernet",
                },
            ]
        }

        args = self.create_args()
        command = InterfacesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "device: 0/1" in result.message
        assert "device: 0/2" in result.message

    def test_multiple_interfaces_one_down(self):
        """Test multiple interfaces with one DOWN"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "interface": [
                {
                    "devicename": "0/1",
                    "linkstate": "1",
                    "intfstate": "1",
                    "state": "ENABLED",
                    "actspeed": "1000",
                    "actualmtu": "1500",
                    "vlan": "1",
                    "intftype": "Ethernet",
                },
                {
                    "devicename": "0/2",
                    "linkstate": "0",  # DOWN
                    "intfstate": "1",
                    "state": "ENABLED",
                    "actspeed": "Auto",
                    "actualmtu": "1500",
                    "vlan": "2",
                    "intftype": "Ethernet",
                },
            ]
        }

        args = self.create_args()
        command = InterfacesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert 'interface 0/2 has linkstate "DOWN"' in result.message
        assert "device: 0/1" in result.message
        assert "device: 0/2" in result.message

    def test_interface_multiple_errors(self):
        """Test interface with multiple errors"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "interface": [
                {
                    "devicename": "0/1",
                    "linkstate": "0",  # DOWN
                    "intfstate": "0",  # DOWN
                    "state": "DISABLED",
                    "actspeed": "Auto",
                    "actualmtu": "1500",
                    "vlan": "1",
                    "intftype": "Ethernet",
                }
            ]
        }

        args = self.create_args()
        command = InterfacesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert 'linkstate "DOWN"' in result.message
        assert 'intfstate "DOWN"' in result.message
        assert 'state "DISABLED"' in result.message

    def test_filter_interfaces(self):
        """Test filtering out interfaces by regex"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "interface": [
                {
                    "devicename": "0/1",
                    "linkstate": "0",  # Would be DOWN
                    "intfstate": "1",
                    "state": "ENABLED",
                    "actspeed": "Auto",
                    "actualmtu": "1500",
                    "vlan": "1",
                    "intftype": "Ethernet",
                },
                {
                    "devicename": "1/1",
                    "linkstate": "1",
                    "intfstate": "1",
                    "state": "ENABLED",
                    "actspeed": "1000",
                    "actualmtu": "1500",
                    "vlan": "2",
                    "intftype": "Ethernet",
                },
            ]
        }

        # Filter out 0/x interfaces
        args = self.create_args(filter=r"^0/")
        command = InterfacesCommand(client, args)
        result = command.execute()

        # 0/1 should be filtered out (even though it's DOWN)
        assert result.status == STATE_OK
        assert "0/1" not in result.message
        assert "1/1" in result.message

    def test_limit_interfaces(self):
        """Test limiting to specific interfaces by regex"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "interface": [
                {
                    "devicename": "0/1",
                    "linkstate": "1",
                    "intfstate": "1",
                    "state": "ENABLED",
                    "actspeed": "1000",
                    "actualmtu": "1500",
                    "vlan": "1",
                    "intftype": "Ethernet",
                },
                {
                    "devicename": "1/1",
                    "linkstate": "0",  # Would be DOWN
                    "intfstate": "1",
                    "state": "ENABLED",
                    "actspeed": "Auto",
                    "actualmtu": "1500",
                    "vlan": "2",
                    "intftype": "Ethernet",
                },
            ]
        }

        # Only check 0/x interfaces
        args = self.create_args(limit=r"^0/")
        command = InterfacesCommand(client, args)
        result = command.execute()

        # Only 0/1 should be checked
        assert result.status == STATE_OK
        assert "0/1" in result.message
        assert "1/1" not in result.message

    def test_interface_as_dict(self):
        """Test when Interface is returned as dict instead of list"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "interface": {
                "devicename": "0/1",
                "linkstate": "1",
                "intfstate": "1",
                "state": "ENABLED",
                "actspeed": "1000",
                "actualmtu": "1500",
                "vlan": "1",
                "intftype": "Ethernet",
            }
        }

        args = self.create_args()
        command = InterfacesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "device: 0/1" in result.message

    def test_no_interfaces_found(self):
        """Test when no interfaces are found"""
        client = self.create_mock_client()
        client.get_config.return_value = {"interface": []}

        args = self.create_args()
        command = InterfacesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "no interfaces found" in result.message

    def test_interface_not_in_response(self):
        """Test when Interface is not in API response"""
        client = self.create_mock_client()
        client.get_config.return_value = {}

        args = self.create_args()
        command = InterfacesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "not found in API response" in result.message

    def test_stat_endpoint(self):
        """Test with stat endpoint"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "interface": [
                {
                    "devicename": "0/1",
                    "linkstate": "1",
                    "intfstate": "1",
                    "state": "ENABLED",
                    "actspeed": "1000",
                    "actualmtu": "1500",
                    "vlan": "1",
                    "intftype": "Ethernet",
                }
            ]
        }

        args = self.create_args(endpoint="stat")
        command = InterfacesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        client.get_stat.assert_called_once()
        client.get_config.assert_not_called()

    def test_invalid_endpoint(self):
        """Test with invalid endpoint"""
        client = self.create_mock_client()

        args = self.create_args(endpoint="invalid")
        command = InterfacesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Invalid endpoint" in result.message

    def test_invalid_filter_regex(self):
        """Test with invalid filter regex"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "interface": [
                {
                    "devicename": "0/1",
                    "linkstate": "1",
                    "intfstate": "1",
                    "state": "ENABLED",
                    "actspeed": "1000",
                    "actualmtu": "1500",
                    "vlan": "1",
                    "intftype": "Ethernet",
                }
            ]
        }

        args = self.create_args(filter="[invalid(")
        command = InterfacesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Invalid filter regex" in result.message

    def test_invalid_limit_regex(self):
        """Test with invalid limit regex"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "interface": [
                {
                    "devicename": "0/1",
                    "linkstate": "1",
                    "intfstate": "1",
                    "state": "ENABLED",
                    "actspeed": "1000",
                    "actualmtu": "1500",
                    "vlan": "1",
                    "intftype": "Ethernet",
                }
            ]
        }

        args = self.create_args(limit="[invalid(")
        command = InterfacesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Invalid limit regex" in result.message

    def test_perfdata_included(self):
        """Test that performance data is included"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "interface": [
                {
                    "devicename": "0/1",
                    "linkstate": "1",
                    "intfstate": "1",
                    "state": "ENABLED",
                    "actspeed": "1000",
                    "actualmtu": "1500",
                    "vlan": "1",
                    "intftype": "Ethernet",
                    "rxbytes": "12345678",
                    "txbytes": "87654321",
                    "rxerrors": "10",
                    "txerrors": "5",
                }
            ]
        }

        args = self.create_args()
        command = InterfacesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "0/1.rxbytes" in result.perfdata
        assert "0/1.txbytes" in result.perfdata
        assert "0/1.rxerrors" in result.perfdata
        assert "0/1.txerrors" in result.perfdata
        assert result.perfdata["0/1.rxbytes"] == 12345678.0
        assert result.perfdata["0/1.txerrors"] == 5.0

    def test_custom_separator(self):
        """Test with custom separator for perfdata"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "interface": [
                {
                    "devicename": "0/1",
                    "linkstate": "1",
                    "intfstate": "1",
                    "state": "ENABLED",
                    "actspeed": "1000",
                    "actualmtu": "1500",
                    "vlan": "1",
                    "intftype": "Ethernet",
                    "rxbytes": "12345678",
                }
            ]
        }

        args = self.create_args(separator="_")
        command = InterfacesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "0/1_rxbytes" in result.perfdata

    def test_missing_optional_fields(self):
        """Test interface with missing optional fields"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "interface": [
                {
                    "devicename": "0/1",
                    "linkstate": "1",
                    "intfstate": "1",
                    "state": "ENABLED",
                    # Missing actspeed, actualmtu, vlan, intftype
                }
            ]
        }

        args = self.create_args()
        command = InterfacesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "N/A" in result.message

    def test_invalid_perfdata_values(self):
        """Test with invalid perfdata values (non-numeric)"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "interface": [
                {
                    "devicename": "0/1",
                    "linkstate": "1",
                    "intfstate": "1",
                    "state": "ENABLED",
                    "actspeed": "1000",
                    "actualmtu": "1500",
                    "vlan": "1",
                    "intftype": "Ethernet",
                    "rxbytes": "invalid",
                    "txbytes": "12345",
                }
            ]
        }

        args = self.create_args()
        command = InterfacesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        # Invalid value should be skipped
        assert "0/1.rxbytes" not in result.perfdata
        # Valid value should be included
        assert "0/1.txbytes" in result.perfdata

    def test_api_error(self):
        """Test when API returns an error"""
        from check_netscaler.client.exceptions import NITROAPIError

        client = self.create_mock_client()
        client.get_config.side_effect = NITROAPIError("API Error")

        args = self.create_args()
        command = InterfacesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Error checking interfaces" in result.message

    def test_unexpected_exception(self):
        """Test handling of unexpected exceptions"""
        client = self.create_mock_client()
        client.get_config.side_effect = Exception("Unexpected error")

        args = self.create_args()
        command = InterfacesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Unexpected error" in result.message

    def test_message_format_with_errors(self):
        """Test message format when there are errors"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "interface": [
                {
                    "devicename": "0/1",
                    "linkstate": "0",
                    "intfstate": "1",
                    "state": "ENABLED",
                    "actspeed": "Auto",
                    "actualmtu": "1500",
                    "vlan": "1",
                    "intftype": "Ethernet",
                }
            ]
        }

        args = self.create_args()
        command = InterfacesCommand(client, args)
        result = command.execute()

        # Message should start with "interfaces:"
        assert result.message.startswith("interfaces:")
        # Errors should come first
        assert 'linkstate "DOWN"' in result.message.split(" - ")[0]

    def test_message_format_no_errors(self):
        """Test message format when there are no errors"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "interface": [
                {
                    "devicename": "0/1",
                    "linkstate": "1",
                    "intfstate": "1",
                    "state": "ENABLED",
                    "actspeed": "1000",
                    "actualmtu": "1500",
                    "vlan": "1",
                    "intftype": "Ethernet",
                }
            ]
        }

        args = self.create_args()
        command = InterfacesCommand(client, args)
        result = command.execute()

        # Message should start with "interfaces:"
        assert result.message.startswith("interfaces:")
        # Should use semicolons as separators
        assert "device: 0/1" in result.message

    def test_linkstate_as_string(self):
        """Test linkstate as string value"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "interface": [
                {
                    "devicename": "0/1",
                    "linkstate": "1",  # Already a string
                    "intfstate": 1,  # As integer
                    "state": "ENABLED",
                    "actspeed": "1000",
                    "actualmtu": "1500",
                    "vlan": "1",
                    "intftype": "Ethernet",
                }
            ]
        }

        args = self.create_args()
        command = InterfacesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK

    def test_missing_linkstate(self):
        """Test when linkstate field is missing"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "interface": [
                {
                    "devicename": "0/1",
                    # Missing linkstate
                    "intfstate": "1",
                    "state": "ENABLED",
                    "actspeed": "1000",
                    "actualmtu": "1500",
                    "vlan": "1",
                    "intftype": "Ethernet",
                }
            ]
        }

        args = self.create_args()
        command = InterfacesCommand(client, args)
        result = command.execute()

        # Should not crash, just skip the linkstate check
        assert result.status == STATE_OK
