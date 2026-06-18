"""
State check command - monitors vServer, service, servicegroup, and server states
"""

import re
from typing import Any, Dict, List, Optional, Tuple

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

            # Check backup vServer status if requested (only for lbvserver)
            if (
                hasattr(self.args, "check_backup")
                and self.args.check_backup
                and objecttype == "lbvserver"
            ):
                result = self._check_backup_status(result, objectname)

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
        if objecttype == "lbvserver" and self._lbvserver_health_check_enabled():
            return self._evaluate_lbvserver_states(objects)

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

            # Add to long output with Icinga2-compatible status tags
            long_output.append(f"[{status_str}] {name}: {state}")

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

    def _evaluate_lbvserver_states(self, objects: List[Dict]) -> CheckResult:
        """Evaluate lbvserver status using stat state and health percentage."""
        total = len(objects)
        ok_count = 0
        warning_count = 0
        critical_count = 0
        unknown_count = 0

        critical_objects = []
        warning_objects = []
        long_output = []
        perfdata = {}
        warning_threshold, critical_threshold = self._get_lbvserver_health_thresholds()

        for obj in objects:
            name = obj.get("name", "unknown")
            state = self._get_lbvserver_state(obj)
            health = self._get_lbvserver_health(obj)

            if state != "UP":
                critical_count += 1
                status_str = "CRITICAL"
                critical_objects.append(name)
            elif health is None:
                ok_count += 1
                status_str = "OK"
            elif health <= critical_threshold:
                critical_count += 1
                status_str = "CRITICAL"
                critical_objects.append(name)
            elif health < warning_threshold:
                warning_count += 1
                status_str = "WARNING"
                warning_objects.append(name)
            else:
                ok_count += 1
                status_str = "OK"

            health_text = self._format_health(health)
            details = state if health_text is None else f"{state}, health={health_text}"
            long_output.append(f"[{status_str}] {name}: {details}")

            if health is not None:
                perfdata[f"{name}.health"] = self._build_lbvserver_health_perfdata(
                    health, warning_threshold, critical_threshold
                )

        if critical_count > 0:
            overall_status = STATE_CRITICAL
        elif warning_count > 0 or unknown_count > 0:
            overall_status = STATE_WARNING
        else:
            overall_status = STATE_OK

        message = self._build_lbvserver_message(
            objects,
            ok_count,
            warning_count,
            critical_count,
            unknown_count,
            critical_objects,
            warning_objects,
        )

        perfdata.update(
            {
                "total": total,
                "ok": ok_count,
                "warning": warning_count,
                "critical": critical_count,
                "unknown": unknown_count,
            }
        )

        if total == 1:
            health = self._get_lbvserver_health(objects[0])
            health_text = self._format_health(health)
            if health is not None:
                perfdata["health"] = self._build_lbvserver_health_perfdata(
                    health, warning_threshold, critical_threshold
                )

        return CheckResult(
            status=overall_status,
            message=message,
            perfdata=perfdata,
            long_output=long_output if len(objects) > 1 else [],
        )

    def _lbvserver_health_check_enabled(self) -> bool:
        """Return whether lbvserver health evaluation is enabled via thresholds."""
        return (
            getattr(self.args, "warning", None) is not None
            or getattr(self.args, "critical", None) is not None
        )

    def _build_lbvserver_message(
        self,
        objects: List[Dict],
        ok: int,
        warning: int,
        critical: int,
        unknown: int,
        critical_objects: List[str],
        warning_objects: List[str],
    ) -> str:
        """Build lbvserver-specific messages with state and health."""
        total = len(objects)
        if total == 1:
            obj = objects[0]
            name = obj.get("name", "unknown")
            state = self._get_lbvserver_state(obj)
            health_text = self._format_health(self._get_lbvserver_health(obj))
            if health_text is None:
                return f"{name} state: {state}"
            return f"{name} state: {state}, Health: {health_text}"

        return self._build_message(
            "lbvserver",
            total,
            ok,
            warning,
            critical,
            unknown,
            critical_objects,
            warning_objects,
        )

    def _get_lbvserver_state(self, obj: Dict[str, Any]) -> str:
        """Return lbvserver state from the stat response."""
        state = obj.get("state") or "UNKNOWN"
        return str(state).upper()

    def _get_lbvserver_health(self, obj: Dict[str, Any]) -> Optional[float]:
        """Return lbvserver health percentage when provided by the API."""
        for field in ("health", "vslbhealth"):
            value = obj.get(field)
            if value is None:
                continue
            try:
                return float(value)
            except (TypeError, ValueError):
                return None
        return None

    def _format_health(self, health: Optional[float]) -> Optional[str]:
        """Format health as a percentage without trailing decimals when possible."""
        if health is None:
            return None
        if float(health).is_integer():
            return f"{int(health)}%"
        return f"{health:g}%"

    def _build_lbvserver_health_perfdata(
        self, health: float, warning_threshold: float, critical_threshold: float
    ) -> Dict[str, str]:
        """Build perfdata metadata for lbvserver health."""
        return {
            "value": f"{health:g}",
            "uom": "%",
            "warn": f"{warning_threshold:g}",
            "crit": f"{critical_threshold:g}",
            "min": "0",
            "max": "100",
        }

    def _get_lbvserver_health_thresholds(self) -> Tuple[float, float]:
        """Return warning and critical health thresholds for lbvserver checks."""
        warning = self._parse_lbvserver_health_threshold(getattr(self.args, "warning", None), 100.0)
        critical = self._parse_lbvserver_health_threshold(getattr(self.args, "critical", None), 0.0)

        if critical > warning:
            raise ValueError(
                f"Invalid lbvserver health thresholds: critical ({critical:g}) cannot exceed warning ({warning:g})"
            )

        return warning, critical

    def _parse_lbvserver_health_threshold(self, value: Optional[str], default: float) -> float:
        """Parse lbvserver health threshold from CLI, preserving legacy defaults."""
        if value is None:
            return default

        try:
            threshold = float(value)
        except ValueError as exc:
            raise ValueError(f"Invalid lbvserver health threshold: {value}") from exc

        if threshold < 0 or threshold > 100:
            raise ValueError(
                f"Invalid lbvserver health threshold: {threshold:g} (must be between 0 and 100)"
            )

        return threshold

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

    def _check_backup_status(self, result: CheckResult, objectname: str) -> CheckResult:
        """
        Check backup vServer status for lbvserver objects

        Args:
            result: Current check result
            objectname: Name of the lbvserver to check

        Returns:
            Modified CheckResult with backup status evaluation
        """
        try:
            # Get config data to check backup status
            config_data = self.client.get_config("lbvserver", objectname)

            if "lbvserver" not in config_data:
                # No config data found, return original result
                return result

            lb_objects = config_data["lbvserver"]
            if not isinstance(lb_objects, list):
                lb_objects = [lb_objects]

            for lb_obj in lb_objects:
                # Check if backup vServer is configured
                backup_vserver = lb_obj.get("backupvserver")
                if not backup_vserver:
                    # No backup configured, nothing to check
                    continue

                # Check if backup is currently active
                backup_status = lb_obj.get("backupvserverstatus")
                if backup_status == "(Backup Active)":
                    # Backup is active - determine severity
                    backup_severity = (
                        STATE_CRITICAL if self.args.check_backup == "critical" else STATE_WARNING
                    )

                    # Update status if backup issue is more severe
                    if backup_severity > result.status:
                        result.status = backup_severity

                    # Add to message
                    vserver_name = lb_obj.get("name", "unknown")
                    backup_msg = f"Backup vServer active: {backup_vserver}"
                    if backup_msg not in result.message:
                        result.message = f"{result.message}; {backup_msg}"

                    # Add to long output
                    severity_tag = "CRITICAL" if backup_severity == STATE_CRITICAL else "WARNING"
                    long_output_msg = f"[{severity_tag}] {vserver_name}: Backup vServer '{backup_vserver}' is active"
                    if long_output_msg not in result.long_output:
                        result.long_output.append(long_output_msg)

            return result

        except Exception:
            # If backup check fails, return original result
            # Don't fail the entire check because of backup check issues
            return result
