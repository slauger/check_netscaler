"""
Debug command - displays raw API response
"""

import json

from check_netscaler.client.exceptions import NITROException
from check_netscaler.commands.base import BaseCommand, CheckResult
from check_netscaler.constants import STATE_OK, STATE_UNKNOWN


class DebugCommand(BaseCommand):
    """Display raw NITRO API response for debugging"""

    def execute(self) -> CheckResult:
        """
        Execute debug command

        Returns:
            CheckResult with raw JSON output (always OK unless error)
        """
        try:
            # Determine endpoint type (default to stat)
            endpoint = getattr(self.args, "endpoint", None) or "stat"

            # Get objecttype (required)
            objecttype = getattr(self.args, "objecttype", None)
            if not objecttype:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message="debug command requires --objecttype parameter",
                )

            # Get objectname (optional)
            objectname = getattr(self.args, "objectname", None)

            # Fetch data from appropriate endpoint
            if endpoint == "stat":
                data = self.client.get_stat(objecttype, objectname)
            elif endpoint == "config":
                data = self.client.get_config(objecttype, objectname)
            else:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message=f"Invalid endpoint: {endpoint} (use 'stat' or 'config')",
                )

            # Format as pretty-printed JSON
            json_output = json.dumps(data, indent=2, sort_keys=True)

            # Return OK with JSON as message
            # Note: This will be printed to stdout by the CLI
            return CheckResult(
                status=STATE_OK,
                message=f"Debug output for {objecttype}:\n{json_output}",
            )

        except NITROException as e:
            return CheckResult(
                status=STATE_UNKNOWN,
                message=f"Error fetching debug data: {str(e)}",
            )
        except Exception as e:
            return CheckResult(
                status=STATE_UNKNOWN,
                message=f"Unexpected error: {str(e)}",
            )
