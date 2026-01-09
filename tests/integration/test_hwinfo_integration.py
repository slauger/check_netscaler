"""Integration tests for HWInfo Command"""

from argparse import Namespace

from check_netscaler.client import NITROClient
from check_netscaler.commands.hwinfo import HWInfoCommand
from check_netscaler.constants import STATE_OK


class TestHWInfoCommandIntegration:
    """Test hwinfo command against mock API"""

    def test_hwinfo_display(self, mock_nitro_server):
        """Test hwinfo displays hardware information"""
        with NITROClient(
            hostname=mock_nitro_server.host,
            port=mock_nitro_server.port,
            username="nsroot",
            password="nsroot",
            ssl=False,
        ) as client:
            args = Namespace(command="hwinfo")

            command = HWInfoCommand(client, args)
            result = command.execute()

            assert result.status == STATE_OK
            assert "Platform" in result.message or "CPU" in result.message
