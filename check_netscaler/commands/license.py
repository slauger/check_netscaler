"""
License expiration check command
"""

import base64
from datetime import datetime, timezone
from typing import List

from check_netscaler.client.exceptions import NITROException
from check_netscaler.commands.base import BaseCommand, CheckResult
from check_netscaler.constants import (
    STATE_CRITICAL,
    STATE_OK,
    STATE_UNKNOWN,
    STATE_WARNING,
)


class LicenseCommand(BaseCommand):
    """Check license expiration"""

    # Default thresholds in days
    DEFAULT_WARNING = 30
    DEFAULT_CRITICAL = 10

    def execute(self) -> CheckResult:
        """
        Execute license check

        Returns:
            CheckResult indicating license expiration status
        """
        try:
            # Get thresholds
            warning_days = self._get_threshold("warning", self.DEFAULT_WARNING)
            critical_days = self._get_threshold("critical", self.DEFAULT_CRITICAL)

            if warning_days is None or critical_days is None:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message="license: command requires warning and critical thresholds (in days)",
                )

            # Get endpoint (default to config)
            endpoint = getattr(self.args, "endpoint", None) or "config"

            if endpoint != "config":
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message="license: only config endpoint is supported",
                )

            # Get license files
            license_files = self._get_license_files()

            if not license_files:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message="license: no license files found",
                )

            # Check each license file
            messages: List[str] = []
            worst_status = STATE_OK

            for license_file in license_files:
                file_status, file_messages = self._check_license_file(
                    license_file, warning_days, critical_days
                )

                if file_status > worst_status:
                    worst_status = file_status

                messages.extend(file_messages)

            if not messages:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message="license: no INCREMENT lines found in license files",
                )

            # Build final message
            message = "license: " + "; ".join(messages)

            return CheckResult(
                status=worst_status,
                message=message,
            )

        except NITROException as e:
            return CheckResult(
                status=STATE_UNKNOWN,
                message=f"Error checking license: {str(e)}",
            )
        except Exception as e:
            return CheckResult(
                status=STATE_UNKNOWN,
                message=f"Unexpected error: {str(e)}",
            )

    def _get_threshold(self, name: str, default: int) -> int:
        """Get threshold value from args"""
        if not hasattr(self.args, name):
            return default
        value = getattr(self.args, name)
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _get_license_files(self) -> List[str]:
        """Get list of license files to check"""
        objectname = getattr(self.args, "objectname", None)

        if objectname:
            # User specified specific license file(s)
            return [f.strip() for f in objectname.split(",")]

        # Get all .lic files from /nsconfig/license
        try:
            data = self.client.get_config("systemfile", args="filelocation:/nsconfig/license")

            if "systemfile" not in data:
                return []

            files = data["systemfile"]
            if not isinstance(files, list):
                files = [files]

            # Filter for .lic files
            license_files = [
                f["filename"]
                for f in files
                if isinstance(f, dict) and f.get("filename", "").endswith(".lic")
            ]

            return license_files

        except NITROException:
            return []

    def _check_license_file(self, filename: str, warning_days: int, critical_days: int) -> tuple:
        """
        Check a single license file

        Returns:
            tuple: (status, messages)
        """
        try:
            # Get license file content
            data = self.client.get_config(
                "systemfile", args=f"filelocation:/nsconfig/license,filename:{filename}"
            )

            if "systemfile" not in data:
                return (STATE_UNKNOWN, [f"{filename}: not found"])

            files = data["systemfile"]
            if isinstance(files, list):
                if not files:
                    return (STATE_UNKNOWN, [f"{filename}: not found"])
                file_data = files[0]
            else:
                file_data = files

            # Decode base64 content
            filecontent = file_data.get("filecontent", "")
            if not filecontent:
                return (STATE_UNKNOWN, [f"{filename}: empty content"])

            try:
                content = base64.b64decode(filecontent).decode("utf-8")
            except Exception as e:
                return (STATE_UNKNOWN, [f"{filename}: failed to decode content - {e}"])

            # Parse INCREMENT lines
            messages = []
            worst_status = STATE_OK

            for line in content.splitlines():
                line = line.strip()
                if line.startswith("INCREMENT"):
                    parts = line.split()
                    if len(parts) < 5:
                        continue

                    feature = parts[1]
                    expiry = parts[4]

                    if expiry.lower() == "permanent":
                        messages.append(f"{feature} never expires")
                    else:
                        # Parse date (format: 18-jan-2018)
                        try:
                            expiry_date = datetime.strptime(expiry, "%d-%b-%Y")
                            # Make it timezone-aware (UTC)
                            expiry_date = expiry_date.replace(tzinfo=timezone.utc)
                            now = datetime.now(timezone.utc)
                            days_until_expiry = (expiry_date - now).days

                            if days_until_expiry < critical_days:
                                status = STATE_CRITICAL
                            elif days_until_expiry < warning_days:
                                status = STATE_WARNING
                            else:
                                status = STATE_OK

                            if status > worst_status:
                                worst_status = status

                            messages.append(f"{feature} expires on {expiry}")

                        except ValueError:
                            messages.append(f"{feature} has invalid date format: {expiry}")
                            if worst_status < STATE_WARNING:
                                worst_status = STATE_WARNING

            return (worst_status, messages)

        except NITROException as e:
            return (STATE_UNKNOWN, [f"{filename}: API error - {str(e)}"])
        except Exception as e:
            return (STATE_UNKNOWN, [f"{filename}: error - {str(e)}"])
