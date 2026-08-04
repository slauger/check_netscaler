"""
Tests for license command
"""

from argparse import Namespace
from unittest.mock import Mock

from check_netscaler.client.exceptions import NITROException
from check_netscaler.commands.license import LicenseCommand
from check_netscaler.constants import STATE_CRITICAL, STATE_OK, STATE_UNKNOWN, STATE_WARNING


class TestLicenseCommand:
    """Test license check command"""

    def create_mock_client(self):
        """Create a mock NITRO client"""
        client = Mock()
        client.get_config = Mock()
        return client

    def create_args(self, **kwargs):
        """Create mock arguments"""
        defaults = {
            "command": "license",
            "objecttype": None,
            "warning": "30",
            "critical": "10",
        }
        defaults.update(kwargs)
        return Namespace(**defaults)

    def nslicense(self, days="113", modelid="200", mode="LAS (Fixed Bandwidth)"):
        """Build an nslicense API response"""
        return {
            "nslicense": {
                "modelid": modelid,
                "licensingmode": mode,
                "daystoexpiration": days,
            }
        }

    def nslaslicense(self, days="546", status="ACTIVE", renewal="Thu Oct 29 14:33:06 2026"):
        """Build an nslaslicense API response"""
        return {
            "nslaslicense": {
                "status": status,
                "daystoexpiration": days,
                "renewalnextdate": renewal,
            }
        }

    # ---- selector: nslicense (default) -------------------------------------

    def test_default_selector_checks_nslicense(self):
        """No -o defaults to 'nslicense' and queries only nslicense"""
        client = self.create_mock_client()
        client.get_config.return_value = self.nslicense(days="113")

        result = LicenseCommand(client, self.create_args()).execute()

        client.get_config.assert_called_once_with("nslicense")
        assert result.status == STATE_OK
        assert result.message.startswith("license: ")
        assert (
            "nslicense modelid=200 mode=LAS (Fixed Bandwidth) expires in 113 days" in result.message
        )
        assert result.perfdata["nslicense_daystoexpiration"]["value"] == "113"
        assert result.perfdata["nslicense_daystoexpiration"]["warn"] == "30"
        assert result.perfdata["nslicense_daystoexpiration"]["crit"] == "10"

    def test_explicit_nslicense_selector(self):
        """-o nslicense behaves like the default"""
        client = self.create_mock_client()
        client.get_config.return_value = self.nslicense(days="113")

        result = LicenseCommand(client, self.create_args(objecttype="nslicense")).execute()

        client.get_config.assert_called_once_with("nslicense")
        assert result.status == STATE_OK

    def test_selector_is_case_insensitive(self):
        """-o NsLicense is accepted"""
        client = self.create_mock_client()
        client.get_config.return_value = self.nslicense(days="113")

        result = LicenseCommand(client, self.create_args(objecttype="NsLicense")).execute()

        client.get_config.assert_called_once_with("nslicense")
        assert result.status == STATE_OK

    def test_lic_warning(self):
        """nslicense days between critical and warning -> WARNING"""
        client = self.create_mock_client()
        client.get_config.return_value = self.nslicense(days="20")

        result = LicenseCommand(client, self.create_args()).execute()

        assert result.status == STATE_WARNING
        assert "expires in 20 days" in result.message

    def test_lic_critical(self):
        """nslicense days below critical -> CRITICAL"""
        client = self.create_mock_client()
        client.get_config.return_value = self.nslicense(days="5")

        result = LicenseCommand(client, self.create_args()).execute()

        assert result.status == STATE_CRITICAL
        assert "expires in 5 days" in result.message

    def test_lic_custom_thresholds(self):
        """Custom -w/-c are honoured and reflected in perfdata"""
        client = self.create_mock_client()
        client.get_config.return_value = self.nslicense(days="113")

        result = LicenseCommand(client, self.create_args(warning="120", critical="10")).execute()

        assert result.status == STATE_WARNING
        assert result.perfdata["nslicense_daystoexpiration"]["warn"] == "120"

    def test_lic_non_numeric_days(self):
        """Non-numeric daystoexpiration -> UNKNOWN, no stale perfdata"""
        client = self.create_mock_client()
        client.get_config.return_value = self.nslicense(days="n/a")

        result = LicenseCommand(client, self.create_args()).execute()

        assert result.status == STATE_UNKNOWN
        assert "daystoexpiration unavailable" in result.message
        assert result.perfdata == {}

    def test_lic_resource_as_list(self):
        """nslicense returned as a list is unwrapped"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "nslicense": [{"modelid": "200", "licensingmode": "LAS", "daystoexpiration": "113"}]
        }

        result = LicenseCommand(client, self.create_args()).execute()

        assert result.status == STATE_OK
        assert "expires in 113 days" in result.message

    def test_lic_missing_body(self):
        """nslicense absent from response -> UNKNOWN"""
        client = self.create_mock_client()
        client.get_config.return_value = {"errorcode": 0}

        result = LicenseCommand(client, self.create_args()).execute()

        assert result.status == STATE_UNKNOWN
        assert "nslicense data not found" in result.message

    def test_lic_api_error(self):
        """NITROException while fetching nslicense -> UNKNOWN"""
        client = self.create_mock_client()
        client.get_config.side_effect = NITROException("boom")

        result = LicenseCommand(client, self.create_args()).execute()

        assert result.status == STATE_UNKNOWN
        assert "Error checking license" in result.message

    # ---- selector: nslaslicense --------------------------------------------

    def test_nslaslicense_selector_ok(self):
        """-o nslaslicense queries only nslaslicense"""
        client = self.create_mock_client()
        client.get_config.return_value = self.nslaslicense(days="546")

        result = LicenseCommand(client, self.create_args(objecttype="nslaslicense")).execute()

        client.get_config.assert_called_once_with("nslaslicense")
        assert result.status == STATE_OK
        assert "nslaslicense status=ACTIVE entitlement expires in 546 days" in result.message
        assert "renewal Thu Oct 29 14:33:06 2026" in result.message
        assert result.perfdata["nslaslicense_daystoexpiration"]["value"] == "546"

    def test_nslaslicense_non_active_is_critical(self):
        """A non-ACTIVE lease is CRITICAL regardless of days left"""
        client = self.create_mock_client()
        client.get_config.return_value = self.nslaslicense(days="999", status="EXPIRED")

        result = LicenseCommand(client, self.create_args(objecttype="nslaslicense")).execute()

        assert result.status == STATE_CRITICAL
        assert "status=EXPIRED" in result.message

    def test_nslaslicense_days_drive_status(self):
        """nslaslicense days below critical -> CRITICAL"""
        client = self.create_mock_client()
        client.get_config.return_value = self.nslaslicense(days="3")

        result = LicenseCommand(client, self.create_args(objecttype="nslaslicense")).execute()

        assert result.status == STATE_CRITICAL

    def test_nslaslicense_missing_body(self):
        """nslaslicense absent (not licensed) -> UNKNOWN when explicitly requested"""
        client = self.create_mock_client()
        client.get_config.return_value = {"errorcode": 0}

        result = LicenseCommand(client, self.create_args(objecttype="nslaslicense")).execute()

        assert result.status == STATE_UNKNOWN
        assert "nslaslicense data not found" in result.message

    def test_nslaslicense_no_renewal_date(self):
        """Missing renewalnextdate simply omits the suffix"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "nslaslicense": {"status": "ACTIVE", "daystoexpiration": "546"}
        }

        result = LicenseCommand(client, self.create_args(objecttype="nslaslicense")).execute()

        assert result.status == STATE_OK
        assert "renewal" not in result.message

    # ---- selector validation & thresholds ----------------------------------

    def test_invalid_selector(self):
        """An unknown -o value -> UNKNOWN and no API call"""
        client = self.create_mock_client()

        result = LicenseCommand(client, self.create_args(objecttype="bogus")).execute()

        assert result.status == STATE_UNKNOWN
        assert "must be 'nslicense' or 'nslaslicense'" in result.message
        client.get_config.assert_not_called()

    def test_missing_thresholds(self):
        """Missing warning/critical -> UNKNOWN"""
        client = self.create_mock_client()

        result = LicenseCommand(client, self.create_args(warning=None, critical=None)).execute()

        assert result.status == STATE_UNKNOWN
        assert "requires warning and critical thresholds" in result.message
        client.get_config.assert_not_called()

    def test_invalid_thresholds(self):
        """Non-numeric warning/critical -> UNKNOWN"""
        client = self.create_mock_client()

        result = LicenseCommand(client, self.create_args(warning="soon", critical="now")).execute()

        assert result.status == STATE_UNKNOWN
        client.get_config.assert_not_called()
