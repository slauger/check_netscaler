"""
Tests for servicegroup command
"""

from argparse import Namespace
from unittest.mock import Mock

from check_netscaler.commands.servicegroup import ServiceGroupCommand
from check_netscaler.constants import STATE_CRITICAL, STATE_OK, STATE_UNKNOWN, STATE_WARNING


class TestServiceGroupCommand:
    """Test servicegroup check command"""

    def create_mock_client(self):
        """Create a mock NITRO client"""
        client = Mock()
        client.get_config = Mock()
        return client

    def create_args(self, **kwargs):
        """Create mock arguments"""
        defaults = {
            "command": "servicegroup",
            "objectname": "test-sg",
            "warning": "90",
            "critical": "50",
            "separator": ".",
        }
        defaults.update(kwargs)
        return Namespace(**defaults)

    def test_healthy_servicegroup_all_members_up(self):
        """Test healthy servicegroup with all members UP"""
        client = self.create_mock_client()

        def mock_get_config(objecttype, objectname=None):
            if objecttype == "servicegroup":
                return {
                    "servicegroup": {
                        "servicegroupname": "test-sg",
                        "servicetype": "HTTP",
                        "state": "ENABLED",
                        "servicegroupeffectivestate": "UP",
                        "monstate": "ENABLED",
                        "healthmonitor": "YES",
                    }
                }
            elif objecttype == "servicegroup_servicegroupmember_binding":
                return {
                    "servicegroup_servicegroupmember_binding": [
                        {
                            "servername": "server1",
                            "ip": "192.168.1.10",
                            "port": "80",
                            "state": "ENABLED",
                            "svrstate": "UP",
                        },
                        {
                            "servername": "server2",
                            "ip": "192.168.1.11",
                            "port": "80",
                            "state": "ENABLED",
                            "svrstate": "UP",
                        },
                    ]
                }

        client.get_config.side_effect = mock_get_config

        args = self.create_args()
        command = ServiceGroupCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "test-sg (HTTP)" in result.message
        assert "state: UP" in result.message
        assert "member quorum: 100.00%" in result.message
        assert "(UP/DOWN): 2/0" in result.message
        assert "test-sg.member_quorum" in result.perfdata
        assert result.perfdata["test-sg.member_quorum"] == 100.0

    def test_servicegroup_quorum_warning(self):
        """Test servicegroup with quorum at warning level"""
        client = self.create_mock_client()

        def mock_get_config(objecttype, objectname=None):
            if objecttype == "servicegroup":
                return {
                    "servicegroup": {
                        "servicegroupname": "test-sg",
                        "servicetype": "HTTP",
                        "state": "ENABLED",
                        "servicegroupeffectivestate": "UP",
                        "monstate": "ENABLED",
                        "healthmonitor": "YES",
                    }
                }
            elif objecttype == "servicegroup_servicegroupmember_binding":
                return {
                    "servicegroup_servicegroupmember_binding": [
                        {
                            "servername": "server1",
                            "ip": "192.168.1.10",
                            "port": "80",
                            "state": "ENABLED",
                            "svrstate": "UP",
                        },
                        {
                            "servername": "server2",
                            "ip": "192.168.1.11",
                            "port": "80",
                            "state": "ENABLED",
                            "svrstate": "UP",
                        },
                        {
                            "servername": "server3",
                            "ip": "192.168.1.12",
                            "port": "80",
                            "state": "ENABLED",
                            "svrstate": "UP",
                        },
                        {
                            "servername": "server4",
                            "ip": "192.168.1.13",
                            "port": "80",
                            "state": "ENABLED",
                            "svrstate": "DOWN",
                        },
                    ]
                }

        client.get_config.side_effect = mock_get_config

        args = self.create_args()
        command = ServiceGroupCommand(client, args)
        result = command.execute()

        # 3/4 = 75% which is <= 90% warning threshold
        assert result.status == STATE_WARNING
        assert "member quorum: 75.00%" in result.message
        assert "(UP/DOWN): 3/1" in result.message

    def test_servicegroup_quorum_critical(self):
        """Test servicegroup with quorum at critical level"""
        client = self.create_mock_client()

        def mock_get_config(objecttype, objectname=None):
            if objecttype == "servicegroup":
                return {
                    "servicegroup": {
                        "servicegroupname": "test-sg",
                        "servicetype": "HTTP",
                        "state": "ENABLED",
                        "servicegroupeffectivestate": "UP",
                        "monstate": "ENABLED",
                        "healthmonitor": "YES",
                    }
                }
            elif objecttype == "servicegroup_servicegroupmember_binding":
                return {
                    "servicegroup_servicegroupmember_binding": [
                        {
                            "servername": "server1",
                            "ip": "192.168.1.10",
                            "port": "80",
                            "state": "ENABLED",
                            "svrstate": "UP",
                        },
                        {
                            "servername": "server2",
                            "ip": "192.168.1.11",
                            "port": "80",
                            "state": "ENABLED",
                            "svrstate": "DOWN",
                        },
                        {
                            "servername": "server3",
                            "ip": "192.168.1.12",
                            "port": "80",
                            "state": "ENABLED",
                            "svrstate": "DOWN",
                        },
                        {
                            "servername": "server4",
                            "ip": "192.168.1.13",
                            "port": "80",
                            "state": "ENABLED",
                            "svrstate": "DOWN",
                        },
                    ]
                }

        client.get_config.side_effect = mock_get_config

        args = self.create_args()
        command = ServiceGroupCommand(client, args)
        result = command.execute()

        # 1/4 = 25% which is <= 50% critical threshold
        assert result.status == STATE_CRITICAL
        assert "member quorum: 25.00%" in result.message
        assert "(UP/DOWN): 1/3" in result.message

    def test_servicegroup_state_disabled(self):
        """Test servicegroup with disabled state"""
        client = self.create_mock_client()

        def mock_get_config(objecttype, objectname=None):
            if objecttype == "servicegroup":
                return {
                    "servicegroup": {
                        "servicegroupname": "test-sg",
                        "servicetype": "HTTP",
                        "state": "DISABLED",  # Not healthy
                        "servicegroupeffectivestate": "DOWN",
                        "monstate": "ENABLED",
                        "healthmonitor": "YES",
                    }
                }
            elif objecttype == "servicegroup_servicegroupmember_binding":
                return {
                    "servicegroup_servicegroupmember_binding": [
                        {
                            "servername": "server1",
                            "ip": "192.168.1.10",
                            "port": "80",
                            "state": "ENABLED",
                            "svrstate": "UP",
                        },
                    ]
                }

        client.get_config.side_effect = mock_get_config

        args = self.create_args()
        command = ServiceGroupCommand(client, args)
        result = command.execute()

        # Should be CRITICAL due to servicegroup state
        assert result.status == STATE_CRITICAL
        assert "state is DISABLED" in str(result.long_output)

    def test_servicegroup_effective_state_down(self):
        """Test servicegroup with effective state DOWN"""
        client = self.create_mock_client()

        def mock_get_config(objecttype, objectname=None):
            if objecttype == "servicegroup":
                return {
                    "servicegroup": {
                        "servicegroupname": "test-sg",
                        "servicetype": "HTTP",
                        "state": "ENABLED",
                        "servicegroupeffectivestate": "DOWN",  # Not healthy
                        "monstate": "ENABLED",
                        "healthmonitor": "YES",
                    }
                }
            elif objecttype == "servicegroup_servicegroupmember_binding":
                return {
                    "servicegroup_servicegroupmember_binding": [
                        {
                            "servername": "server1",
                            "ip": "192.168.1.10",
                            "port": "80",
                            "state": "ENABLED",
                            "svrstate": "UP",
                        },
                    ]
                }

        client.get_config.side_effect = mock_get_config

        args = self.create_args()
        command = ServiceGroupCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "effective state is DOWN" in str(result.long_output)

    def test_custom_quorum_thresholds(self):
        """Test with custom quorum thresholds"""
        client = self.create_mock_client()

        def mock_get_config(objecttype, objectname=None):
            if objecttype == "servicegroup":
                return {
                    "servicegroup": {
                        "servicegroupname": "test-sg",
                        "servicetype": "HTTP",
                        "state": "ENABLED",
                        "servicegroupeffectivestate": "UP",
                        "monstate": "ENABLED",
                        "healthmonitor": "YES",
                    }
                }
            elif objecttype == "servicegroup_servicegroupmember_binding":
                return {
                    "servicegroup_servicegroupmember_binding": [
                        {
                            "servername": "server1",
                            "ip": "192.168.1.10",
                            "port": "80",
                            "state": "ENABLED",
                            "svrstate": "UP",
                        },
                        {
                            "servername": "server2",
                            "ip": "192.168.1.11",
                            "port": "80",
                            "state": "ENABLED",
                            "svrstate": "DOWN",
                        },
                    ]
                }

        client.get_config.side_effect = mock_get_config

        # Custom thresholds: 60% warning, 30% critical
        args = self.create_args(warning="60", critical="30")
        command = ServiceGroupCommand(client, args)
        result = command.execute()

        # 1/2 = 50% which is WARNING with these thresholds (50% <= 60%)
        assert result.status == STATE_WARNING
        assert "member quorum: 50.00%" in result.message

    def test_no_objectname(self):
        """Test without objectname specified"""
        client = self.create_mock_client()

        args = self.create_args(objectname=None)
        command = ServiceGroupCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert 'no object name "-n" set' in result.message

    def test_servicegroup_not_found(self):
        """Test when servicegroup is not found"""
        client = self.create_mock_client()
        client.get_config.return_value = {}

        args = self.create_args()
        command = ServiceGroupCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "not found in API response" in result.message

    def test_empty_servicegroup_list(self):
        """Test when servicegroup list is empty"""
        client = self.create_mock_client()
        client.get_config.return_value = {"servicegroup": []}

        args = self.create_args()
        command = ServiceGroupCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "not found" in result.message

    def test_members_not_found(self):
        """Test when servicegroup members are not found"""
        client = self.create_mock_client()

        def mock_get_config(objecttype, objectname=None):
            if objecttype == "servicegroup":
                return {
                    "servicegroup": {
                        "servicegroupname": "test-sg",
                        "servicetype": "HTTP",
                        "state": "ENABLED",
                        "servicegroupeffectivestate": "UP",
                        "monstate": "ENABLED",
                        "healthmonitor": "YES",
                    }
                }
            elif objecttype == "servicegroup_servicegroupmember_binding":
                return {}  # No members

        client.get_config.side_effect = mock_get_config

        args = self.create_args()
        command = ServiceGroupCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "members" in result.message.lower()

    def test_single_member_as_dict(self):
        """Test when single member is returned as dict instead of list"""
        client = self.create_mock_client()

        def mock_get_config(objecttype, objectname=None):
            if objecttype == "servicegroup":
                return {
                    "servicegroup": {
                        "servicegroupname": "test-sg",
                        "servicetype": "HTTP",
                        "state": "ENABLED",
                        "servicegroupeffectivestate": "UP",
                        "monstate": "ENABLED",
                        "healthmonitor": "YES",
                    }
                }
            elif objecttype == "servicegroup_servicegroupmember_binding":
                return {
                    "servicegroup_servicegroupmember_binding": {
                        "servername": "server1",
                        "ip": "192.168.1.10",
                        "port": "80",
                        "state": "ENABLED",
                        "svrstate": "UP",
                    }
                }

        client.get_config.side_effect = mock_get_config

        args = self.create_args()
        command = ServiceGroupCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "member quorum: 100.00%" in result.message

    def test_member_state_disabled(self):
        """Test when member state is disabled"""
        client = self.create_mock_client()

        def mock_get_config(objecttype, objectname=None):
            if objecttype == "servicegroup":
                return {
                    "servicegroup": {
                        "servicegroupname": "test-sg",
                        "servicetype": "HTTP",
                        "state": "ENABLED",
                        "servicegroupeffectivestate": "UP",
                        "monstate": "ENABLED",
                        "healthmonitor": "YES",
                    }
                }
            elif objecttype == "servicegroup_servicegroupmember_binding":
                return {
                    "servicegroup_servicegroupmember_binding": [
                        {
                            "servername": "server1",
                            "ip": "192.168.1.10",
                            "port": "80",
                            "state": "DISABLED",
                            "svrstate": "UP",
                        },
                    ]
                }

        client.get_config.side_effect = mock_get_config

        args = self.create_args()
        command = ServiceGroupCommand(client, args)
        result = command.execute()

        # Member is considered DOWN
        assert result.status == STATE_CRITICAL
        assert "member quorum: 0.00%" in result.message
        assert "(UP/DOWN): 0/1" in result.message

    def test_invalid_warning_threshold(self):
        """Test with invalid warning threshold"""
        client = self.create_mock_client()

        args = self.create_args(warning="invalid")
        command = ServiceGroupCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Invalid warning threshold" in result.message

    def test_invalid_critical_threshold(self):
        """Test with invalid critical threshold"""
        client = self.create_mock_client()

        args = self.create_args(critical="invalid")
        command = ServiceGroupCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Invalid critical threshold" in result.message

    def test_api_error(self):
        """Test when API returns an error"""
        from check_netscaler.client.exceptions import NITROAPIError

        client = self.create_mock_client()
        client.get_config.side_effect = NITROAPIError("API Error")

        args = self.create_args()
        command = ServiceGroupCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Error checking servicegroup" in result.message

    def test_unexpected_exception(self):
        """Test handling of unexpected exceptions"""
        client = self.create_mock_client()
        client.get_config.side_effect = Exception("Unexpected error")

        args = self.create_args()
        command = ServiceGroupCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Unexpected error" in result.message

    def test_long_output_contains_member_details(self):
        """Test that long output contains member details"""
        client = self.create_mock_client()

        def mock_get_config(objecttype, objectname=None):
            if objecttype == "servicegroup":
                return {
                    "servicegroup": {
                        "servicegroupname": "test-sg",
                        "servicetype": "HTTP",
                        "state": "ENABLED",
                        "servicegroupeffectivestate": "UP",
                        "monstate": "ENABLED",
                        "healthmonitor": "YES",
                    }
                }
            elif objecttype == "servicegroup_servicegroupmember_binding":
                return {
                    "servicegroup_servicegroupmember_binding": [
                        {
                            "servername": "server1",
                            "ip": "192.168.1.10",
                            "port": "80",
                            "state": "ENABLED",
                            "svrstate": "UP",
                        },
                        {
                            "servername": "server2",
                            "ip": "192.168.1.11",
                            "port": "8080",
                            "state": "ENABLED",
                            "svrstate": "DOWN",
                        },
                    ]
                }

        client.get_config.side_effect = mock_get_config

        args = self.create_args()
        command = ServiceGroupCommand(client, args)
        result = command.execute()

        # Check that long output contains member details
        long_output_str = "\n".join(result.long_output)
        assert "server1 (192.168.1.10:80)" in long_output_str
        assert "server2 (192.168.1.11:8080)" in long_output_str
        assert "is UP" in long_output_str
        assert "is DOWN" in long_output_str

    def test_custom_separator_in_perfdata(self):
        """Test that custom separator is used in perfdata"""
        client = self.create_mock_client()

        def mock_get_config(objecttype, objectname=None):
            if objecttype == "servicegroup":
                return {
                    "servicegroup": {
                        "servicegroupname": "test-sg",
                        "servicetype": "HTTP",
                        "state": "ENABLED",
                        "servicegroupeffectivestate": "UP",
                        "monstate": "ENABLED",
                        "healthmonitor": "YES",
                    }
                }
            elif objecttype == "servicegroup_servicegroupmember_binding":
                return {
                    "servicegroup_servicegroupmember_binding": [
                        {
                            "servername": "server1",
                            "ip": "192.168.1.10",
                            "port": "80",
                            "state": "ENABLED",
                            "svrstate": "UP",
                        },
                    ]
                }

        client.get_config.side_effect = mock_get_config

        args = self.create_args(separator="_")
        command = ServiceGroupCommand(client, args)
        result = command.execute()

        assert "test-sg_member_quorum" in result.perfdata

    def test_default_thresholds(self):
        """Test that default thresholds are used when not specified"""
        client = self.create_mock_client()

        def mock_get_config(objecttype, objectname=None):
            if objecttype == "servicegroup":
                return {
                    "servicegroup": {
                        "servicegroupname": "test-sg",
                        "servicetype": "HTTP",
                        "state": "ENABLED",
                        "servicegroupeffectivestate": "UP",
                        "monstate": "ENABLED",
                        "healthmonitor": "YES",
                    }
                }
            elif objecttype == "servicegroup_servicegroupmember_binding":
                return {
                    "servicegroup_servicegroupmember_binding": [
                        {
                            "servername": "server1",
                            "ip": "192.168.1.10",
                            "port": "80",
                            "state": "ENABLED",
                            "svrstate": "UP",
                        },
                        {
                            "servername": "server2",
                            "ip": "192.168.1.11",
                            "port": "80",
                            "state": "ENABLED",
                            "svrstate": "UP",
                        },
                        {
                            "servername": "server3",
                            "ip": "192.168.1.12",
                            "port": "80",
                            "state": "ENABLED",
                            "svrstate": "DOWN",
                        },
                    ]
                }

        client.get_config.side_effect = mock_get_config

        args = self.create_args(warning=None, critical=None)
        command = ServiceGroupCommand(client, args)
        result = command.execute()

        # 2/3 = 66.67% which is <= 90% (default warning)
        assert result.status == STATE_WARNING
