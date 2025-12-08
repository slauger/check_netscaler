"""
Nagios/Icinga plugin output formatter
"""

from typing import Any, Dict, List, Optional

from check_netscaler.constants import STATE_NAMES


class NagiosOutput:
    """Format output according to Nagios plugin guidelines"""

    @staticmethod
    def format_output(
        status: int,
        message: str,
        perfdata: Optional[Dict[str, Any]] = None,
        long_output: Optional[List[str]] = None,
        separator: str = ".",
        label_prefix: str = "",
    ) -> str:
        """
        Format complete plugin output

        Args:
            status: Exit code (0=OK, 1=WARNING, 2=CRITICAL, 3=UNKNOWN)
            message: Main status message
            perfdata: Performance data dictionary
            long_output: Additional output lines
            separator: Separator for performance data labels
            label_prefix: Prefix for performance data labels

        Returns:
            Formatted output string

        Format:
            STATUS_NAME - message | perfdata
            long_output_line_1
            long_output_line_2
        """
        # Status line
        status_name = STATE_NAMES.get(status, "UNKNOWN")
        output_parts = [f"{status_name} - {message}"]

        # Add performance data
        if perfdata:
            perfdata_str = NagiosOutput.format_perfdata(
                perfdata, separator=separator, label_prefix=label_prefix
            )
            if perfdata_str:
                output_parts[0] += f" | {perfdata_str}"

        # Add long output
        if long_output:
            output_parts.extend(long_output)

        return "\n".join(output_parts)

    @staticmethod
    def format_perfdata(
        data: Dict[str, Any],
        separator: str = ".",
        label_prefix: str = "",
        warn: Optional[str] = None,
        crit: Optional[str] = None,
    ) -> str:
        """
        Format performance data according to Nagios format

        Args:
            data: Dictionary of metric_name -> value
            separator: Separator for label parts (default: .)
            label_prefix: Prefix for all labels
            warn: Warning threshold
            crit: Critical threshold

        Returns:
            Formatted perfdata string

        Format:
            'label'=value[UOM];[warn];[crit];[min];[max]

        Example:
            {'active': 10, 'down': 0} -> 'active'=10;; 'down'=0;;
        """
        if not data:
            return ""

        perfdata_parts = []

        for key, value in data.items():
            # Build label
            if label_prefix:
                label = f"{label_prefix}{separator}{key}"
            else:
                label = key

            # Format value
            # Nagios perfdata format: 'label'=value[UOM];[warn];[crit];[min];[max]
            perfdata_str = f"'{label}'={value}"

            # Add thresholds if provided
            if warn is not None or crit is not None:
                perfdata_str += f";{warn or ''};{crit or ''}"
            else:
                perfdata_str += ";;"

            perfdata_parts.append(perfdata_str)

        return " ".join(perfdata_parts)

    @staticmethod
    def format_perfdata_item(
        label: str,
        value: Any,
        uom: str = "",
        warn: Optional[str] = None,
        crit: Optional[str] = None,
        min_val: Optional[str] = None,
        max_val: Optional[str] = None,
    ) -> str:
        """
        Format a single performance data item

        Args:
            label: Metric label
            value: Metric value
            uom: Unit of measurement (%, s, ms, B, KB, MB, GB, c for counter)
            warn: Warning threshold
            crit: Critical threshold
            min_val: Minimum value
            max_val: Maximum value

        Returns:
            Formatted perfdata string

        Format:
            'label'=value[UOM];[warn];[crit];[min];[max]
        """
        perfdata = f"'{label}'={value}{uom}"

        # Add thresholds and limits
        thresholds = [
            warn or "",
            crit or "",
            min_val or "",
            max_val or "",
        ]

        # Only add threshold part if at least one is set
        if any(thresholds):
            perfdata += ";" + ";".join(thresholds)

        return perfdata
