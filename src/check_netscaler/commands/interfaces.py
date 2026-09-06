"""
Network interfaces status check command
"""

import re
from typing import Dict, List

from check_netscaler.client.exceptions import NITROException
from check_netscaler.commands.base import BaseCommand, CheckResult
from check_netscaler.constants import (
    STATE_CRITICAL,
    STATE_OK,
    STATE_UNKNOWN,
)


class InterfacesCommand(BaseCommand):
    """Check network interfaces status"""

    def execute(self) -> CheckResult:
        """
        Execute interfaces check

        Returns:
            CheckResult indicating interfaces status
        """
        try:
            # Get endpoint (default to config)
            endpoint = getattr(self.args, "endpoint", None) or "config"

            # Fetch data
            if endpoint == "config":
                data = self.client.get_config("interface")
            elif endpoint == "stat":
                data = self.client.get_stat("interface")
            else:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message=f"Invalid endpoint: {endpoint}",
                )

            if "interface" not in data:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message="interfaces: 'interface' not found in API response",
                )

            response = data["interface"]

            # Handle both single object and list
            if not isinstance(response, list):
                response = [response]

            if not response:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message="interfaces: no interfaces found",
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

            # Check each interface
            messages: List[str] = []
            errors: List[str] = []
            worst_status = STATE_OK
            perfdata: Dict[str, float] = {}
            separator = getattr(self.args, "separator", ".")

            for interface in response:
                devicename = interface.get("devicename", "Unknown")

                # Apply filter (skip if matches)
                if filter_regex and filter_regex.search(devicename):
                    continue

                # Apply limit (skip if doesn't match)
                if limit_regex and not limit_regex.search(devicename):
                    continue

                interface_status = STATE_OK
                interface_errors = []

                # Check linkstate (1 = UP, 0 = DOWN)
                linkstate = interface.get("linkstate")
                try:
                    if int(linkstate) != 1:
                        interface_errors.append(f'interface {devicename} has linkstate "DOWN"')
                        interface_status = STATE_CRITICAL
                except (ValueError, TypeError):
                    pass

                # Check intfstate (1 = UP, 0 = DOWN)
                intfstate = interface.get("intfstate")
                try:
                    if int(intfstate) != 1:
                        interface_errors.append(f'interface {devicename} has intfstate "DOWN"')
                        interface_status = STATE_CRITICAL
                except (ValueError, TypeError):
                    pass

                # Check state (should be ENABLED)
                state = interface.get("state", "")
                if state != "ENABLED":
                    interface_errors.append(f'interface {devicename} has state "{state}"')
                    interface_status = STATE_CRITICAL

                if interface_status > worst_status:
                    worst_status = interface_status

                # Add errors to error list
                if interface_errors:
                    errors.extend(interface_errors)

                # Build interface info message
                actspeed = interface.get("actspeed", "N/A")
                actualmtu = interface.get("actualmtu", "N/A")
                vlan = interface.get("vlan", "N/A")
                intftype = interface.get("intftype", "N/A")

                info = (
                    f"device: {devicename} "
                    f"(speed: {actspeed}, MTU: {actualmtu}, VLAN: {vlan}, type: {intftype}) "
                    f"{state}"
                )
                messages.append(info)

                # Add performance data
                for metric in ["rxbytes", "txbytes", "rxerrors", "txerrors"]:
                    if metric in interface:
                        try:
                            value = float(interface[metric])
                            label = f"{devicename}{separator}{metric}"
                            perfdata[label] = value
                        except (ValueError, TypeError):
                            pass

            # Build final message
            if errors:
                # Errors first, then status messages
                message = "interfaces: " + ", ".join(errors) + " - " + "; ".join(messages)
            else:
                message = "interfaces: " + "; ".join(messages)

            return CheckResult(
                status=worst_status,
                message=message,
                perfdata=perfdata,
            )

        except NITROException as e:
            return CheckResult(
                status=STATE_UNKNOWN,
                message=f"Error checking interfaces: {str(e)}",
            )
        except Exception as e:
            return CheckResult(
                status=STATE_UNKNOWN,
                message=f"Unexpected error: {str(e)}",
            )
