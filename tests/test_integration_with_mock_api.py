"""
Integration tests using the Mock NITRO API Server

These tests validate end-to-end functionality with realistic API responses.
"""

from argparse import Namespace

import pytest

from check_netscaler.client import NITROClient
from check_netscaler.commands.state import StateCommand
from check_netscaler.commands.sslcert import SSLCertCommand
from check_netscaler.commands.ntp import NTPCommand
from check_netscaler.commands.license import LicenseCommand
from check_netscaler.constants import STATE_CRITICAL, STATE_OK, STATE_WARNING


class TestStateCommandWithMockAPI:
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
            assert "lb_web" in result.message
            assert "UP" in result.message

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
            assert "lb_down" in result.message
            assert "DOWN" in result.message

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

            # Should be CRITICAL because lb_down is DOWN
            assert result.status == STATE_CRITICAL
            assert "lb_web" in result.message
            assert "lb_ssl" in result.message
            assert "lb_down" in result.message


class TestSSLCertCommandWithMockAPI:
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
                warning="30",
                critical="10",
                filter="cert_web",
                limit=None,
            )

            command = SSLCertCommand(client, args)
            result = command.execute()

            assert result.status == STATE_OK
            assert "cert_web" in result.message
            assert "60 days" in result.message

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
                warning="30",
                critical="10",
                filter="cert_warning",
                limit=None,
            )

            command = SSLCertCommand(client, args)
            result = command.execute()

            assert result.status == STATE_WARNING
            assert "cert_warning" in result.message
            assert "20 days" in result.message

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
                warning="30",
                critical="10",
                filter="cert_critical",
                limit=None,
            )

            command = SSLCertCommand(client, args)
            result = command.execute()

            assert result.status == STATE_CRITICAL
            assert "cert_critical" in result.message
            assert "5 days" in result.message


class TestNTPCommandWithMockAPI:
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
            # Check perfdata
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


class TestLicenseCommandWithMockAPI:
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

            # License expires in 365 days, should be OK
            assert result.status == STATE_OK
            assert "CNS_V3000_SERVER_PLT" in result.message
            assert "CNS_WEBLOGGING" in result.message
            assert "CNS_SSL" in result.message
            assert "never expires" in result.message  # Permanent license


@pytest.mark.integration
class TestEndToEndScenarios:
    """End-to-end scenario tests"""

    def test_complete_health_check(self, mock_nitro_server):
        """Test complete system health check"""
        with NITROClient(
            hostname=mock_nitro_server.host,
            port=mock_nitro_server.port,
            username="nsroot",
            password="nsroot",
            ssl=False,
        ) as client:
            # Check all load balancers
            args = Namespace(
                command="state",
                objecttype="lbvserver",
                objectname=None,
                filter=None,
                limit=None,
            )
            state_cmd = StateCommand(client, args)
            state_result = state_cmd.execute()

            # Check SSL certificates
            args = Namespace(
                command="sslcert",
                objecttype="sslcertkey",
                warning="30",
                critical="10",
                filter=None,
                limit=None,
            )
            ssl_cmd = SSLCertCommand(client, args)
            ssl_result = ssl_cmd.execute()

            # Check NTP
            args = Namespace(command="ntp", warning=None, critical=None)
            ntp_cmd = NTPCommand(client, args)
            ntp_result = ntp_cmd.execute()

            # Validate results
            assert state_result.status in [STATE_OK, STATE_WARNING, STATE_CRITICAL]
            assert ssl_result.status in [STATE_OK, STATE_WARNING, STATE_CRITICAL]
            assert ntp_result.status == STATE_OK

            # All checks should return messages
            assert len(state_result.message) > 0
            assert len(ssl_result.message) > 0
            assert len(ntp_result.message) > 0
