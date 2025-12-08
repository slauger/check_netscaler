"""
ServiceGroup with member quorum monitoring command
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


class ServiceGroupCommand(BaseCommand):
    """Check ServiceGroup state and member quorum"""

    def execute(self) -> CheckResult:
        """
        Execute servicegroup check

        Returns:
            CheckResult indicating servicegroup health and member quorum
        """
        try:
            # Get objectname (required for servicegroup)
            objectname = getattr(self.args, "objectname", None)
            if not objectname:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message='servicegroup: no object name "-n" set',
                )

            # Default quorum thresholds (in percent)
            warning_quorum = 90
            critical_quorum = 50

            # Parse thresholds from args
            if self.args.warning:
                try:
                    warning_quorum = float(self.args.warning)
                except ValueError:
                    return CheckResult(
                        status=STATE_UNKNOWN,
                        message=f"Invalid warning threshold: {self.args.warning}",
                    )

            if self.args.critical:
                try:
                    critical_quorum = float(self.args.critical)
                except ValueError:
                    return CheckResult(
                        status=STATE_UNKNOWN,
                        message=f"Invalid critical threshold: {self.args.critical}",
                    )

            # Get servicegroup information
            sg_data = self.client.get_config("servicegroup", objectname)

            if "servicegroup" not in sg_data:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message=f"servicegroup '{objectname}' not found in API response",
                )

            servicegroups = sg_data["servicegroup"]

            # Handle both single object and list
            if not isinstance(servicegroups, list):
                servicegroups = [servicegroups]

            if not servicegroups:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message=f"servicegroup '{objectname}' not found",
                )

            sg = servicegroups[0]  # Should only be one with specific name

            # Check servicegroup health
            sg_errors: List[str] = []
            sg_name = sg.get("servicegroupname", objectname)
            sg_type = sg.get("servicetype", "UNKNOWN")
            sg_effective_state = sg.get("servicegroupeffectivestate", "UNKNOWN")

            # Healthy states for servicegroup
            if sg.get("state") != "ENABLED":
                sg_errors.append(f"servicegroup {sg_name} state is {sg.get('state')}")
            if sg.get("servicegroupeffectivestate") != "UP":
                sg_errors.append(
                    f"servicegroup {sg_name} effective state is {sg.get('servicegroupeffectivestate')}"
                )
            if sg.get("monstate") != "ENABLED":
                sg_errors.append(f"servicegroup {sg_name} monstate is {sg.get('monstate')}")
            if sg.get("healthmonitor") != "YES":
                sg_errors.append(
                    f"servicegroup {sg_name} healthmonitor is {sg.get('healthmonitor')}"
                )

            # Get servicegroup members
            binding_type = "servicegroup_servicegroupmember_binding"
            members_data = self.client.get_config(binding_type, objectname)

            if binding_type not in members_data:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message=f"servicegroup members for '{objectname}' not found",
                )

            members = members_data[binding_type]

            # Handle both single object and list
            if not isinstance(members, list):
                members = [members]

            # Check member health
            member_states: Dict[str, str] = {}
            member_details: List[str] = []

            for member in members:
                server_name = member.get("servername", "Unknown")
                server_ip = member.get("ip", "")
                server_port = member.get("port", "")
                server_state = member.get("svrstate", "UNKNOWN")
                member_state_field = member.get("state", "UNKNOWN")

                # Check member health - both state and svrstate must be healthy
                is_healthy = member_state_field == "ENABLED" and server_state == "UP"

                # Track member state for quorum calculation
                member_states[server_name] = "UP" if is_healthy else "DOWN"

                # Build detail string
                detail = f"{server_name} ({server_ip}:{server_port}) is {server_state}"
                member_details.append(detail)

            # Count states
            members_up = sum(1 for state in member_states.values() if state == "UP")
            members_down = sum(1 for state in member_states.values() if state == "DOWN")
            total_members = members_up + members_down

            # Calculate quorum percentage
            if total_members > 0:
                member_quorum = (members_up / total_members) * 100
            else:
                member_quorum = 0

            # Determine status based on quorum and servicegroup errors
            # Servicegroup errors always result in CRITICAL
            if sg_errors:
                status = STATE_CRITICAL
            elif member_quorum <= critical_quorum:
                status = STATE_CRITICAL
            elif member_quorum <= warning_quorum:
                status = STATE_WARNING
            else:
                status = STATE_OK

            # Build message
            sg_info = f"{sg_name} ({sg_type}) - state: {sg_effective_state}"
            quorum_info = (
                f"member quorum: {member_quorum:.2f}% (UP/DOWN): {members_up}/{members_down}"
            )

            message = f"{sg_info} - {quorum_info}"

            # Build long output
            long_output: List[str] = []

            # Add servicegroup errors
            for error in sg_errors:
                long_output.append(f"CRITICAL: {error}")

            # Add member details
            for detail in member_details:
                long_output.append(detail)

            # Build performance data
            perfdata: Dict[str, float] = {}
            separator = getattr(self.args, "separator", ".")
            perfdata_label = f"{objectname}{separator}member_quorum"
            perfdata[perfdata_label] = member_quorum

            return CheckResult(
                status=status,
                message=message,
                perfdata=perfdata,
                long_output=long_output,
            )

        except NITROException as e:
            return CheckResult(
                status=STATE_UNKNOWN,
                message=f"Error checking servicegroup: {str(e)}",
            )
        except Exception as e:
            return CheckResult(
                status=STATE_UNKNOWN,
                message=f"Unexpected error: {str(e)}",
            )
