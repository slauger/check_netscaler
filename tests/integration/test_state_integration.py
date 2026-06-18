"""Integration tests for State Command"""

from argparse import Namespace

from check_netscaler.client import NITROClient
from check_netscaler.commands.state import StateCommand
from check_netscaler.constants import STATE_CRITICAL, STATE_OK, STATE_WARNING


class TestStateCommandIntegration:
    """Test state command against mock API"""

    def test_state_check_lbvserver_up(self, mock_nitro_server):
        """Test checking state of UP load balancer"""
        with NITROClient(
            hostname=mock_nitro_server.host,
            port=mock_nitro_server.port,
            username="nsroot",
            password="nsroot",
            ssl=False,
        ) as client:
            args = Namespace(
                command="state",
                objecttype="lbvserver",
                objectname="lb_web",
                filter=None,
                limit=None,
            )

            command = StateCommand(client, args)
            result = command.execute()

            assert result.status == STATE_OK
            assert result.message == "lbvserver is UP"

    def test_state_check_lbvserver_ignores_health_by_default(self, mock_nitro_server):
        """Test lbvserver health does not affect status without thresholds."""
        with NITROClient(
            hostname=mock_nitro_server.host,
            port=mock_nitro_server.port,
            username="nsroot",
            password="nsroot",
            ssl=False,
        ) as client:
            args = Namespace(
                command="state",
                objecttype="lbvserver",
                objectname="lb_ssl",
                filter=None,
                limit=None,
            )

            command = StateCommand(client, args)
            result = command.execute()

            assert result.status == STATE_OK
            assert result.message == "lbvserver is UP"
            assert "health" not in result.perfdata

    def test_state_check_lbvserver_health_warning(self, mock_nitro_server):
        """Test checking lbvserver health below warning threshold."""
        with NITROClient(
            hostname=mock_nitro_server.host,
            port=mock_nitro_server.port,
            username="nsroot",
            password="nsroot",
            ssl=False,
        ) as client:
            args = Namespace(
                command="state",
                objecttype="lbvserver",
                objectname="lb_ssl",
                filter=None,
                limit=None,
                warning="100",
                critical=None,
            )

            command = StateCommand(client, args)
            result = command.execute()

            assert result.status == STATE_WARNING
            assert result.message == "lb_ssl state: UP, Health: 95%"
            assert result.perfdata["health"]["value"] == "95"
            assert result.perfdata["health"]["warn"] == "100"
            assert result.perfdata["health"]["crit"] == "0"

    def test_state_check_lbvserver_down(self, mock_nitro_server):
        """Test checking state of DOWN load balancer"""
        with NITROClient(
            hostname=mock_nitro_server.host,
            port=mock_nitro_server.port,
            username="nsroot",
            password="nsroot",
            ssl=False,
        ) as client:
            args = Namespace(
                command="state",
                objecttype="lbvserver",
                objectname="lb_down",
                filter=None,
                limit=None,
            )

            command = StateCommand(client, args)
            result = command.execute()

            assert result.status == STATE_CRITICAL
            assert result.message == "1/1 lbvserver CRITICAL (lb_down)"

    def test_state_check_all_lbvservers(self, mock_nitro_server):
        """Test checking all load balancers"""
        with NITROClient(
            hostname=mock_nitro_server.host,
            port=mock_nitro_server.port,
            username="nsroot",
            password="nsroot",
            ssl=False,
        ) as client:
            args = Namespace(
                command="state",
                objecttype="lbvserver",
                objectname=None,
                filter=None,
                limit=None,
            )

            command = StateCommand(client, args)
            result = command.execute()

            assert result.status == STATE_CRITICAL
            assert "CRITICAL" in result.message
            assert "lb_down" in result.message
            assert "1/3" in result.message
