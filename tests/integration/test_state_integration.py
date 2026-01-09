"""Integration tests for State Command"""

from argparse import Namespace

from check_netscaler.client import NITROClient
from check_netscaler.commands.state import StateCommand
from check_netscaler.constants import STATE_CRITICAL, STATE_OK


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
            assert "CRITICAL" in result.message
            assert "lb_down" in result.message
            assert "1/1" in result.message

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
