"""Integration tests for License Command"""

from argparse import Namespace

from check_netscaler.client import NITROClient
from check_netscaler.commands.license import LicenseCommand
from check_netscaler.constants import STATE_OK


class TestLicenseCommandIntegration:
    """Test license command against mock API"""

    def _client(self, mock_nitro_server):
        return NITROClient(
            hostname=mock_nitro_server.host,
            port=mock_nitro_server.port,
            username="nsroot",
            password="nsroot",
            ssl=False,
        )

    def test_license_nslicense_ok(self, mock_nitro_server):
        """Default selector reports the base platform license (nslicense)"""
        with self._client(mock_nitro_server) as client:
            args = Namespace(
                command="license",
                objecttype="nslicense",
                warning="30",
                critical="10",
            )

            result = LicenseCommand(client, args).execute()

            assert result.status == STATE_OK
            assert "nslicense modelid=200" in result.message
            assert "mode=LAS (Fixed Bandwidth)" in result.message
            assert "expires in 113 days" in result.message
            assert result.perfdata["nslicense_daystoexpiration"]["value"] == "113"

    def test_license_nslaslicense_ok(self, mock_nitro_server):
        """-o nslaslicense reports the LAS/pooled lease (nslaslicense)"""
        with self._client(mock_nitro_server) as client:
            args = Namespace(
                command="license",
                objecttype="nslaslicense",
                warning="30",
                critical="10",
            )

            result = LicenseCommand(client, args).execute()

            assert result.status == STATE_OK
            assert "nslaslicense status=ACTIVE" in result.message
            assert "entitlement expires in 546 days" in result.message
            assert result.perfdata["nslaslicense_daystoexpiration"]["value"] == "546"
