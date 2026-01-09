"""Integration tests for Threshold Commands (above/below)"""

from argparse import Namespace

from check_netscaler.client import NITROClient
from check_netscaler.commands.threshold import ThresholdCommand
from check_netscaler.constants import STATE_CRITICAL, STATE_OK, STATE_WARNING


class TestAboveCommandIntegration:
    """Test above (threshold) command against mock API"""

    def test_above_check_ok(self, mock_nitro_server):
        """Test above check when value is below threshold (OK)"""
        with NITROClient(
            hostname=mock_nitro_server.host,
            port=mock_nitro_server.port,
            username="nsroot",
            password="nsroot",
            ssl=False,
        ) as client:
            # system stats have cpuusagepcnt=15.5
            args = Namespace(
                command="above",
                objecttype="system",
                objectname="cpuusagepcnt",
                warning="50",
                critical="80",
                filter=None,
                limit=None,
            )

            command = ThresholdCommand(client, args)
            result = command.execute()

            assert result.status == STATE_OK
            assert "cpuusagepcnt" in result.message
            assert "15.5" in result.message

    def test_above_check_warning(self, mock_nitro_server):
        """Test above check when value exceeds warning threshold"""
        with NITROClient(
            hostname=mock_nitro_server.host,
            port=mock_nitro_server.port,
            username="nsroot",
            password="nsroot",
            ssl=False,
        ) as client:
            # system stats have memoryusagepcnt=45.2
            args = Namespace(
                command="above",
                objecttype="system",
                objectname="memoryusagepcnt",
                warning="40",
                critical="80",
                filter=None,
                limit=None,
            )

            command = ThresholdCommand(client, args)
            result = command.execute()

            assert result.status == STATE_WARNING
            assert "WARNING" in result.message
            assert "memoryusagepcnt" in result.message

    def test_above_check_critical(self, mock_nitro_server):
        """Test above check when value exceeds critical threshold"""
        with NITROClient(
            hostname=mock_nitro_server.host,
            port=mock_nitro_server.port,
            username="nsroot",
            password="nsroot",
            ssl=False,
        ) as client:
            # system stats have disk0perusage=60.8
            args = Namespace(
                command="above",
                objecttype="system",
                objectname="disk0perusage",
                warning="40",
                critical="59",
                filter=None,
                limit=None,
            )

            command = ThresholdCommand(client, args)
            result = command.execute()

            assert result.status == STATE_CRITICAL
            assert "CRITICAL" in result.message
            assert "disk0perusage" in result.message


class TestBelowCommandIntegration:
    """Test below (threshold) command against mock API"""

    def test_below_check_ok(self, mock_nitro_server):
        """Test below check when value is above threshold (OK)"""
        with NITROClient(
            hostname=mock_nitro_server.host,
            port=mock_nitro_server.port,
            username="nsroot",
            password="nsroot",
            ssl=False,
        ) as client:
            # system stats have disk1perusage=25.3
            args = Namespace(
                command="below",
                objecttype="system",
                objectname="disk1perusage",
                warning="20",
                critical="10",
                filter=None,
                limit=None,
            )

            command = ThresholdCommand(client, args)
            result = command.execute()

            assert result.status == STATE_OK
            assert "disk1perusage" in result.message

    def test_below_check_warning(self, mock_nitro_server):
        """Test below check when value falls below warning threshold"""
        with NITROClient(
            hostname=mock_nitro_server.host,
            port=mock_nitro_server.port,
            username="nsroot",
            password="nsroot",
            ssl=False,
        ) as client:
            # system stats have disk1perusage=25.3
            args = Namespace(
                command="below",
                objecttype="system",
                objectname="disk1perusage",
                warning="30",
                critical="10",
                filter=None,
                limit=None,
            )

            command = ThresholdCommand(client, args)
            result = command.execute()

            assert result.status == STATE_WARNING
            assert "WARNING" in result.message
            assert "disk1perusage" in result.message

    def test_below_check_critical(self, mock_nitro_server):
        """Test below check when value falls below critical threshold"""
        with NITROClient(
            hostname=mock_nitro_server.host,
            port=mock_nitro_server.port,
            username="nsroot",
            password="nsroot",
            ssl=False,
        ) as client:
            # system stats have disk1perusage=25.3
            args = Namespace(
                command="below",
                objecttype="system",
                objectname="disk1perusage",
                warning="30",
                critical="26",
                filter=None,
                limit=None,
            )

            command = ThresholdCommand(client, args)
            result = command.execute()

            assert result.status == STATE_CRITICAL
            assert "CRITICAL" in result.message
            assert "disk1perusage" in result.message
