"""
STA Server availability check command
"""

import re
from typing import List

from check_netscaler.client.exceptions import NITROException
from check_netscaler.commands.base import BaseCommand, CheckResult
from check_netscaler.constants import (
    STATE_CRITICAL,
    STATE_OK,
    STATE_UNKNOWN,
    STATE_WARNING,
)


class STAServerCommand(BaseCommand):
    """Check STA (Secure Ticket Authority) server availability"""

    def execute(self) -> CheckResult:
        """
        Execute staserver check

        Returns:
            CheckResult indicating STA server availability
        """
        try:
            # Determine objecttype based on objectname
            objectname = getattr(self.args, "objectname", None)

            if not objectname:
                # Global STA servers
                objecttype = getattr(self.args, "objecttype", None) or "vpnglobal_staserver_binding"
            else:
                # STA servers bound to specific vServer
                objecttype = (
                    getattr(self.args, "objecttype", None) or "vpnvserver_staserver_binding"
                )

            # Get endpoint (default to config)
            endpoint = getattr(self.args, "endpoint", None) or "config"

            # Fetch data
            if endpoint == "config":
                data = self.client.get_config(objecttype, objectname)
            elif endpoint == "stat":
                data = self.client.get_stat(objecttype, objectname)
            else:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message=f"Invalid endpoint: {endpoint}",
                )

            if objecttype not in data:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message=f"staserver: objecttype '{objecttype}' not found in API response",
                )

            response = data[objecttype]

            # Handle both single object and list
            if not isinstance(response, list):
                response = [response]

            if not response:
                return CheckResult(
                    status=STATE_CRITICAL,
                    message="staserver: no staserver found in configuration",
                )

            # Compile filter and limit regex if provided
            filter_regex = None
            limit_regex = None

            if hasattr(self.args, "filter") and self.args.filter:
                try:
                    filter_regex = re.compile(self.args.filter)
                except re.error as e:
                    return CheckResult(
                        status=STATE_UNKNOWN,
                        message=f"Invalid filter regex: {e}",
                    )

            if hasattr(self.args, "limit") and self.args.limit:
                try:
                    limit_regex = re.compile(self.args.limit)
                except re.error as e:
                    return CheckResult(
                        status=STATE_UNKNOWN,
                        message=f"Invalid limit regex: {e}",
                    )

            # Check each STA server
            messages: List[str] = []
            has_available = False  # Track if at least one STA is available
            has_unavailable = False

            for sta in response:
                staserver = sta.get("staserver", "Unknown")

                # Apply filter (skip if matches)
                if filter_regex and filter_regex.search(staserver):
                    continue

                # Apply limit (skip if doesn't match)
                if limit_regex and not limit_regex.search(staserver):
                    continue

                # Check if STA is available by checking staauthid
                staauthid = sta.get("staauthid", "")

                if staauthid == "" or staauthid is None:
                    # STA is unavailable
                    messages.append(f"{staserver} unavailable")
                    has_unavailable = True
                else:
                    # STA is available
                    messages.append(f"{staserver} OK ({staauthid})")
                    has_available = True

            # Determine overall status
            if not has_available and has_unavailable:
                # All STAs are down - CRITICAL
                status = STATE_CRITICAL
            elif has_unavailable:
                # Some STAs are down - WARNING
                status = STATE_WARNING
            else:
                # All STAs are OK
                status = STATE_OK

            # Build final message
            message = "staserver: " + "; ".join(messages)

            return CheckResult(
                status=status,
                message=message,
            )

        except NITROException as e:
            return CheckResult(
                status=STATE_UNKNOWN,
                message=f"Error checking staserver: {str(e)}",
            )
        except Exception as e:
            return CheckResult(
                status=STATE_UNKNOWN,
                message=f"Unexpected error: {str(e)}",
            )
