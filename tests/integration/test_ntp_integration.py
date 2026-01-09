"""Integration tests for NTP Command"""

from argparse import Namespace

from check_netscaler.client import NITROClient
from check_netscaler.commands.ntp import NTPCommand
from check_netscaler.constants import STATE_OK, STATE_WARNING


class TestNTPCommandIntegration:
    """Test NTP command against mock API"""

    def test_ntp_check_ok(self, mock_nitro_server):
        """Test NTP check with synchronized state"""
        with NITROClient(
            hostname=mock_nitro_server.host,
            port=mock_nitro_server.port,
            username="nsroot",
            password="nsroot",
            ssl=False,
        ) as client:
            args = Namespace(
                command="ntp",
                warning=None,
                critical=None,
            )

            command = NTPCommand(client, args)
            result = command.execute()

            assert result.status == STATE_OK
            assert "Offset" in result.message
            assert "jitter" in result.message
            assert "stratum" in result.message
            assert "truechimers=3" in result.message
            assert "offset" in result.perfdata
            assert "jitter" in result.perfdata
            assert result.perfdata["truechimers"] == 3.0

    def test_ntp_check_with_thresholds(self, mock_nitro_server):
        """Test NTP check with warning thresholds"""
        with NITROClient(
            hostname=mock_nitro_server.host,
            port=mock_nitro_server.port,
            username="nsroot",
            password="nsroot",
            ssl=False,
        ) as client:
            # Set warning at 0.003s (3ms) - our fixture has 5ms offset
            args = Namespace(
                command="ntp",
                warning="o=0.003",
                critical="o=0.010",
            )

            command = NTPCommand(client, args)
            result = command.execute()

            assert result.status == STATE_WARNING
            assert "WARNING" in result.message
