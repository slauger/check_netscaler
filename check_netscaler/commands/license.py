"""
License expiration check command

Checks the NetScaler license state directly via the NITRO API instead of
reading ``*.lic`` files. The ``-o/--objecttype`` flag names the NITRO config
resource to query:

- ``-o nslicense`` (default) - base platform license:
  ``licensingmode``, ``modelid``, ``daystoexpiration``.
- ``-o nslaslicense``        - LAS / pooled ("Application Delivery Management")
  license lease: ``status``, ``daystoexpiration``, ``renewalnextdate``.

Only the selected resource is queried. If the appliance does not return it, the
result is UNKNOWN.
"""

from typing import Any, Dict, Optional, Tuple

from check_netscaler.client.exceptions import NITROException
from check_netscaler.commands.base import BaseCommand, CheckResult
from check_netscaler.constants import (
    STATE_CRITICAL,
    STATE_OK,
    STATE_UNKNOWN,
    STATE_WARNING,
)


class LicenseCommand(BaseCommand):
    """Check license expiration via the NITRO nslicense/nslaslicense resources"""

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
            warning_days = self._get_threshold("warning", self.DEFAULT_WARNING)
            critical_days = self._get_threshold("critical", self.DEFAULT_CRITICAL)

            if warning_days is None or critical_days is None:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message="license: command requires warning and critical thresholds (in days)",
                )

            # Select which license resource to query via -o/--objecttype. The
            # value is the NITRO config resource name itself:
            #   nslicense    -> base platform license
            #   nslaslicense -> LAS/pooled (ADM) license lease
            # Defaults to "nslicense" when -o is omitted.
            resource = (getattr(self.args, "objecttype", None) or "nslicense").strip().lower()

            if resource not in ("nslicense", "nslaslicense"):
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message="license: -o/--objecttype must be 'nslicense' or 'nslaslicense'",
                )

            perfdata: Dict[str, Any] = {}

            data = self.client.get_config(resource)
            license_data = self._unwrap(data.get(resource))
            if license_data is None:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message=f"license: {resource} data not found in API response",
                )

            if resource == "nslicense":
                status, message = self._check_nslicense(
                    license_data, warning_days, critical_days, perfdata
                )
            else:  # resource == "nslaslicense"
                status, message = self._check_nslaslicense(
                    license_data, warning_days, critical_days, perfdata
                )

            return CheckResult(
                status=status,
                message="license: " + message,
                perfdata=perfdata,
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

    def _get_threshold(self, name: str, default: int) -> Optional[int]:
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

    @staticmethod
    def _unwrap(resource: Any) -> Optional[Dict[str, Any]]:
        """Return a single dict from a NITRO resource that may be a dict or a list"""
        if isinstance(resource, list):
            return resource[0] if resource else None
        if isinstance(resource, dict):
            return resource
        return None

    @staticmethod
    def _parse_days(value: Any) -> Optional[int]:
        """Parse a daystoexpiration value to int, or None if not numeric"""
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _classify_days(self, days: Optional[int], warning_days: int, critical_days: int) -> int:
        """Map a days-to-expiration value to a Nagios status"""
        if days is None:
            return STATE_UNKNOWN
        if days < critical_days:
            return STATE_CRITICAL
        if days < warning_days:
            return STATE_WARNING
        return STATE_OK

    def _check_nslicense(
        self,
        nslicense: Dict[str, Any],
        warning_days: int,
        critical_days: int,
        perfdata: Dict[str, Any],
    ) -> Tuple[int, str]:
        """Evaluate the base platform license (nslicense)"""
        modelid = nslicense.get("modelid", "unknown")
        mode = nslicense.get("licensingmode", "unknown")
        days = self._parse_days(nslicense.get("daystoexpiration"))

        status = self._classify_days(days, warning_days, critical_days)

        if days is None:
            expiry_text = "daystoexpiration unavailable"
        else:
            perfdata["nslicense_daystoexpiration"] = {
                "value": str(days),
                "warn": str(warning_days),
                "crit": str(critical_days),
            }
            expiry_text = f"expires in {days} days"

        message = f"nslicense modelid={modelid} mode={mode} {expiry_text}"
        return status, message

    def _check_nslaslicense(
        self,
        nslaslicense: Dict[str, Any],
        warning_days: int,
        critical_days: int,
        perfdata: Dict[str, Any],
    ) -> Tuple[int, str]:
        """Evaluate the LAS / pooled (ADM) license lease (nslaslicense)"""
        lic_status = nslaslicense.get("status", "unknown")
        days = self._parse_days(nslaslicense.get("daystoexpiration"))

        status = self._classify_days(days, warning_days, critical_days)

        # A non-ACTIVE lease is critical regardless of days-to-expiration.
        if str(lic_status).upper() != "ACTIVE":
            status = STATE_CRITICAL

        if days is None:
            expiry_text = "entitlement daystoexpiration unavailable"
        else:
            perfdata["nslaslicense_daystoexpiration"] = {
                "value": str(days),
                "warn": str(warning_days),
                "crit": str(critical_days),
            }
            expiry_text = f"entitlement expires in {days} days"

        message = f"nslaslicense status={lic_status} {expiry_text}"

        renewal = nslaslicense.get("renewalnextdate")
        if renewal:
            message += f" (renewal {renewal})"

        return status, message
