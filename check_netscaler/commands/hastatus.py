"""
High Availability status check command
"""

from typing import Dict, List

from check_netscaler.client.exceptions import NITROException
from check_netscaler.commands.base import BaseCommand, CheckResult
from check_netscaler.constants import (
    STATE_CRITICAL,
    STATE_OK,
    STATE_UNKNOWN,
    STATE_WARNING,
)


class HAStatusCommand(BaseCommand):
    """Check High Availability status"""

    # Status mappings for hacurmasterstate
    MASTER_STATE_MAP = {
        "PRIMARY": STATE_OK,
        "SECONDARY": STATE_OK,
        "STAYSECONDARY": STATE_WARNING,
        "CLAIMING": STATE_WARNING,
        "FORCE CHANGE": STATE_WARNING,
    }

    # Status mappings for hacurstate
    HA_STATE_MAP = {
        "UP": STATE_OK,
        "DISABLED": STATE_WARNING,
        "INIT": STATE_WARNING,
        "DUMB": STATE_WARNING,
        "PARTIALFAIL": STATE_CRITICAL,
        "COMPLETEFAIL": STATE_CRITICAL,
        "PARTIALFAILSSL": STATE_CRITICAL,
        "ROUTEMONITORFAIL": STATE_CRITICAL,
    }

    def execute(self) -> CheckResult:
        """
        Execute hastatus check

        Returns:
            CheckResult indicating HA status
        """
        try:
            # Get objecttype (default to hanode)
            objecttype = getattr(self.args, "objecttype", None) or "hanode"

            # Get endpoint (default to stat)
            endpoint = getattr(self.args, "endpoint", None) or "stat"

            # Fetch data
            if endpoint == "stat":
                data = self.client.get_stat(objecttype)
            elif endpoint == "config":
                data = self.client.get_config(objecttype)
            else:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message=f"Invalid endpoint: {endpoint}",
                )

            if objecttype not in data:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message=f"hastatus: objecttype '{objecttype}' not found in API response",
                )

            response = data[objecttype]

            # Handle list (take first element)
            if isinstance(response, list):
                if not response:
                    return CheckResult(
                        status=STATE_UNKNOWN,
                        message="hastatus: no hanode data found",
                    )
                response = response[0]

            # Check if HA is configured
            hacurstatus = response.get("hacurstatus", "")
            if hacurstatus != "YES":
                return CheckResult(
                    status=STATE_CRITICAL,
                    message="hastatus: appliance is not configured for high availability",
                )

            # Track messages and worst status
            messages: List[str] = []
            worst_status = STATE_OK

            # Check hacurmasterstate (PRIMARY/SECONDARY/etc.)
            hacurmasterstate = response.get("hacurmasterstate", "")
            if hacurmasterstate:
                state_upper = hacurmasterstate.upper()
                if state_upper in self.MASTER_STATE_MAP:
                    status = self.MASTER_STATE_MAP[state_upper]
                else:
                    # Unknown state - treat as CRITICAL
                    status = STATE_CRITICAL

                if status > worst_status:
                    worst_status = status

                messages.append(f"hacurmasterstate {hacurmasterstate}")

            # Check hacurstate (UP/DISABLED/PARTIALFAIL/etc.)
            hacurstate = response.get("hacurstate", "")
            if hacurstate:
                state_upper = hacurstate.upper()
                if state_upper in self.HA_STATE_MAP:
                    status = self.HA_STATE_MAP[state_upper]
                else:
                    # Unknown state - treat as CRITICAL
                    status = STATE_CRITICAL

                if status > worst_status:
                    worst_status = status

                messages.append(f"hacurstate {hacurstate}")

            # Check for sync failures
            haerrsyncfailure = response.get("haerrsyncfailure", 0)
            try:
                sync_failures = int(haerrsyncfailure)
                if sync_failures > 0:
                    if worst_status < STATE_WARNING:
                        worst_status = STATE_WARNING
                    messages.append(f"ha sync failed {sync_failures} times")
            except (ValueError, TypeError):
                pass

            # Check for propagation timeouts
            haerrproptimeout = response.get("haerrproptimeout", 0)
            try:
                prop_timeouts = int(haerrproptimeout)
                if prop_timeouts > 0:
                    if worst_status < STATE_WARNING:
                        worst_status = STATE_WARNING
                    messages.append(f"ha propagation timed out {prop_timeouts} times")
            except (ValueError, TypeError):
                pass

            # Build performance data
            perfdata: Dict[str, float] = {}

            # Add packet statistics
            for field in ["hatotpktrx", "hatotpkttx", "hapktrxrate", "hapkttxrate"]:
                if field in response:
                    try:
                        value = float(response[field])
                        perfdata[field] = value
                    except (ValueError, TypeError):
                        pass

            # Build final message
            message = "hastatus: " + "; ".join(messages)

            return CheckResult(
                status=worst_status,
                message=message,
                perfdata=perfdata,
            )

        except NITROException as e:
            return CheckResult(
                status=STATE_UNKNOWN,
                message=f"Error checking hastatus: {str(e)}",
            )
        except Exception as e:
            return CheckResult(
                status=STATE_UNKNOWN,
                message=f"Unexpected error: {str(e)}",
            )
