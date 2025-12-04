"""
String matching command - matches and matches_not
"""

from typing import Any, Dict, List

from check_netscaler.client.exceptions import NITROException
from check_netscaler.commands.base import BaseCommand, CheckResult
from check_netscaler.constants import (
    STATE_CRITICAL,
    STATE_OK,
    STATE_UNKNOWN,
    STATE_WARNING,
)


class MatchesCommand(BaseCommand):
    """Check if field values match or don't match specific strings"""

    def execute(self) -> CheckResult:
        """
        Execute matches/matches_not check

        Returns:
            CheckResult indicating if values match expectations
        """
        try:
            # Determine mode from command
            mode = self.args.command  # "matches" or "matches_not"

            if mode not in ["matches", "matches_not"]:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message=f"Invalid command: {mode}",
                )

            # Required parameters
            objecttype = getattr(self.args, "objecttype", None)
            if not objecttype:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message=f"{mode}: command requires parameter for objecttype",
                )

            objectname = getattr(self.args, "objectname", None)
            if not objectname:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message=f"{mode}: command requires parameter for objectname",
                )

            if not self.args.warning or not self.args.critical:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message=f"{mode}: command requires parameter for warning and critical",
                )

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
                    message=f"{mode}: objecttype '{objecttype}' not found in API response",
                )

            response = data[objecttype]

            # Parse field names (can be comma-separated)
            field_names = [f.strip() for f in objectname.split(",")]

            # Track results
            messages: List[str] = []
            worst_status = STATE_OK

            # Handle both HASH (single object) and ARRAY (multiple objects)
            if isinstance(response, dict):
                # Single object - check each field
                for field in field_names:
                    if field not in response:
                        return CheckResult(
                            status=STATE_UNKNOWN,
                            message=f"{mode}: field '{field}' not found in output",
                        )

                    value = str(response[field])
                    status, msg = self._check_value(
                        mode, field, value, objecttype, self.args.warning, self.args.critical
                    )

                    if status > worst_status:
                        worst_status = status
                    messages.append(msg)

            elif isinstance(response, list):
                # Multiple objects - check field in each object
                if not response:
                    return CheckResult(
                        status=STATE_UNKNOWN,
                        message=f"{mode}: no objects found",
                    )

                for idx, obj in enumerate(response):
                    for field in field_names:
                        if field not in obj:
                            return CheckResult(
                                status=STATE_UNKNOWN,
                                message=f"{mode}: field '{field}' not found in object {idx}",
                            )

                        value = str(obj[field])

                        # Build description with label
                        label = self._get_label(obj, idx)
                        description = f"{objecttype}.{field}[{label}]"

                        status, msg = self._check_value_with_desc(
                            mode, description, value, self.args.warning, self.args.critical
                        )

                        if status > worst_status:
                            worst_status = status
                        messages.append(msg)
            else:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message=f"{mode}: unable to parse data. Returned data is not a HASH or ARRAY",
                )

            # Build final message
            final_message = f"keyword {mode}: " + "; ".join(messages)

            return CheckResult(
                status=worst_status,
                message=final_message,
            )

        except NITROException as e:
            return CheckResult(
                status=STATE_UNKNOWN,
                message=f"Error checking {self.args.command}: {str(e)}",
            )
        except Exception as e:
            return CheckResult(
                status=STATE_UNKNOWN,
                message=f"Unexpected error: {str(e)}",
            )

    def _get_label(self, obj: Dict[str, Any], idx: int) -> str:
        """Get label for object (from label field or index)"""
        label_field = getattr(self.args, "label", None)
        if label_field and label_field in obj:
            return str(obj[label_field])
        return str(idx)

    def _check_value(
        self, mode: str, field: str, value: str, objecttype: str, warning: str, critical: str
    ) -> tuple:
        """Check a single value and return status and message"""
        separator = getattr(self.args, "separator", ".")
        description = f"{objecttype}{separator}{field}"
        return self._check_value_with_desc(mode, description, value, warning, critical)

    def _check_value_with_desc(
        self, mode: str, description: str, value: str, warning: str, critical: str
    ) -> tuple:
        """Check a value with description and return status and message"""
        if mode == "matches":
            # matches: value EQUALS critical/warning → CRITICAL/WARNING
            if value == critical:
                return (STATE_CRITICAL, f'{description}: "{value}" {mode} keyword "{critical}"')
            elif value == warning:
                return (STATE_WARNING, f'{description}: "{value}" {mode} keyword "{warning}"')
            else:
                return (STATE_OK, f'{description}: "{value}"')
        else:  # matches_not
            # matches_not: value NOT EQUALS critical/warning → CRITICAL/WARNING
            if value != critical:
                return (STATE_CRITICAL, f'{description}: "{value}" {mode} keyword "{critical}"')
            elif value != warning:
                return (STATE_WARNING, f'{description}: "{value}" {mode} keyword "{warning}"')
            else:
                return (STATE_OK, f'{description}: "{value}"')
