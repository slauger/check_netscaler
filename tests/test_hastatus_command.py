"""
Tests for hastatus command
"""

from argparse import Namespace
from unittest.mock import Mock

from check_netscaler.commands.hastatus import HAStatusCommand
from check_netscaler.constants import STATE_CRITICAL, STATE_OK, STATE_UNKNOWN, STATE_WARNING


class TestHAStatusCommand:
    """Test hastatus check command"""

    def create_mock_client(self):
        """Create a mock NITRO client"""
        client = Mock()
        client.get_config = Mock()
        client.get_stat = Mock()
        return client

    def create_args(self, **kwargs):
        """Create mock arguments"""
        defaults = {
            "command": "hastatus",
            "objecttype": None,
            "endpoint": None,
            "separator": ".",
        }
        defaults.update(kwargs)
        return Namespace(**defaults)

    def test_ha_primary_up(self):
        """Test HA node in PRIMARY state and UP"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "hanode": {
                "hacurstatus": "YES",
                "hacurmasterstate": "Primary",
                "hacurstate": "UP",
                "haerrsyncfailure": "0",
                "haerrproptimeout": "0",
                "hatotpktrx": "12345",
                "hatotpkttx": "67890",
                "hapktrxrate": "100",
                "hapkttxrate": "150",
            }
        }

        args = self.create_args()
        command = HAStatusCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "hacurmasterstate Primary" in result.message
        assert "hacurstate UP" in result.message
        # Check perfdata
        assert "hatotpktrx" in result.perfdata
        assert result.perfdata["hatotpktrx"] == 12345.0

    def test_ha_secondary_up(self):
        """Test HA node in SECONDARY state and UP"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "hanode": {
                "hacurstatus": "YES",
                "hacurmasterstate": "SECONDARY",
                "hacurstate": "UP",
                "haerrsyncfailure": "0",
                "haerrproptimeout": "0",
            }
        }

        args = self.create_args()
        command = HAStatusCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "hacurmasterstate SECONDARY" in result.message
        assert "hacurstate UP" in result.message

    def test_ha_not_configured(self):
        """Test when HA is not configured"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "hanode": {
                "hacurstatus": "NO",
            }
        }

        args = self.create_args()
        command = HAStatusCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "not configured for high availability" in result.message

    def test_ha_staysecondary_warning(self):
        """Test STAYSECONDARY state (WARNING)"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "hanode": {
                "hacurstatus": "YES",
                "hacurmasterstate": "STAYSECONDARY",
                "hacurstate": "UP",
            }
        }

        args = self.create_args()
        command = HAStatusCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING
        assert "STAYSECONDARY" in result.message

    def test_ha_claiming_warning(self):
        """Test CLAIMING state (WARNING)"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "hanode": {
                "hacurstatus": "YES",
                "hacurmasterstate": "CLAIMING",
                "hacurstate": "UP",
            }
        }

        args = self.create_args()
        command = HAStatusCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING
        assert "CLAIMING" in result.message

    def test_ha_force_change_warning(self):
        """Test FORCE CHANGE state (WARNING)"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "hanode": {
                "hacurstatus": "YES",
                "hacurmasterstate": "FORCE CHANGE",
                "hacurstate": "UP",
            }
        }

        args = self.create_args()
        command = HAStatusCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING
        assert "FORCE CHANGE" in result.message

    def test_ha_disabled_warning(self):
        """Test DISABLED state (WARNING)"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "hanode": {
                "hacurstatus": "YES",
                "hacurmasterstate": "PRIMARY",
                "hacurstate": "DISABLED",
            }
        }

        args = self.create_args()
        command = HAStatusCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING
        assert "hacurstate DISABLED" in result.message

    def test_ha_init_warning(self):
        """Test INIT state (WARNING)"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "hanode": {
                "hacurstatus": "YES",
                "hacurmasterstate": "PRIMARY",
                "hacurstate": "INIT",
            }
        }

        args = self.create_args()
        command = HAStatusCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING
        assert "INIT" in result.message

    def test_ha_dumb_warning(self):
        """Test DUMB state (WARNING)"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "hanode": {
                "hacurstatus": "YES",
                "hacurmasterstate": "PRIMARY",
                "hacurstate": "DUMB",
            }
        }

        args = self.create_args()
        command = HAStatusCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING
        assert "DUMB" in result.message

    def test_ha_partialfail_critical(self):
        """Test PARTIALFAIL state (CRITICAL)"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "hanode": {
                "hacurstatus": "YES",
                "hacurmasterstate": "PRIMARY",
                "hacurstate": "PARTIALFAIL",
            }
        }

        args = self.create_args()
        command = HAStatusCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "PARTIALFAIL" in result.message

    def test_ha_completefail_critical(self):
        """Test COMPLETEFAIL state (CRITICAL)"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "hanode": {
                "hacurstatus": "YES",
                "hacurmasterstate": "PRIMARY",
                "hacurstate": "COMPLETEFAIL",
            }
        }

        args = self.create_args()
        command = HAStatusCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "COMPLETEFAIL" in result.message

    def test_ha_partialfailssl_critical(self):
        """Test PARTIALFAILSSL state (CRITICAL)"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "hanode": {
                "hacurstatus": "YES",
                "hacurmasterstate": "PRIMARY",
                "hacurstate": "PARTIALFAILSSL",
            }
        }

        args = self.create_args()
        command = HAStatusCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "PARTIALFAILSSL" in result.message

    def test_ha_routemonitorfail_critical(self):
        """Test ROUTEMONITORFAIL state (CRITICAL)"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "hanode": {
                "hacurstatus": "YES",
                "hacurmasterstate": "PRIMARY",
                "hacurstate": "ROUTEMONITORFAIL",
            }
        }

        args = self.create_args()
        command = HAStatusCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "ROUTEMONITORFAIL" in result.message

    def test_ha_unknown_masterstate_critical(self):
        """Test unknown hacurmasterstate (CRITICAL)"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "hanode": {
                "hacurstatus": "YES",
                "hacurmasterstate": "UNKNOWN_STATE",
                "hacurstate": "UP",
            }
        }

        args = self.create_args()
        command = HAStatusCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "UNKNOWN_STATE" in result.message

    def test_ha_unknown_curstate_critical(self):
        """Test unknown hacurstate (CRITICAL)"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "hanode": {
                "hacurstatus": "YES",
                "hacurmasterstate": "PRIMARY",
                "hacurstate": "UNKNOWN_STATE",
            }
        }

        args = self.create_args()
        command = HAStatusCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "UNKNOWN_STATE" in result.message

    def test_ha_sync_failures_warning(self):
        """Test HA with sync failures (WARNING)"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "hanode": {
                "hacurstatus": "YES",
                "hacurmasterstate": "PRIMARY",
                "hacurstate": "UP",
                "haerrsyncfailure": "5",
                "haerrproptimeout": "0",
            }
        }

        args = self.create_args()
        command = HAStatusCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING
        assert "ha sync failed 5 times" in result.message

    def test_ha_prop_timeout_warning(self):
        """Test HA with propagation timeouts (WARNING)"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "hanode": {
                "hacurstatus": "YES",
                "hacurmasterstate": "PRIMARY",
                "hacurstate": "UP",
                "haerrsyncfailure": "0",
                "haerrproptimeout": "3",
            }
        }

        args = self.create_args()
        command = HAStatusCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING
        assert "ha propagation timed out 3 times" in result.message

    def test_ha_sync_and_prop_failures(self):
        """Test HA with both sync failures and propagation timeouts"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "hanode": {
                "hacurstatus": "YES",
                "hacurmasterstate": "PRIMARY",
                "hacurstate": "UP",
                "haerrsyncfailure": "5",
                "haerrproptimeout": "3",
            }
        }

        args = self.create_args()
        command = HAStatusCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING
        assert "ha sync failed 5 times" in result.message
        assert "ha propagation timed out 3 times" in result.message

    def test_ha_critical_overrides_warnings(self):
        """Test that CRITICAL state overrides WARNING from sync failures"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "hanode": {
                "hacurstatus": "YES",
                "hacurmasterstate": "PRIMARY",
                "hacurstate": "PARTIALFAIL",
                "haerrsyncfailure": "5",
            }
        }

        args = self.create_args()
        command = HAStatusCommand(client, args)
        result = command.execute()

        # PARTIALFAIL is CRITICAL, should override WARNING from sync failures
        assert result.status == STATE_CRITICAL
        assert "PARTIALFAIL" in result.message
        assert "ha sync failed 5 times" in result.message

    def test_ha_response_as_list(self):
        """Test when hanode is returned as a list"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "hanode": [
                {
                    "hacurstatus": "YES",
                    "hacurmasterstate": "PRIMARY",
                    "hacurstate": "UP",
                }
            ]
        }

        args = self.create_args()
        command = HAStatusCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "PRIMARY" in result.message

    def test_ha_empty_response_list(self):
        """Test when hanode is an empty list"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"hanode": []}

        args = self.create_args()
        command = HAStatusCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "no hanode data found" in result.message

    def test_ha_objecttype_not_found(self):
        """Test when objecttype is not in API response"""
        client = self.create_mock_client()
        client.get_stat.return_value = {}

        args = self.create_args()
        command = HAStatusCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "not found in API response" in result.message

    def test_ha_custom_objecttype(self):
        """Test with custom objecttype"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "custom_ha": {
                "hacurstatus": "YES",
                "hacurmasterstate": "PRIMARY",
                "hacurstate": "UP",
            }
        }

        args = self.create_args(objecttype="custom_ha")
        command = HAStatusCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK

    def test_ha_config_endpoint(self):
        """Test with config endpoint"""
        client = self.create_mock_client()
        client.get_config.return_value = {
            "hanode": {
                "hacurstatus": "YES",
                "hacurmasterstate": "PRIMARY",
                "hacurstate": "UP",
            }
        }

        args = self.create_args(endpoint="config")
        command = HAStatusCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        client.get_config.assert_called_once()
        client.get_stat.assert_not_called()

    def test_ha_invalid_endpoint(self):
        """Test with invalid endpoint"""
        client = self.create_mock_client()

        args = self.create_args(endpoint="invalid")
        command = HAStatusCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Invalid endpoint" in result.message

    def test_ha_perfdata_included(self):
        """Test that performance data is included"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "hanode": {
                "hacurstatus": "YES",
                "hacurmasterstate": "PRIMARY",
                "hacurstate": "UP",
                "hatotpktrx": "12345",
                "hatotpkttx": "67890",
                "hapktrxrate": "100.5",
                "hapkttxrate": "150.75",
            }
        }

        args = self.create_args()
        command = HAStatusCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "hatotpktrx" in result.perfdata
        assert "hatotpkttx" in result.perfdata
        assert "hapktrxrate" in result.perfdata
        assert "hapkttxrate" in result.perfdata
        assert result.perfdata["hatotpktrx"] == 12345.0
        assert result.perfdata["hapkttxrate"] == 150.75

    def test_ha_invalid_perfdata_values(self):
        """Test with invalid perfdata values (non-numeric)"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "hanode": {
                "hacurstatus": "YES",
                "hacurmasterstate": "PRIMARY",
                "hacurstate": "UP",
                "hatotpktrx": "invalid",
                "hatotpkttx": "67890",
            }
        }

        args = self.create_args()
        command = HAStatusCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        # Invalid value should be skipped
        assert "hatotpktrx" not in result.perfdata
        # Valid value should be included
        assert "hatotpkttx" in result.perfdata

    def test_ha_api_error(self):
        """Test when API returns an error"""
        from check_netscaler.client.exceptions import NITROAPIError

        client = self.create_mock_client()
        client.get_stat.side_effect = NITROAPIError("API Error")

        args = self.create_args()
        command = HAStatusCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Error checking hastatus" in result.message

    def test_ha_unexpected_exception(self):
        """Test handling of unexpected exceptions"""
        client = self.create_mock_client()
        client.get_stat.side_effect = Exception("Unexpected error")

        args = self.create_args()
        command = HAStatusCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Unexpected error" in result.message

    def test_ha_message_format(self):
        """Test that message format is correct"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "hanode": {
                "hacurstatus": "YES",
                "hacurmasterstate": "PRIMARY",
                "hacurstate": "UP",
            }
        }

        args = self.create_args()
        command = HAStatusCommand(client, args)
        result = command.execute()

        # Message should start with "hastatus:"
        assert result.message.startswith("hastatus:")
        # Should use semicolons as separators
        assert ";" in result.message

    def test_ha_case_insensitive_states(self):
        """Test that state matching is case-insensitive"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "hanode": {
                "hacurstatus": "YES",
                "hacurmasterstate": "primary",  # lowercase
                "hacurstate": "up",  # lowercase
            }
        }

        args = self.create_args()
        command = HAStatusCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "primary" in result.message
        assert "up" in result.message

    def test_ha_missing_states(self):
        """Test when state fields are missing"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "hanode": {
                "hacurstatus": "YES",
                # Missing hacurmasterstate and hacurstate
            }
        }

        args = self.create_args()
        command = HAStatusCommand(client, args)
        result = command.execute()

        # Should not crash, just not include those states in message
        assert result.status == STATE_OK
        assert result.message == "hastatus: "
