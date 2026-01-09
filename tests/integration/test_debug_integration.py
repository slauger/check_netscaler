"""Integration tests for Debug Command"""

from argparse import Namespace

from check_netscaler.client import NITROClient
from check_netscaler.commands.debug import DebugCommand
from check_netscaler.constants import STATE_OK


class TestDebugCommandIntegration:
    """Test debug command against mock API"""

    def test_debug_raw_response(self, mock_nitro_server):
        """Test debug shows raw API response"""
        with NITROClient(
            hostname=mock_nitro_server.host,
            port=mock_nitro_server.port,
            username="nsroot",
            password="nsroot",
            ssl=False,
        ) as client:
            args = Namespace(
                command="debug",
                objecttype="lbvserver",
                objectname="lb_web",
                endpoint="config",
            )

            command = DebugCommand(client, args)
            result = command.execute()

            assert result.status == STATE_OK
            assert "lbvserver" in result.message or "lb_web" in result.message
