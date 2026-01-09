"""Integration tests for NSConfig Command"""

from argparse import Namespace

from check_netscaler.client import NITROClient
from check_netscaler.commands.nsconfig import NSConfigCommand
from check_netscaler.constants import STATE_OK


class TestNSConfigCommandIntegration:
    """Test nsconfig command against mock API"""

    def test_nsconfig_no_changes(self, mock_nitro_server):
        """Test nsconfig when no unsaved changes"""
        with NITROClient(
            hostname=mock_nitro_server.host,
            port=mock_nitro_server.port,
            username="nsroot",
            password="nsroot",
            ssl=False,
        ) as client:
            args = Namespace(command="nsconfig")

            command = NSConfigCommand(client, args)
            result = command.execute()

            assert result.status == STATE_OK
            assert "No unsaved configuration changes" in result.message
