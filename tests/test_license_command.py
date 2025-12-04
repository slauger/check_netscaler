"""
Tests for license command
"""

import base64
from argparse import Namespace
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

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
            "objectname": None,
            "endpoint": "config",
            "warning": "30",
            "critical": "10",
        }
        defaults.update(kwargs)
        return Namespace(**defaults)

    def create_license_content(self, features):
        """
        Create license file content

        Args:
            features: List of tuples (feature_name, expiry_date_string or "permanent")
        """
        lines = []
        for feature, expiry in features:
            if expiry == "permanent":
                lines.append(f"INCREMENT {feature} vendor version {expiry}")
            else:
                lines.append(f"INCREMENT {feature} vendor version {expiry}")
        content = "\n".join(lines)
        return base64.b64encode(content.encode("utf-8")).decode("utf-8")

    def test_license_expires_ok(self):
        """Test license that expires far in the future (OK)"""
        client = self.create_mock_client()

        # License expires in 60 days
        future_date = datetime.now(timezone.utc) + timedelta(days=60)
        expiry_str = future_date.strftime("%d-%b-%Y").lower()

        # First call: list license files
        client.get_config.side_effect = [
            {"systemfile": [{"filename": "license.lic"}]},
            # Second call: get license content
            {
                "systemfile": [
                    {
                        "filecontent": self.create_license_content(
                            [("CNS_V1000_ServerPlatinum", expiry_str)]
                        )
                    }
                ]
            },
        ]

        args = self.create_args()
        command = LicenseCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "CNS_V1000_ServerPlatinum expires on" in result.message

    def test_license_expires_warning(self):
        """Test license that expires soon (WARNING)"""
        client = self.create_mock_client()

        # License expires in 20 days (between warning 30 and critical 10)
        future_date = datetime.now(timezone.utc) + timedelta(days=20)
        expiry_str = future_date.strftime("%d-%b-%Y").lower()

        client.get_config.side_effect = [
            {"systemfile": [{"filename": "license.lic"}]},
            {
                "systemfile": [
                    {
                        "filecontent": self.create_license_content(
                            [("CNS_V1000_ServerPlatinum", expiry_str)]
                        )
                    }
                ]
            },
        ]

        args = self.create_args()
        command = LicenseCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING
        assert "CNS_V1000_ServerPlatinum expires on" in result.message

    def test_license_expires_critical(self):
        """Test license that expires very soon (CRITICAL)"""
        client = self.create_mock_client()

        # License expires in 5 days (less than critical 10)
        future_date = datetime.now(timezone.utc) + timedelta(days=5)
        expiry_str = future_date.strftime("%d-%b-%Y").lower()

        client.get_config.side_effect = [
            {"systemfile": [{"filename": "license.lic"}]},
            {
                "systemfile": [
                    {
                        "filecontent": self.create_license_content(
                            [("CNS_V1000_ServerPlatinum", expiry_str)]
                        )
                    }
                ]
            },
        ]

        args = self.create_args()
        command = LicenseCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "CNS_V1000_ServerPlatinum expires on" in result.message

    def test_license_permanent(self):
        """Test permanent license"""
        client = self.create_mock_client()

        client.get_config.side_effect = [
            {"systemfile": [{"filename": "license.lic"}]},
            {
                "systemfile": [
                    {
                        "filecontent": self.create_license_content(
                            [("CNS_V1000_ServerPlatinum", "permanent")]
                        )
                    }
                ]
            },
        ]

        args = self.create_args()
        command = LicenseCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "CNS_V1000_ServerPlatinum never expires" in result.message

    def test_multiple_licenses_all_ok(self):
        """Test multiple license features, all OK"""
        client = self.create_mock_client()

        future_date = datetime.now(timezone.utc) + timedelta(days=60)
        expiry_str = future_date.strftime("%d-%b-%Y").lower()

        client.get_config.side_effect = [
            {"systemfile": [{"filename": "license.lic"}]},
            {
                "systemfile": [
                    {
                        "filecontent": self.create_license_content(
                            [
                                ("CNS_V1000_ServerPlatinum", expiry_str),
                                ("CNS_SSLVPN_CONCURRENT_USERS_5000", expiry_str),
                                ("CNS_AppFW", "permanent"),
                            ]
                        )
                    }
                ]
            },
        ]

        args = self.create_args()
        command = LicenseCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "CNS_V1000_ServerPlatinum expires on" in result.message
        assert "CNS_SSLVPN_CONCURRENT_USERS_5000 expires on" in result.message
        assert "CNS_AppFW never expires" in result.message

    def test_multiple_licenses_one_warning(self):
        """Test multiple licenses with one expiring soon"""
        client = self.create_mock_client()

        ok_date = datetime.now(timezone.utc) + timedelta(days=60)
        warning_date = datetime.now(timezone.utc) + timedelta(days=20)
        ok_str = ok_date.strftime("%d-%b-%Y").lower()
        warning_str = warning_date.strftime("%d-%b-%Y").lower()

        client.get_config.side_effect = [
            {"systemfile": [{"filename": "license.lic"}]},
            {
                "systemfile": [
                    {
                        "filecontent": self.create_license_content(
                            [("Feature1", ok_str), ("Feature2", warning_str)]
                        )
                    }
                ]
            },
        ]

        args = self.create_args()
        command = LicenseCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING
        assert "Feature1 expires on" in result.message
        assert "Feature2 expires on" in result.message

    def test_multiple_licenses_one_critical(self):
        """Test multiple licenses with one expiring very soon"""
        client = self.create_mock_client()

        ok_date = datetime.now(timezone.utc) + timedelta(days=60)
        critical_date = datetime.now(timezone.utc) + timedelta(days=5)
        ok_str = ok_date.strftime("%d-%b-%Y").lower()
        critical_str = critical_date.strftime("%d-%b-%Y").lower()

        client.get_config.side_effect = [
            {"systemfile": [{"filename": "license.lic"}]},
            {
                "systemfile": [
                    {
                        "filecontent": self.create_license_content(
                            [("Feature1", ok_str), ("Feature2", critical_str)]
                        )
                    }
                ]
            },
        ]

        args = self.create_args()
        command = LicenseCommand(client, args)
        result = command.execute()

        assert result.status == STATE_CRITICAL
        assert "Feature1 expires on" in result.message
        assert "Feature2 expires on" in result.message

    def test_custom_thresholds(self):
        """Test custom warning/critical thresholds"""
        client = self.create_mock_client()

        # License expires in 40 days
        # With custom thresholds: warning=50, critical=25
        # Should be WARNING
        future_date = datetime.now(timezone.utc) + timedelta(days=40)
        expiry_str = future_date.strftime("%d-%b-%Y").lower()

        client.get_config.side_effect = [
            {"systemfile": [{"filename": "license.lic"}]},
            {
                "systemfile": [
                    {"filecontent": self.create_license_content([("Feature1", expiry_str)])}
                ]
            },
        ]

        args = self.create_args(warning="50", critical="25")
        command = LicenseCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING

    def test_specific_license_file(self):
        """Test checking specific license file via objectname"""
        client = self.create_mock_client()

        future_date = datetime.now(timezone.utc) + timedelta(days=60)
        expiry_str = future_date.strftime("%d-%b-%Y").lower()

        # Only one call - directly fetch the specified file
        client.get_config.return_value = {
            "systemfile": [{"filecontent": self.create_license_content([("Feature1", expiry_str)])}]
        }

        args = self.create_args(objectname="specific.lic")
        command = LicenseCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        # Should not list files, just fetch the specific one
        assert client.get_config.call_count == 1

    def test_multiple_license_files(self):
        """Test checking multiple license files"""
        client = self.create_mock_client()

        future_date = datetime.now(timezone.utc) + timedelta(days=60)
        expiry_str = future_date.strftime("%d-%b-%Y").lower()

        # Multiple files specified via objectname
        client.get_config.side_effect = [
            {
                "systemfile": [
                    {"filecontent": self.create_license_content([("Feature1", expiry_str)])}
                ]
            },
            {
                "systemfile": [
                    {"filecontent": self.create_license_content([("Feature2", expiry_str)])}
                ]
            },
        ]

        args = self.create_args(objectname="file1.lic,file2.lic")
        command = LicenseCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "Feature1" in result.message
        assert "Feature2" in result.message

    def test_no_license_files_found(self):
        """Test when no license files are found"""
        client = self.create_mock_client()
        client.get_config.return_value = {"systemfile": []}

        args = self.create_args()
        command = LicenseCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "no license files found" in result.message

    def test_no_increment_lines(self):
        """Test license file with no INCREMENT lines"""
        client = self.create_mock_client()

        content = "# Some comment\nSERVER this_host ANY\n"
        encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")

        client.get_config.side_effect = [
            {"systemfile": [{"filename": "license.lic"}]},
            {"systemfile": [{"filecontent": encoded}]},
        ]

        args = self.create_args()
        command = LicenseCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "no INCREMENT lines found" in result.message

    def test_empty_license_content(self):
        """Test license file with empty content"""
        client = self.create_mock_client()

        client.get_config.side_effect = [
            {"systemfile": [{"filename": "license.lic"}]},
            {"systemfile": [{"filecontent": ""}]},
        ]

        args = self.create_args()
        command = LicenseCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "empty content" in result.message

    def test_invalid_base64_content(self):
        """Test license file with invalid base64 content"""
        client = self.create_mock_client()

        client.get_config.side_effect = [
            {"systemfile": [{"filename": "license.lic"}]},
            {"systemfile": [{"filecontent": "invalid!!!base64"}]},
        ]

        args = self.create_args()
        command = LicenseCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "failed to decode content" in result.message

    def test_invalid_date_format(self):
        """Test license with invalid date format"""
        client = self.create_mock_client()

        content = "INCREMENT Feature1 vendor version invalid-date-format\n"
        encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")

        client.get_config.side_effect = [
            {"systemfile": [{"filename": "license.lic"}]},
            {"systemfile": [{"filecontent": encoded}]},
        ]

        args = self.create_args()
        command = LicenseCommand(client, args)
        result = command.execute()

        assert result.status == STATE_WARNING
        assert "invalid date format" in result.message

    def test_missing_warning_threshold(self):
        """Test when warning threshold is not provided"""
        client = self.create_mock_client()

        args = self.create_args(warning=None)
        command = LicenseCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "requires warning and critical thresholds" in result.message

    def test_missing_critical_threshold(self):
        """Test when critical threshold is not provided"""
        client = self.create_mock_client()

        args = self.create_args(critical=None)
        command = LicenseCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "requires warning and critical thresholds" in result.message

    def test_invalid_warning_threshold(self):
        """Test when warning threshold is invalid"""
        client = self.create_mock_client()

        args = self.create_args(warning="invalid")
        command = LicenseCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "requires warning and critical thresholds" in result.message

    def test_stat_endpoint_not_supported(self):
        """Test that stat endpoint is not supported"""
        client = self.create_mock_client()

        args = self.create_args(endpoint="stat")
        command = LicenseCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "only config endpoint is supported" in result.message

    def test_systemfile_not_in_response(self):
        """Test when systemfile is not in API response"""
        client = self.create_mock_client()
        client.get_config.return_value = {}

        args = self.create_args()
        command = LicenseCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "no license files found" in result.message

    def test_systemfile_as_dict(self):
        """Test when systemfile is returned as dict instead of list"""
        client = self.create_mock_client()

        future_date = datetime.now(timezone.utc) + timedelta(days=60)
        expiry_str = future_date.strftime("%d-%b-%Y").lower()

        client.get_config.side_effect = [
            {"systemfile": {"filename": "license.lic"}},  # Dict instead of list
            {
                "systemfile": {
                    "filecontent": self.create_license_content([("Feature1", expiry_str)])
                }
            },
        ]

        args = self.create_args()
        command = LicenseCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "Feature1" in result.message

    def test_filter_non_lic_files(self):
        """Test that only .lic files are checked"""
        client = self.create_mock_client()

        future_date = datetime.now(timezone.utc) + timedelta(days=60)
        expiry_str = future_date.strftime("%d-%b-%Y").lower()

        client.get_config.side_effect = [
            {
                "systemfile": [
                    {"filename": "license.lic"},
                    {"filename": "readme.txt"},  # Should be filtered out
                    {"filename": "backup.lic"},
                ]
            },
            {
                "systemfile": [
                    {"filecontent": self.create_license_content([("Feature1", expiry_str)])}
                ]
            },
            {
                "systemfile": [
                    {"filecontent": self.create_license_content([("Feature2", expiry_str)])}
                ]
            },
        ]

        args = self.create_args()
        command = LicenseCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        # Only 2 .lic files should be checked
        assert "Feature1" in result.message
        assert "Feature2" in result.message

    def test_api_error_listing_files(self):
        """Test when API returns an error listing files"""
        from check_netscaler.client.exceptions import NITROAPIError

        client = self.create_mock_client()
        client.get_config.side_effect = NITROAPIError("API Error")

        args = self.create_args()
        command = LicenseCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        # API error during listing is caught and results in empty list
        assert "no license files found" in result.message

    def test_api_error_reading_file(self):
        """Test when API returns an error reading a specific file"""
        from check_netscaler.client.exceptions import NITROAPIError

        client = self.create_mock_client()
        client.get_config.side_effect = [
            {"systemfile": [{"filename": "license.lic"}]},
            NITROAPIError("API Error reading file"),
        ]

        args = self.create_args()
        command = LicenseCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "API error" in result.message

    def test_unexpected_exception(self):
        """Test handling of unexpected exceptions"""
        client = self.create_mock_client()
        client.get_config.side_effect = Exception("Unexpected error")

        args = self.create_args()
        command = LicenseCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Unexpected error" in result.message

    def test_message_format(self):
        """Test that message format is correct"""
        client = self.create_mock_client()

        future_date = datetime.now(timezone.utc) + timedelta(days=60)
        expiry_str = future_date.strftime("%d-%b-%Y").lower()

        client.get_config.side_effect = [
            {"systemfile": [{"filename": "license.lic"}]},
            {
                "systemfile": [
                    {"filecontent": self.create_license_content([("Feature1", expiry_str)])}
                ]
            },
        ]

        args = self.create_args()
        command = LicenseCommand(client, args)
        result = command.execute()

        # Message should start with "license:"
        assert result.message.startswith("license:")
        # Should use semicolons as separators
        assert ";" in result.message or "expires on" in result.message

    def test_expired_license(self):
        """Test license that has already expired"""
        client = self.create_mock_client()

        # License expired 5 days ago
        past_date = datetime.now(timezone.utc) - timedelta(days=5)
        expiry_str = past_date.strftime("%d-%b-%Y").lower()

        client.get_config.side_effect = [
            {"systemfile": [{"filename": "license.lic"}]},
            {
                "systemfile": [
                    {"filecontent": self.create_license_content([("Feature1", expiry_str)])}
                ]
            },
        ]

        args = self.create_args()
        command = LicenseCommand(client, args)
        result = command.execute()

        # Expired license should be CRITICAL (negative days < critical threshold)
        assert result.status == STATE_CRITICAL
        assert "Feature1 expires on" in result.message

    def test_license_expires_today(self):
        """Test license that expires today"""
        client = self.create_mock_client()

        today = datetime.now(timezone.utc)
        expiry_str = today.strftime("%d-%b-%Y").lower()

        client.get_config.side_effect = [
            {"systemfile": [{"filename": "license.lic"}]},
            {
                "systemfile": [
                    {"filecontent": self.create_license_content([("Feature1", expiry_str)])}
                ]
            },
        ]

        args = self.create_args()
        command = LicenseCommand(client, args)
        result = command.execute()

        # Expires today (0 days) should be CRITICAL
        assert result.status == STATE_CRITICAL
        assert "Feature1 expires on" in result.message
