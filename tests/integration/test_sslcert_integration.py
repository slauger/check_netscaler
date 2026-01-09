"""Integration tests for SSL Certificate Command"""

from argparse import Namespace

from check_netscaler.client import NITROClient
from check_netscaler.commands.sslcert import SSLCertCommand
from check_netscaler.constants import STATE_CRITICAL, STATE_OK, STATE_WARNING


class TestSSLCertCommandIntegration:
    """Test SSL certificate command against mock API"""

    def test_sslcert_check_ok(self, mock_nitro_server):
        """Test SSL cert check with OK cert (60 days)"""
        with NITROClient(
            hostname=mock_nitro_server.host,
            port=mock_nitro_server.port,
            username="nsroot",
            password="nsroot",
            ssl=False,
        ) as client:
            args = Namespace(
                command="sslcert",
                objecttype="sslcertkey",
                objectname="cert_web",
                warning="30",
                critical="10",
                filter=None,
                limit=None,
            )

            command = SSLCertCommand(client, args)
            result = command.execute()

            assert result.status == STATE_OK
            assert "1 certificate(s) OK" in result.message
            assert "warn=30d" in result.message
            assert "crit=10d" in result.message

    def test_sslcert_check_warning(self, mock_nitro_server):
        """Test SSL cert check with warning cert (20 days)"""
        with NITROClient(
            hostname=mock_nitro_server.host,
            port=mock_nitro_server.port,
            username="nsroot",
            password="nsroot",
            ssl=False,
        ) as client:
            args = Namespace(
                command="sslcert",
                objecttype="sslcertkey",
                objectname="cert_warning",
                warning="30",
                critical="10",
                filter=None,
                limit=None,
            )

            command = SSLCertCommand(client, args)
            result = command.execute()

            assert result.status == STATE_WARNING
            assert "WARNING:" in result.message
            assert "cert_warning expires in 20 days" in result.message

    def test_sslcert_check_critical(self, mock_nitro_server):
        """Test SSL cert check with critical cert (5 days)"""
        with NITROClient(
            hostname=mock_nitro_server.host,
            port=mock_nitro_server.port,
            username="nsroot",
            password="nsroot",
            ssl=False,
        ) as client:
            args = Namespace(
                command="sslcert",
                objecttype="sslcertkey",
                objectname="cert_critical",
                warning="30",
                critical="10",
                filter=None,
                limit=None,
            )

            command = SSLCertCommand(client, args)
            result = command.execute()

            assert result.status == STATE_CRITICAL
            assert "CRITICAL:" in result.message
            assert "cert_critical expires in 5 days" in result.message
