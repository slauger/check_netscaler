"""
Tests for threshold commands (above/below)
"""

from argparse import Namespace
from unittest.mock import Mock

from check_netscaler.commands.threshold import ThresholdCommand
from check_netscaler.constants import STATE_CRITICAL, STATE_OK, STATE_UNKNOWN, STATE_WARNING


class TestThresholdCommand:
    """Test threshold check commands"""

    def create_mock_client(self):
        """Create a mock NITRO client"""
        client = Mock()
        client.get_stat = Mock()
        return client

    def create_args(self, command="above", **kwargs):
        """Create mock arguments"""
        defaults = {
            "command": command,
            "objecttype": "system",
            "objectname": "cpuusagepcnt",  # Field name
            "warning": "75",
            "critical": "90",
            "separator": ".",
        }
        defaults.update(kwargs)
        return Namespace(**defaults)

    # Tests for 'above' command

    def test_above_ok(self):
        """Test value below warning threshold (OK)"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"system": [{"cpuusagepcnt": 50}]}

        args = self.create_args(command="above")
        command = ThresholdCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "cpuusagepcnt=50" in result.message
        assert result.perfdata["cpuusagepcnt"] == 50

    def test_above_warning(self):
        """Test value above warning threshold"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"system": [{"cpuusagepcnt": 80}]}

        args = self.create_args(command="above")
        command = ThresholdCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING
        assert "WARNING" in result.message
        assert "cpuusagepcnt=80" in result.message

    def test_above_critical(self):
        """Test value above critical threshold"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"system": [{"cpuusagepcnt": 95}]}

        args = self.create_args(command="above")
        command = ThresholdCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "CRITICAL" in result.message
        assert "cpuusagepcnt=95" in result.message

    def test_above_at_warning_threshold(self):
        """Test value exactly at warning threshold"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"system": [{"cpuusagepcnt": 75}]}

        args = self.create_args(command="above")
        command = ThresholdCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING

    def test_above_at_critical_threshold(self):
        """Test value exactly at critical threshold"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"system": [{"cpuusagepcnt": 90}]}

        args = self.create_args(command="above")
        command = ThresholdCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL

    # Tests for 'below' command

    def test_below_ok(self):
        """Test value above warning threshold (OK for below)"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"servicegroup": [{"activemembers": 10}]}

        args = self.create_args(
            command="below",
            objecttype="servicegroup",
            objectname="activemembers",
            warning="5",
            critical="2",
        )
        command = ThresholdCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "activemembers=10" in result.message

    def test_below_warning(self):
        """Test value below warning threshold"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"servicegroup": [{"activemembers": 4}]}

        args = self.create_args(
            command="below",
            objecttype="servicegroup",
            objectname="activemembers",
            warning="5",
            critical="2",
        )
        command = ThresholdCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING
        assert "WARNING" in result.message

    def test_below_critical(self):
        """Test value below critical threshold"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"servicegroup": [{"activemembers": 1}]}

        args = self.create_args(
            command="below",
            objecttype="servicegroup",
            objectname="activemembers",
            warning="5",
            critical="2",
        )
        command = ThresholdCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "CRITICAL" in result.message

    # Tests for multiple fields

    def test_multiple_fields_all_ok(self):
        """Test multiple fields, all OK"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "system": [
                {
                    "cpuusagepcnt": 50,
                    "memusagepcnt": 60,
                    "disk0perusage": 40,
                }
            ]
        }

        args = self.create_args(
            command="above",
            objectname="cpuusagepcnt,memusagepcnt,disk0perusage",
        )
        command = ThresholdCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "All 3 metrics OK" in result.message
        assert len(result.perfdata) == 3

    def test_multiple_fields_one_warning(self):
        """Test multiple fields, one WARNING"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "system": [
                {
                    "cpuusagepcnt": 50,
                    "memusagepcnt": 80,  # WARNING
                    "disk0perusage": 40,
                }
            ]
        }

        args = self.create_args(
            command="above",
            objectname="cpuusagepcnt,memusagepcnt,disk0perusage",
        )
        command = ThresholdCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING
        assert "WARNING" in result.message
        assert "memusagepcnt=80" in result.message

    def test_multiple_fields_one_critical(self):
        """Test multiple fields, one CRITICAL"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "system": [
                {
                    "cpuusagepcnt": 95,  # CRITICAL
                    "memusagepcnt": 60,
                    "disk0perusage": 40,
                }
            ]
        }

        args = self.create_args(
            command="above",
            objectname="cpuusagepcnt,memusagepcnt,disk0perusage",
        )
        command = ThresholdCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "CRITICAL" in result.message
        assert "cpuusagepcnt=95" in result.message

    def test_multiple_fields_mixed_states(self):
        """Test multiple fields with mixed states"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "system": [
                {
                    "cpuusagepcnt": 95,  # CRITICAL
                    "memusagepcnt": 80,  # WARNING
                    "disk0perusage": 40,  # OK
                }
            ]
        }

        args = self.create_args(
            command="above",
            objectname="cpuusagepcnt,memusagepcnt,disk0perusage",
        )
        command = ThresholdCommand(client, args)
        result = command.execute()

        # CRITICAL takes precedence
        assert result.status == STATE_CRITICAL
        assert "CRITICAL" in result.message
        assert "WARNING" in result.message
        assert len(result.long_output) == 3

    # Error cases

    def test_no_objecttype(self):
        """Test without objecttype"""
        client = self.create_mock_client()
        args = self.create_args(objecttype=None)
        command = ThresholdCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "No objecttype specified" in result.message

    def test_no_field_name(self):
        """Test without field name"""
        client = self.create_mock_client()
        args = self.create_args(objectname=None)
        command = ThresholdCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "No field names specified" in result.message

    def test_no_thresholds(self):
        """Test without thresholds"""
        client = self.create_mock_client()
        args = self.create_args(warning=None, critical=None)
        command = ThresholdCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "thresholds required" in result.message

    def test_invalid_threshold_values(self):
        """Test with invalid threshold values"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"system": [{"cpuusagepcnt": 50}]}

        args = self.create_args(warning="invalid", critical="90")
        command = ThresholdCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Invalid threshold" in result.message

    def test_field_not_found(self):
        """Test with field that doesn't exist"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"system": [{"cpuusagepcnt": 50}]}

        args = self.create_args(objectname="nonexistent_field")
        command = ThresholdCommand(client, args)
        result = command.execute()

        # Should return UNKNOWN when field not found
        assert result.status == STATE_UNKNOWN

    def test_field_invalid_value(self):
        """Test with field that has non-numeric value"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"system": [{"cpuusagepcnt": "invalid"}]}

        args = self.create_args()
        command = ThresholdCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        # Single field doesn't produce long_output
        assert result.perfdata == {}

    def test_no_data_returned(self):
        """Test when API returns no data"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"system": []}

        args = self.create_args()
        command = ThresholdCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "No system data found" in result.message

    def test_resource_not_found(self):
        """Test when resource not found"""
        from check_netscaler.client.exceptions import NITROResourceNotFoundError

        client = self.create_mock_client()
        client.get_stat.side_effect = NITROResourceNotFoundError("Not found")

        args = self.create_args()
        command = ThresholdCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "not found" in result.message

    def test_thresholds_in_message(self):
        """Test that thresholds appear in message"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"system": [{"cpuusagepcnt": 50}]}

        args = self.create_args()
        command = ThresholdCommand(client, args)
        result = command.execute()

        assert "warn=75" in result.message
        assert "crit=90" in result.message
