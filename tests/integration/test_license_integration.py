"""Integration tests for License Command"""

from argparse import Namespace

from check_netscaler.client import NITROClient
from check_netscaler.commands.license import LicenseCommand
from check_netscaler.constants import STATE_OK


class TestLicenseCommandIntegration:
    """Test license command against mock API"""

    def test_license_check_ok(self, mock_nitro_server):
        """Test license check with valid license"""
        with NITROClient(
            hostname=mock_nitro_server.host,
            port=mock_nitro_server.port,
            username="nsroot",
            password="nsroot",
            ssl=False,
        ) as client:
            args = Namespace(
                command="license",
                objectname=None,
                warning="30",
                critical="10",
                endpoint="config",
            )

            command = LicenseCommand(client, args)
            result = command.execute()

            assert result.status == STATE_OK
            assert "CNS_V3000_SERVER_PLT" in result.message
            assert "CNS_WEBLOGGING" in result.message
            assert "CNS_SSL" in result.message
            assert "never expires" in result.message
