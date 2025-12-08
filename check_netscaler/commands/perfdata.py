"""
Generic performance data collection command
"""

from typing import Dict

from check_netscaler.client.exceptions import NITROException
from check_netscaler.commands.base import BaseCommand, CheckResult
from check_netscaler.constants import (
    STATE_OK,
    STATE_UNKNOWN,
)


class PerfdataCommand(BaseCommand):
    """Collect arbitrary performance data fields"""

    def execute(self) -> CheckResult:
        """
        Execute perfdata check

        Returns:
            CheckResult with performance data
        """
        try:
            # Get objecttype (required)
            objecttype = getattr(self.args, "objecttype", None)
            if not objecttype:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message="perfdata: objecttype is required",
                )

            # Get objectname (optional)
            objectname = getattr(self.args, "objectname", None)

            # Get endpoint (default to stat)
            endpoint = getattr(self.args, "endpoint", None) or "stat"

            # Get fields to collect (from warning parameter, comma-separated)
            fields_str = getattr(self.args, "warning", None)
            if not fields_str:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message="perfdata: fields are required (use --warning parameter with comma-separated field names)",
                )

            fields = [f.strip() for f in fields_str.split(",")]

            # Fetch data
            if endpoint == "stat":
                data = self.client.get_stat(objecttype, objectname)
            elif endpoint == "config":
                data = self.client.get_config(objecttype, objectname)
            else:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message=f"Invalid endpoint: {endpoint}",
                )

            if objecttype not in data:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message=f"perfdata: objecttype '{objecttype}' not found in API response",
                )

            response = data[objecttype]

            # Handle both single object and list
            if not isinstance(response, list):
                response = [response]

            if not response:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message="perfdata: no data found",
                )

            # Get label field (optional)
            label_field = getattr(self.args, "label", None)
            separator = getattr(self.args, "separator", ".")

            # Collect performance data
            perfdata: Dict[str, float] = {}

            for idx, obj in enumerate(response):
                # Determine label for this object
                if label_field and label_field in obj:
                    label_prefix = str(obj[label_field])
                elif len(response) > 1:
                    # Multiple objects without label field, use index
                    label_prefix = str(idx)
                else:
                    # Single object, no prefix needed
                    label_prefix = None

                # Collect each field
                for field in fields:
                    if field not in obj:
                        continue

                    try:
                        value = float(obj[field])

                        # Build perfdata label
                        if label_prefix:
                            perfdata_label = f"{label_prefix}{separator}{field}"
                        else:
                            perfdata_label = field

                        perfdata[perfdata_label] = value
                    except (ValueError, TypeError):
                        # Skip non-numeric values
                        pass

            if not perfdata:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message=f"perfdata: no numeric values found for fields: {', '.join(fields)}",
                )

            # Build message
            message = f"perfdata: collected {len(perfdata)} metrics from {objecttype}"
            if objectname:
                message += f" ({objectname})"

            return CheckResult(
                status=STATE_OK,
                message=message,
                perfdata=perfdata,
            )

        except NITROException as e:
            return CheckResult(
                status=STATE_UNKNOWN,
                message=f"Error collecting perfdata: {str(e)}",
            )
        except Exception as e:
            return CheckResult(
                status=STATE_UNKNOWN,
                message=f"Unexpected error: {str(e)}",
            )
