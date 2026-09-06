"""
Threshold check commands - above and below
Used for monitoring system resources like CPU, memory, disk usage
"""

from typing import Any, Dict, List

from check_netscaler.client.exceptions import NITROResourceNotFoundError
from check_netscaler.commands.base import BaseCommand, CheckResult
from check_netscaler.constants import (
    STATE_CRITICAL,
    STATE_OK,
    STATE_UNKNOWN,
    STATE_WARNING,
)


class ThresholdCommand(BaseCommand):
    """Check if values are above or below thresholds"""

    def __init__(self, client, args):
        super().__init__(client, args)
        self.mode = args.command  # 'above' or 'below'

    def execute(self) -> CheckResult:
        """
        Execute threshold check

        Returns:
            CheckResult with threshold evaluation
        """
        objecttype = self.args.objecttype
        field_names = self.args.objectname  # Field names are passed via -n/--objectname
        warning = self.args.warning
        critical = self.args.critical

        if not objecttype:
            return CheckResult(
                status=STATE_UNKNOWN,
                message="No objecttype specified (use -o/--objecttype)",
            )

        if not field_names:
            return CheckResult(
                status=STATE_UNKNOWN,
                message="No field names specified (use -n/--objectname)",
            )

        if not warning or not critical:
            return CheckResult(
                status=STATE_UNKNOWN,
                message="Warning and critical thresholds required (use -w and -c)",
            )

        try:
            # Parse thresholds
            try:
                warn_threshold = float(warning)
                crit_threshold = float(critical)
            except ValueError:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message=f"Invalid threshold values: {warning}, {critical}",
                )

            # Parse field names (comma-separated)
            fields = [f.strip() for f in field_names.split(",")]

            # Get data from NITRO API
            data = self.client.get_stat(objecttype, None)

            # Extract object (should be a single object for system stats)
            objects = self._extract_objects(data, objecttype)

            if not objects:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message=f"No {objecttype} data found",
                )

            # Usually system stats return a single object
            obj = objects[0] if len(objects) == 1 else objects[0]

            # Evaluate thresholds for all fields
            result = self._evaluate_thresholds(
                obj,
                fields,
                warn_threshold,
                crit_threshold,
                objecttype,
            )

            return result

        except NITROResourceNotFoundError:
            return CheckResult(
                status=STATE_CRITICAL,
                message=f"{objecttype} not found",
            )
        except Exception as e:
            return CheckResult(
                status=STATE_UNKNOWN,
                message=f"Error checking {objecttype}: {str(e)}",
            )

    def _extract_objects(self, data: Dict[str, Any], objecttype: str) -> List[Dict]:
        """Extract object list from API response"""
        if objecttype in data:
            obj_data = data[objecttype]
            if isinstance(obj_data, list):
                return obj_data
            else:
                return [obj_data]
        return []

    def _evaluate_thresholds(
        self,
        obj: Dict[str, Any],
        fields: List[str],
        warn_threshold: float,
        crit_threshold: float,
        objecttype: str,
    ) -> CheckResult:
        """
        Evaluate thresholds for all specified fields

        Args:
            obj: Object data from NITRO API
            fields: List of field names to check
            warn_threshold: Warning threshold
            crit_threshold: Critical threshold
            objecttype: Type of object being checked

        Returns:
            CheckResult with aggregated status
        """
        overall_status = STATE_OK
        critical_fields = []
        warning_fields = []
        ok_fields = []
        perfdata = {}
        long_output = []

        for field in fields:
            # Get field value
            value = obj.get(field)

            if value is None:
                # Field not found
                long_output.append(f"{field}: NOT FOUND")
                if overall_status == STATE_OK:
                    overall_status = STATE_UNKNOWN
                continue

            try:
                value_float = float(value)
            except (ValueError, TypeError):
                long_output.append(f"{field}: INVALID VALUE ({value})")
                if overall_status == STATE_OK:
                    overall_status = STATE_UNKNOWN
                continue

            # Evaluate threshold based on mode
            if self.mode == "above":
                # Check if value is above threshold (bad)
                if value_float >= crit_threshold:
                    field_status = STATE_CRITICAL
                    critical_fields.append((field, value_float))
                    if overall_status < STATE_CRITICAL:
                        overall_status = STATE_CRITICAL
                elif value_float >= warn_threshold:
                    field_status = STATE_WARNING
                    warning_fields.append((field, value_float))
                    if overall_status < STATE_WARNING:
                        overall_status = STATE_WARNING
                else:
                    field_status = STATE_OK
                    ok_fields.append((field, value_float))

            else:  # below
                # Check if value is below threshold (bad)
                if value_float <= crit_threshold:
                    field_status = STATE_CRITICAL
                    critical_fields.append((field, value_float))
                    if overall_status < STATE_CRITICAL:
                        overall_status = STATE_CRITICAL
                elif value_float <= warn_threshold:
                    field_status = STATE_WARNING
                    warning_fields.append((field, value_float))
                    if overall_status < STATE_WARNING:
                        overall_status = STATE_WARNING
                else:
                    field_status = STATE_OK
                    ok_fields.append((field, value_float))

            # Build status string
            status_name = {
                STATE_OK: "OK",
                STATE_WARNING: "WARNING",
                STATE_CRITICAL: "CRITICAL",
            }[field_status]

            long_output.append(f"{field}: {value_float} ({status_name})")

            # Add to perfdata
            perfdata[field] = value_float

        # Build message
        message = self._build_message(
            objecttype,
            critical_fields,
            warning_fields,
            ok_fields,
            warn_threshold,
            crit_threshold,
        )

        return CheckResult(
            status=overall_status,
            message=message,
            perfdata=perfdata,
            long_output=long_output if len(fields) > 1 else [],
        )

    def _build_message(
        self,
        objecttype: str,
        critical_fields: List[tuple],
        warning_fields: List[tuple],
        ok_fields: List[tuple],
        warn_threshold: float,
        crit_threshold: float,
    ) -> str:
        """Build status message"""
        parts = []

        if critical_fields:
            field_list = ", ".join([f"{name}={val}" for name, val in critical_fields])
            parts.append(f"CRITICAL: {field_list}")

        if warning_fields:
            field_list = ", ".join([f"{name}={val}" for name, val in warning_fields])
            parts.append(f"WARNING: {field_list}")

        if not critical_fields and not warning_fields:
            total = len(ok_fields)
            if total == 1:
                name, val = ok_fields[0]
                parts.append(f"{name}={val} is OK")
            else:
                parts.append(f"All {total} metrics OK")

        # Add threshold info
        parts.append(f"(warn={warn_threshold}, crit={crit_threshold})")

        return " ".join(parts)
