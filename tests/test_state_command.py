"""
Tests for state command
"""

from argparse import Namespace
from unittest.mock import Mock

from check_netscaler.commands.state import StateCommand
from check_netscaler.constants import STATE_CRITICAL, STATE_OK, STATE_UNKNOWN, STATE_WARNING


class TestStateCommand:
    """Test state check command"""

    def create_mock_client(self):
        """Create a mock NITRO client"""
        client = Mock()
        client.get_stat = Mock()
        return client

    def create_args(self, **kwargs):
        """Create mock arguments"""
        defaults = {
            "objecttype": "lbvserver",
            "objectname": None,
            "filter": None,
            "limit": None,
            "separator": ".",
        }
        defaults.update(kwargs)
        return Namespace(**defaults)

    def test_state_all_up(self):
        """Test all objects UP"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "lbvserver": [
                {"name": "vserver1", "state": "UP"},
                {"name": "vserver2", "state": "UP"},
            ]
        }

        args = self.create_args()
        command = StateCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "All 2 lbvserver are UP" in result.message
        assert result.perfdata["total"] == 2
        assert result.perfdata["ok"] == 2
        assert result.perfdata["critical"] == 0

    def test_state_single_up(self):
        """Test single object UP"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"lbvserver": [{"name": "vserver1", "state": "UP"}]}

        args = self.create_args()
        command = StateCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "lbvserver is UP" in result.message

    def test_state_one_down(self):
        """Test one object DOWN"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "lbvserver": [
                {"name": "vserver1", "state": "UP"},
                {"name": "vserver2", "state": "DOWN"},
            ]
        }

        args = self.create_args()
        command = StateCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "1/2 lbvserver CRITICAL" in result.message
        assert "vserver2" in result.message
        assert result.perfdata["critical"] == 1
        assert result.perfdata["ok"] == 1

    def test_state_all_down(self):
        """Test all objects DOWN"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "service": [
                {"name": "svc1", "state": "DOWN"},
                {"name": "svc2", "state": "DOWN"},
            ]
        }

        args = self.create_args(objecttype="service")
        command = StateCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "2/2 service CRITICAL" in result.message
        assert result.perfdata["critical"] == 2

    def test_state_out_of_service(self):
        """Test OUT OF SERVICE state (warning)"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "lbvserver": [
                {"name": "vserver1", "state": "UP"},
                {"name": "vserver2", "state": "OUT OF SERVICE"},
            ]
        }

        args = self.create_args()
        command = StateCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING
        assert "1/2 lbvserver WARNING" in result.message
        assert result.perfdata["warning"] == 1

    def test_state_mixed_statuses(self):
        """Test mix of OK, WARNING, and CRITICAL"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "service": [
                {"name": "svc1", "state": "UP"},
                {"name": "svc2", "state": "DOWN"},
                {"name": "svc3", "state": "OUT OF SERVICE"},
                {"name": "svc4", "state": "UP"},
            ]
        }

        args = self.create_args(objecttype="service")
        command = StateCommand(client, args)
        result = command.execute()

        # CRITICAL takes precedence
        assert result.status == STATE_CRITICAL
        assert "1/4 service CRITICAL" in result.message
        assert "1/4 service WARNING" in result.message

    def test_state_with_filter(self):
        """Test with filter regex"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "lbvserver": [
                {"name": "prod_vserver1", "state": "UP"},
                {"name": "test_vserver1", "state": "DOWN"},
                {"name": "prod_vserver2", "state": "UP"},
            ]
        }

        # Filter out test_ vservers
        args = self.create_args(filter="test_.*")
        command = StateCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert result.perfdata["total"] == 2  # Only prod vservers

    def test_state_with_limit(self):
        """Test with limit regex"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "lbvserver": [
                {"name": "prod_vserver1", "state": "UP"},
                {"name": "test_vserver1", "state": "DOWN"},
                {"name": "prod_vserver2", "state": "UP"},
            ]
        }

        # Limit to prod_ vservers only
        args = self.create_args(limit="prod_.*")
        command = StateCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert result.perfdata["total"] == 2  # Only prod vservers

    def test_state_no_objecttype(self):
        """Test without objecttype specified"""
        client = self.create_mock_client()
        args = self.create_args(objecttype=None)
        command = StateCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "No objecttype specified" in result.message

    def test_state_not_found(self):
        """Test resource not found"""
        from check_netscaler.client.exceptions import NITROResourceNotFoundError

        client = self.create_mock_client()
        client.get_stat.side_effect = NITROResourceNotFoundError("Not found")

        args = self.create_args()
        command = StateCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "not found" in result.message

    def test_state_no_objects_returned(self):
        """Test when API returns no objects"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"lbvserver": []}

        args = self.create_args()
        command = StateCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "No lbvserver objects found" in result.message

    def test_state_long_output(self):
        """Test that long output is generated for multiple objects"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "service": [
                {"name": "svc1", "state": "UP"},
                {"name": "svc2", "state": "DOWN"},
            ]
        }

        args = self.create_args(objecttype="service")
        command = StateCommand(client, args)
        result = command.execute()

        assert len(result.long_output) == 2
        assert "svc1: UP" in result.long_output[0]
        assert "svc2: DOWN" in result.long_output[1]

    def test_state_case_insensitive(self):
        """Test that state matching is case-insensitive"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "lbvserver": [
                {"name": "vserver1", "state": "up"},  # lowercase
                {"name": "vserver2", "state": "Up"},  # mixed case
            ]
        }

        args = self.create_args()
        command = StateCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert result.perfdata["ok"] == 2
