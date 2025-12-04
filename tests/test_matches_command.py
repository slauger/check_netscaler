"""
Tests for matches/matches_not commands
"""

from argparse import Namespace
from unittest.mock import Mock

from check_netscaler.commands.matches import MatchesCommand
from check_netscaler.constants import STATE_CRITICAL, STATE_OK, STATE_UNKNOWN, STATE_WARNING


class TestMatchesCommand:
    """Test matches and matches_not check commands"""

    def create_mock_client(self):
        """Create a mock NITRO client"""
        client = Mock()
        client.get_stat = Mock()
        client.get_config = Mock()
        return client

    def create_args(self, **kwargs):
        """Create mock arguments"""
        defaults = {
            "command": "matches",
            "objecttype": "hanode",
            "objectname": "hacurstatus",
            "warning": "SECONDARY",
            "critical": "DOWN",
            "endpoint": "stat",
            "separator": ".",
            "label": None,
        }
        defaults.update(kwargs)
        return Namespace(**defaults)

    # Tests for 'matches' command

    def test_matches_critical(self):
        """Test matches when value equals critical"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"hanode": {"hacurstatus": "DOWN"}}

        args = self.create_args()
        command = MatchesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert '"DOWN" matches keyword "DOWN"' in result.message

    def test_matches_warning(self):
        """Test matches when value equals warning"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"hanode": {"hacurstatus": "SECONDARY"}}

        args = self.create_args()
        command = MatchesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING
        assert '"SECONDARY" matches keyword "SECONDARY"' in result.message

    def test_matches_ok(self):
        """Test matches when value doesn't match either threshold"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"hanode": {"hacurstatus": "PRIMARY"}}

        args = self.create_args()
        command = MatchesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert '"PRIMARY"' in result.message
        assert "matches keyword" not in result.message or "PRIMARY" in result.message

    # Tests for 'matches_not' command

    def test_matches_not_critical(self):
        """Test matches_not when value NOT equals critical"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"hanode": {"hacurstatus": "SECONDARY"}}

        args = self.create_args(command="matches_not", critical="PRIMARY")
        command = MatchesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert '"SECONDARY" matches_not keyword "PRIMARY"' in result.message

    def test_matches_not_warning(self):
        """Test matches_not when value NOT equals warning"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"hanode": {"hacurstatus": "PRIMARY"}}

        args = self.create_args(command="matches_not", warning="SECONDARY", critical="PRIMARY")
        command = MatchesCommand(client, args)
        result = command.execute()

        # Value is PRIMARY which equals critical, so first check is False
        # Then value != warning: PRIMARY != SECONDARY is True, so WARNING
        assert result.status == STATE_WARNING
        assert '"PRIMARY" matches_not keyword "SECONDARY"' in result.message

    def test_matches_not_ok(self):
        """Test matches_not when value equals both thresholds"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"hanode": {"hacurstatus": "UP"}}

        args = self.create_args(command="matches_not", warning="UP", critical="UP")
        command = MatchesCommand(client, args)
        result = command.execute()

        # Value equals both warning and critical, so it's OK
        assert result.status == STATE_OK

    # Tests for multiple fields

    def test_matches_multiple_fields_all_ok(self):
        """Test matches with multiple fields, all OK"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "hanode": {
                "hacurstatus": "PRIMARY",
                "hacurstate": "UP",
            }
        }

        args = self.create_args(objectname="hacurstatus,hacurstate")
        command = MatchesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK

    def test_matches_multiple_fields_one_critical(self):
        """Test matches with multiple fields, one CRITICAL"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "hanode": {
                "hacurstatus": "DOWN",  # matches critical
                "hacurstate": "UP",
            }
        }

        args = self.create_args(objectname="hacurstatus,hacurstate")
        command = MatchesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "hacurstatus" in result.message

    # Tests for arrays (multiple objects)

    def test_matches_array_of_objects(self):
        """Test matches with array of objects"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "service": [
                {"name": "svc1", "svrstate": "UP"},
                {"name": "svc2", "svrstate": "DOWN"},
                {"name": "svc3", "svrstate": "UP"},
            ]
        }

        args = self.create_args(
            objecttype="service", objectname="svrstate", critical="DOWN", warning="OUT OF SERVICE"
        )
        command = MatchesCommand(client, args)
        result = command.execute()

        # svc2 has DOWN which matches critical
        assert result.status == STATE_CRITICAL
        assert "svrstate[1]" in result.message  # Index 1 is svc2

    def test_matches_array_with_custom_label(self):
        """Test matches with array using custom label field"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "service": [
                {"name": "svc1", "svrstate": "UP"},
                {"name": "svc2", "svrstate": "DOWN"},
            ]
        }

        args = self.create_args(
            objecttype="service", objectname="svrstate", critical="DOWN", label="name"
        )
        command = MatchesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "svrstate[svc2]" in result.message  # Uses name as label

    def test_matches_empty_array(self):
        """Test matches with empty array"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"service": []}

        args = self.create_args(objecttype="service", objectname="svrstate")
        command = MatchesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "no objects found" in result.message

    # Error cases

    def test_matches_no_objecttype(self):
        """Test without objecttype"""
        client = self.create_mock_client()

        args = self.create_args(objecttype=None)
        command = MatchesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "requires parameter for objecttype" in result.message

    def test_matches_no_objectname(self):
        """Test without objectname"""
        client = self.create_mock_client()

        args = self.create_args(objectname=None)
        command = MatchesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "requires parameter for objectname" in result.message

    def test_matches_no_warning(self):
        """Test without warning threshold"""
        client = self.create_mock_client()

        args = self.create_args(warning=None)
        command = MatchesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "requires parameter for warning and critical" in result.message

    def test_matches_no_critical(self):
        """Test without critical threshold"""
        client = self.create_mock_client()

        args = self.create_args(critical=None)
        command = MatchesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "requires parameter for warning and critical" in result.message

    def test_matches_field_not_found(self):
        """Test when field is not found in response"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"hanode": {"hacurstatus": "PRIMARY"}}

        args = self.create_args(objectname="nonexistent")
        command = MatchesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "field" in result.message.lower()
        assert "not found" in result.message.lower()

    def test_matches_objecttype_not_found(self):
        """Test when objecttype is not in API response"""
        client = self.create_mock_client()
        client.get_stat.return_value = {}

        args = self.create_args()
        command = MatchesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "not found in API response" in result.message

    def test_matches_invalid_endpoint(self):
        """Test with invalid endpoint"""
        client = self.create_mock_client()

        args = self.create_args(endpoint="invalid")
        command = MatchesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Invalid endpoint" in result.message

    def test_matches_config_endpoint(self):
        """Test matches with config endpoint"""
        client = self.create_mock_client()
        client.get_config.return_value = {"nsconfig": {"configchanged": "false"}}

        args = self.create_args(
            endpoint="config",
            objecttype="nsconfig",
            objectname="configchanged",
            warning="unknown",
            critical="true",
        )
        command = MatchesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        client.get_config.assert_called_once()

    def test_matches_api_error(self):
        """Test when API returns an error"""
        from check_netscaler.client.exceptions import NITROAPIError

        client = self.create_mock_client()
        client.get_stat.side_effect = NITROAPIError("API Error")

        args = self.create_args()
        command = MatchesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Error checking" in result.message

    def test_matches_unexpected_exception(self):
        """Test handling of unexpected exceptions"""
        client = self.create_mock_client()
        client.get_stat.side_effect = Exception("Unexpected error")

        args = self.create_args()
        command = MatchesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Unexpected error" in result.message

    def test_matches_invalid_command(self):
        """Test with invalid command name"""
        client = self.create_mock_client()

        args = self.create_args(command="invalid")
        command = MatchesCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Invalid command" in result.message

    def test_matches_numeric_value(self):
        """Test matches with numeric value converted to string"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"system": {"value": 42}}

        args = self.create_args(objecttype="system", objectname="value", warning="0", critical="42")
        command = MatchesCommand(client, args)
        result = command.execute()

        # Numeric 42 should be converted to string "42" and match
        assert result.status == STATE_CRITICAL

    def test_matches_message_format(self):
        """Test that message format is correct"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"hanode": {"hacurstatus": "DOWN"}}

        args = self.create_args()
        command = MatchesCommand(client, args)
        result = command.execute()

        # Should start with "keyword matches:"
        assert result.message.startswith("keyword matches:")
        assert "hanode.hacurstatus" in result.message

    def test_matches_not_message_format(self):
        """Test that matches_not message format is correct"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"hanode": {"hacurstatus": "DOWN"}}

        args = self.create_args(command="matches_not", critical="UP")
        command = MatchesCommand(client, args)
        result = command.execute()

        # Should start with "keyword matches_not:"
        assert result.message.startswith("keyword matches_not:")
