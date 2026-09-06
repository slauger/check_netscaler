"""
NS Config check command - detects unsaved configuration changes
"""

from check_netscaler.client.exceptions import NITROException
from check_netscaler.commands.base import BaseCommand, CheckResult
from check_netscaler.constants import (
    STATE_OK,
    STATE_UNKNOWN,
    STATE_WARNING,
)


class NSConfigCommand(BaseCommand):
    """Check for unsaved NetScaler configuration changes"""

    def execute(self) -> CheckResult:
        """
        Execute nsconfig check

        Returns:
            CheckResult indicating if config has unsaved changes
        """
        try:
            # Get nsconfig from config endpoint
            data = self.client.get_config("nsconfig")

            # Extract nsconfig object
            if "nsconfig" not in data:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message="nsconfig data not found in API response",
                )

            nsconfig = data["nsconfig"]

            # Handle both single object and list
            if isinstance(nsconfig, list):
                nsconfig = nsconfig[0] if nsconfig else {}

            # Check configchanged field
            # If field is missing or True -> WARNING (unsaved changes)
            # If False -> OK (no unsaved changes)
            config_changed = nsconfig.get("configchanged")

            if config_changed is None:
                # Field not present - assume warning
                return CheckResult(
                    status=STATE_WARNING,
                    message="Unsaved configuration changes detected (field not present)",
                )
            elif config_changed:
                # Explicitly True
                return CheckResult(
                    status=STATE_WARNING,
                    message="Unsaved configuration changes detected",
                )
            else:
                # False
                return CheckResult(
                    status=STATE_OK,
                    message="No unsaved configuration changes",
                )

        except NITROException as e:
            return CheckResult(
                status=STATE_UNKNOWN,
                message=f"Error checking nsconfig: {str(e)}",
            )
        except Exception as e:
            return CheckResult(
                status=STATE_UNKNOWN,
                message=f"Unexpected error: {str(e)}",
            )
