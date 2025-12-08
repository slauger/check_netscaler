"""
Tests for ntp command
"""

from argparse import Namespace
from unittest.mock import Mock

from check_netscaler.commands.ntp import NTPCommand
from check_netscaler.constants import STATE_CRITICAL, STATE_OK, STATE_UNKNOWN, STATE_WARNING


class TestNTPCommand:
    """Test ntp check command"""

    def create_mock_client(self):
        """Create a mock NITRO client"""
        client = Mock()
        client.get_config = Mock()
        return client

    def create_args(self, **kwargs):
        """Create mock arguments"""
        defaults = {
            "command": "ntp",
            "warning": None,
            "critical": None,
        }
        defaults.update(kwargs)
        return Namespace(**defaults)

    def create_ntp_response(
        self, synced_source="192.168.1.1", stratum=2, offset=5.0, jitter=2.5, truechimers=3
    ):
        """Create mock NTP status response"""
        response = """     remote           refid      st t when poll reach   delay   offset  jitter
==============================================================================
"""
        if synced_source:
            response += f"*{synced_source}    .GPS.       {stratum} u   64  128  377    1.234   {offset}   {jitter}\n"

        # Add additional truechimers
        for i in range(truechimers - 1):
            response += f"+192.168.1.{i+10}    .GPS.       {stratum} u   64  128  377    1.234   10.0   1.0\n"

        return response

    def test_ntp_ok(self):
        """Test NTP status OK"""
        client = self.create_mock_client()
        client.get_config.side_effect = [
            {"ntpsync": {"state": "ENABLED"}},
            {"ntpstatus": {"response": self.create_ntp_response()}},
        ]

        args = self.create_args()
        command = NTPCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "Offset" in result.message
        assert "jitter" in result.message
        assert "stratum" in result.message
        assert "truechimers" in result.message
        # Check perfdata
        assert "offset" in result.perfdata
        assert "jitter" in result.perfdata
        assert "stratum" in result.perfdata
        assert "truechimers" in result.perfdata

    def test_ntp_sync_disabled(self):
        """Test when NTP sync is disabled"""
        client = self.create_mock_client()
        client.get_config.return_value = {"ntpsync": {"state": "DISABLED"}}

        args = self.create_args()
        command = NTPCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "Sync DISABLED" in result.message

    def test_ntp_not_synchronized(self):
        """Test when server is not synchronized to any peer"""
        client = self.create_mock_client()
        response = """     remote           refid      st t when poll reach   delay   offset  jitter
==============================================================================
 192.168.1.1     .GPS.       2 u   64  128  377    1.234   5.0   2.5
+192.168.1.2     .GPS.       2 u   64  128  377    1.234   10.0   1.0
"""
        client.get_config.side_effect = [
            {"ntpsync": {"state": "ENABLED"}},
            {"ntpstatus": {"response": response}},
        ]

        args = self.create_args()
        command = NTPCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "Server not synchronized" in result.message

    def test_ntp_offset_warning(self):
        """Test offset exceeds warning threshold"""
        client = self.create_mock_client()
        client.get_config.side_effect = [
            {"ntpsync": {"state": "ENABLED"}},
            {"ntpstatus": {"response": self.create_ntp_response(offset=35.0)}},  # 35ms
        ]

        # Warning at 30ms (0.03s)
        args = self.create_args(warning="o=0.03")
        command = NTPCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING
        assert "(WARNING)" in result.message
        assert "Offset" in result.message

    def test_ntp_offset_critical(self):
        """Test offset exceeds critical threshold"""
        client = self.create_mock_client()
        client.get_config.side_effect = [
            {"ntpsync": {"state": "ENABLED"}},
            {"ntpstatus": {"response": self.create_ntp_response(offset=55.0)}},  # 55ms
        ]

        # Critical at 50ms (0.05s)
        args = self.create_args(critical="o=0.05")
        command = NTPCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "(CRITICAL)" in result.message

    def test_ntp_negative_offset_warning(self):
        """Test negative offset exceeds warning threshold"""
        client = self.create_mock_client()
        client.get_config.side_effect = [
            {"ntpsync": {"state": "ENABLED"}},
            {"ntpstatus": {"response": self.create_ntp_response(offset=-35.0)}},
        ]

        args = self.create_args(warning="o=0.03")
        command = NTPCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING
        assert "(WARNING)" in result.message

    def test_ntp_jitter_warning(self):
        """Test jitter exceeds warning threshold"""
        client = self.create_mock_client()
        client.get_config.side_effect = [
            {"ntpsync": {"state": "ENABLED"}},
            {"ntpstatus": {"response": self.create_ntp_response(jitter=150.0)}},
        ]

        # Warning at 100ms
        args = self.create_args(warning="j=100")
        command = NTPCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING
        assert "jitter=150.0 (WARNING)" in result.message

    def test_ntp_jitter_critical(self):
        """Test jitter exceeds critical threshold"""
        client = self.create_mock_client()
        client.get_config.side_effect = [
            {"ntpsync": {"state": "ENABLED"}},
            {"ntpstatus": {"response": self.create_ntp_response(jitter=250.0)}},
        ]

        args = self.create_args(critical="j=200")
        command = NTPCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "jitter=250.0 (CRITICAL)" in result.message

    def test_ntp_stratum_warning(self):
        """Test stratum exceeds warning threshold"""
        client = self.create_mock_client()
        client.get_config.side_effect = [
            {"ntpsync": {"state": "ENABLED"}},
            {"ntpstatus": {"response": self.create_ntp_response(stratum=5)}},
        ]

        # Warning if stratum > 3
        args = self.create_args(warning="s=3")
        command = NTPCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING
        assert "stratum=5 (WARNING)" in result.message

    def test_ntp_stratum_critical(self):
        """Test stratum exceeds critical threshold"""
        client = self.create_mock_client()
        client.get_config.side_effect = [
            {"ntpsync": {"state": "ENABLED"}},
            {"ntpstatus": {"response": self.create_ntp_response(stratum=10)}},
        ]

        args = self.create_args(critical="s=5")
        command = NTPCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "stratum=10 (CRITICAL)" in result.message

    def test_ntp_truechimers_warning(self):
        """Test truechimers below warning threshold"""
        client = self.create_mock_client()
        client.get_config.side_effect = [
            {"ntpsync": {"state": "ENABLED"}},
            {"ntpstatus": {"response": self.create_ntp_response(truechimers=2)}},
        ]

        # Warning if truechimers <= 3
        args = self.create_args(warning="t=3")
        command = NTPCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING
        assert "truechimers=2 (WARNING)" in result.message

    def test_ntp_truechimers_critical(self):
        """Test truechimers below critical threshold"""
        client = self.create_mock_client()
        client.get_config.side_effect = [
            {"ntpsync": {"state": "ENABLED"}},
            {"ntpstatus": {"response": self.create_ntp_response(truechimers=1)}},
        ]

        args = self.create_args(critical="t=2")
        command = NTPCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "truechimers=1 (CRITICAL)" in result.message

    def test_ntp_multiple_thresholds(self):
        """Test with multiple threshold parameters"""
        client = self.create_mock_client()
        client.get_config.side_effect = [
            {"ntpsync": {"state": "ENABLED"}},
            {
                "ntpstatus": {
                    "response": self.create_ntp_response(
                        offset=35.0, jitter=150.0, stratum=5, truechimers=2
                    )
                }
            },
        ]

        # Multiple warnings
        args = self.create_args(warning="o=0.03,j=100,s=3,t=3")
        command = NTPCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING
        # Should have multiple warnings
        assert "(WARNING)" in result.message

    def test_ntp_critical_overrides_warning(self):
        """Test that critical status overrides warning"""
        client = self.create_mock_client()
        client.get_config.side_effect = [
            {"ntpsync": {"state": "ENABLED"}},
            {"ntpstatus": {"response": self.create_ntp_response(offset=55.0, jitter=150.0)}},
        ]

        # Offset critical, jitter warning
        args = self.create_args(warning="j=100", critical="o=0.05")
        command = NTPCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "Offset" in result.message
        assert "CRITICAL" in result.message

    def test_ntp_perfdata_values(self):
        """Test that performance data values are correct"""
        client = self.create_mock_client()
        client.get_config.side_effect = [
            {"ntpsync": {"state": "ENABLED"}},
            {
                "ntpstatus": {
                    "response": self.create_ntp_response(
                        offset=5.0, jitter=2.5, stratum=2, truechimers=3
                    )
                }
            },
        ]

        args = self.create_args()
        command = NTPCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert result.perfdata["offset"] == 0.005  # 5ms = 0.005s
        assert result.perfdata["jitter"] == 2.5
        assert result.perfdata["stratum"] == 2.0
        assert result.perfdata["truechimers"] == 3.0

    def test_ntp_ntpsync_as_list(self):
        """Test when ntpsync is returned as list"""
        client = self.create_mock_client()
        client.get_config.side_effect = [
            {"ntpsync": [{"state": "ENABLED"}]},
            {"ntpstatus": {"response": self.create_ntp_response()}},
        ]

        args = self.create_args()
        command = NTPCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK

    def test_ntp_ntpstatus_as_list(self):
        """Test when ntpstatus is returned as list"""
        client = self.create_mock_client()
        client.get_config.side_effect = [
            {"ntpsync": {"state": "ENABLED"}},
            {"ntpstatus": [{"response": self.create_ntp_response()}]},
        ]

        args = self.create_args()
        command = NTPCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK

    def test_ntp_ntpsync_not_found(self):
        """Test when ntpsync is not in API response"""
        client = self.create_mock_client()
        client.get_config.return_value = {}

        args = self.create_args()
        command = NTPCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "ntpsync not found" in result.message

    def test_ntp_ntpstatus_not_found(self):
        """Test when ntpstatus is not in API response"""
        client = self.create_mock_client()
        client.get_config.side_effect = [{"ntpsync": {"state": "ENABLED"}}, {}]

        args = self.create_args()
        command = NTPCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "ntpstatus not found" in result.message

    def test_ntp_empty_response(self):
        """Test with empty NTP status response"""
        client = self.create_mock_client()
        client.get_config.side_effect = [
            {"ntpsync": {"state": "ENABLED"}},
            {"ntpstatus": {"response": ""}},
        ]

        args = self.create_args()
        command = NTPCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "Server not synchronized" in result.message

    def test_ntp_malformed_peer_line(self):
        """Test with malformed peer line (too few fields)"""
        client = self.create_mock_client()
        response = """     remote           refid      st t when poll reach   delay   offset  jitter
==============================================================================
*192.168.1.1    .GPS.       2
"""
        client.get_config.side_effect = [
            {"ntpsync": {"state": "ENABLED"}},
            {"ntpstatus": {"response": response}},
        ]

        args = self.create_args()
        command = NTPCommand(client, args)
        result = command.execute()

        # Should handle gracefully
        assert result.status == STATE_CRITICAL
        assert "Server not synchronized" in result.message

    def test_ntp_threshold_parsing_spaces(self):
        """Test threshold parsing with spaces"""
        client = self.create_mock_client()
        client.get_config.side_effect = [
            {"ntpsync": {"state": "ENABLED"}},
            {"ntpstatus": {"response": self.create_ntp_response(offset=35.0)}},
        ]

        # Spaces around values
        args = self.create_args(warning=" o = 0.03 , j = 100 ")
        command = NTPCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING

    def test_ntp_invalid_threshold_values(self):
        """Test with invalid threshold values (non-numeric)"""
        client = self.create_mock_client()
        client.get_config.side_effect = [
            {"ntpsync": {"state": "ENABLED"}},
            {"ntpstatus": {"response": self.create_ntp_response()}},
        ]

        # Invalid values should be ignored
        args = self.create_args(warning="o=invalid,j=abc")
        command = NTPCommand(client, args)
        result = command.execute()

        # Should not crash, just ignore invalid thresholds
        assert result.status == STATE_OK

    def test_ntp_api_error(self):
        """Test when API returns an error"""
        from check_netscaler.client.exceptions import NITROAPIError

        client = self.create_mock_client()
        client.get_config.side_effect = NITROAPIError("API Error")

        args = self.create_args()
        command = NTPCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Error checking ntp" in result.message

    def test_ntp_unexpected_exception(self):
        """Test handling of unexpected exceptions"""
        client = self.create_mock_client()
        client.get_config.side_effect = Exception("Unexpected error")

        args = self.create_args()
        command = NTPCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Unexpected error" in result.message

    def test_ntp_message_format(self):
        """Test message format"""
        client = self.create_mock_client()
        client.get_config.side_effect = [
            {"ntpsync": {"state": "ENABLED"}},
            {"ntpstatus": {"response": self.create_ntp_response()}},
        ]

        args = self.create_args()
        command = NTPCommand(client, args)
        result = command.execute()

        # Message should start with "ntp:"
        assert result.message.startswith("ntp:")
        # Should contain all metrics
        assert "Offset" in result.message
        assert "jitter=" in result.message
        assert "stratum=" in result.message
        assert "truechimers=" in result.message

    def test_ntp_truechimers_count(self):
        """Test truechimers counting (*, +, -)"""
        client = self.create_mock_client()
        response = """     remote           refid      st t when poll reach   delay   offset  jitter
==============================================================================
*192.168.1.1     .GPS.       2 u   64  128  377    1.234   5.0   2.5
+192.168.1.2     .GPS.       2 u   64  128  377    1.234   10.0   1.0
-192.168.1.3     .GPS.       3 u   64  128  377    1.234   15.0   3.0
 192.168.1.4     .GPS.       4 u   64  128  377    1.234   20.0   4.0
"""
        client.get_config.side_effect = [
            {"ntpsync": {"state": "ENABLED"}},
            {"ntpstatus": {"response": response}},
        ]

        args = self.create_args()
        command = NTPCommand(client, args)
        result = command.execute()

        # Should count *, +, - = 3 truechimers (not the space one)
        assert result.perfdata["truechimers"] == 3.0

    def test_ntp_offset_conversion(self):
        """Test that offset is correctly converted from ms to seconds"""
        client = self.create_mock_client()
        # 123.456 ms should become 0.123456 seconds
        client.get_config.side_effect = [
            {"ntpsync": {"state": "ENABLED"}},
            {"ntpstatus": {"response": self.create_ntp_response(offset=123.456)}},
        ]

        args = self.create_args()
        command = NTPCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        # Check the perfdata has seconds
        assert abs(result.perfdata["offset"] - 0.123456) < 0.000001
