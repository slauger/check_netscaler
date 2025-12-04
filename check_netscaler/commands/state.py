"""
State check command - monitors vServer, service, servicegroup, and server states
"""

import re
from typing import Any, Dict, List

from check_netscaler.client.exceptions import NITROResourceNotFoundError
from check_netscaler.commands.base import BaseCommand, CheckResult
from check_netscaler.constants import (
    STATE_CRITICAL,
    STATE_OK,
    STATE_UNKNOWN,
    STATE_WARNING,
)


class StateCommand(BaseCommand):
    """Check state of NetScaler objects"""

    # State mappings - which states are considered OK
    OK_STATES = {"UP", "ENABLED", "ACTIVE"}
    WARNING_STATES = {"OUT OF SERVICE", "GOING OUT OF SERVICE", "UNKNOWN"}
    CRITICAL_STATES = {"DOWN", "DISABLED", "INACTIVE"}

    def execute(self) -> CheckResult:
        """
        Execute state check

        Returns:
            CheckResult with aggregated state information
        """
        objecttype = self.args.objecttype
        objectname = self.args.objectname

        if not objecttype:
            return CheckResult(
                status=STATE_UNKNOWN,
                message="No objecttype specified (use -o/--objecttype)",
            )

        try:
            # Get data from NITRO API
            data = self.client.get_stat(objecttype, objectname)

            # Extract objects from response
            objects = self._extract_objects(data, objecttype)

            if not objects:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message=f"No {objecttype} objects found",
                )

            # Apply filters if specified
            if self.args.filter:
                objects = self._apply_filter(objects, self.args.filter)

            if self.args.limit:
                objects = self._apply_limit(objects, self.args.limit)

            if not objects:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message=f"No {objecttype} objects after filtering",
                )

            # Evaluate state for all objects
            result = self._evaluate_states(objects, objecttype)

            return result

        except NITROResourceNotFoundError:
            return CheckResult(
                status=STATE_CRITICAL,
                message=f"{objecttype} not found" + (f": {objectname}" if objectname else ""),
            )
        except Exception as e:
            return CheckResult(
                status=STATE_UNKNOWN,
                message=f"Error checking {objecttype}: {str(e)}",
            )

    def _extract_objects(self, data: Dict[str, Any], objecttype: str) -> List[Dict]:
        """Extract object list from API response"""
        # NITRO API returns data in format: {objecttype: [...]}
        if objecttype in data:
            obj_data = data[objecttype]
            # Can be a list or a single object
            if isinstance(obj_data, list):
                return obj_data
            else:
                return [obj_data]
        return []

    def _apply_filter(self, objects: List[Dict], filter_pattern: str) -> List[Dict]:
        """Filter out objects matching regex pattern"""
        try:
            regex = re.compile(filter_pattern)
            return [obj for obj in objects if not regex.search(obj.get("name", ""))]
        except re.error:
            # Invalid regex, return all objects
            return objects

    def _apply_limit(self, objects: List[Dict], limit_pattern: str) -> List[Dict]:
        """Limit to objects matching regex pattern"""
        try:
            regex = re.compile(limit_pattern)
            return [obj for obj in objects if regex.search(obj.get("name", ""))]
        except re.error:
            # Invalid regex, return all objects
            return objects

    def _evaluate_states(self, objects: List[Dict], objecttype: str) -> CheckResult:
        """
        Evaluate state for all objects and aggregate results

        Args:
            objects: List of objects from NITRO API
            objecttype: Type of objects being checked

        Returns:
            CheckResult with aggregated status
        """
        total = len(objects)
        ok_count = 0
        warning_count = 0
        critical_count = 0
        unknown_count = 0

        critical_objects = []
        warning_objects = []
        long_output = []

        for obj in objects:
            name = obj.get("name", "unknown")
            state = obj.get("state", "UNKNOWN").upper()

            # Determine status for this object
            if state in self.OK_STATES:
                ok_count += 1
                status_str = "OK"
            elif state in self.WARNING_STATES:
                warning_count += 1
                status_str = "WARNING"
                warning_objects.append(name)
            elif state in self.CRITICAL_STATES:
                critical_count += 1
                status_str = "CRITICAL"
                critical_objects.append(name)
            else:
                unknown_count += 1
                status_str = "UNKNOWN"
                warning_objects.append(name)

            # Add to long output
            long_output.append(f"{name}: {state} ({status_str})")

        # Determine overall status
        if critical_count > 0:
            overall_status = STATE_CRITICAL
        elif warning_count > 0 or unknown_count > 0:
            overall_status = STATE_WARNING
        else:
            overall_status = STATE_OK

        # Build message
        message = self._build_message(
            objecttype,
            total,
            ok_count,
            warning_count,
            critical_count,
            unknown_count,
            critical_objects,
            warning_objects,
        )

        # Build performance data
        perfdata = {
            "total": total,
            "ok": ok_count,
            "warning": warning_count,
            "critical": critical_count,
            "unknown": unknown_count,
        }

        return CheckResult(
            status=overall_status,
            message=message,
            perfdata=perfdata,
            long_output=long_output if len(objects) > 1 else [],
        )

    def _build_message(
        self,
        objecttype: str,
        total: int,
        ok: int,
        warning: int,
        critical: int,
        unknown: int,
        critical_objects: List[str],
        warning_objects: List[str],
    ) -> str:
        """Build status message"""
        parts = []

        if critical > 0:
            parts.append(f"{critical}/{total} {objecttype} CRITICAL")
            if critical_objects and critical <= 5:
                parts.append(f"({', '.join(critical_objects)})")

        if warning > 0 or unknown > 0:
            warn_total = warning + unknown
            parts.append(f"{warn_total}/{total} {objecttype} WARNING")
            if warning_objects and warn_total <= 5:
                parts.append(f"({', '.join(warning_objects)})")

        if ok == total:
            if total == 1:
                parts.append(f"{objecttype} is UP")
            else:
                parts.append(f"All {total} {objecttype} are UP")

        return " ".join(parts) if parts else f"{total} {objecttype} checked"
