"""
Hardware information display command
"""

from typing import List

from check_netscaler.client.exceptions import NITROException
from check_netscaler.commands.base import BaseCommand, CheckResult
from check_netscaler.constants import STATE_OK, STATE_UNKNOWN


class HWInfoCommand(BaseCommand):
    """Display NetScaler hardware and version information"""

    def execute(self) -> CheckResult:
        """
        Execute hwinfo command

        Returns:
            CheckResult with hardware and version information (always OK)
        """
        try:
            # Get hardware information
            hw_data = self.client.get_config("nshardware")

            if "nshardware" not in hw_data:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message="nshardware data not found in API response",
                )

            hw = hw_data["nshardware"]

            # Handle both single object and list
            if isinstance(hw, list):
                hw = hw[0] if hw else {}

            # Get version information
            ver_data = self.client.get_config("nsversion")

            if "nsversion" not in ver_data:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message="nsversion data not found in API response",
                )

            ver = ver_data["nsversion"]

            # Handle both single object and list
            if isinstance(ver, list):
                ver = ver[0] if ver else {}

            # Build output messages
            info_lines: List[str] = []

            # Platform information
            platform = f"{hw.get('hwdescription', 'Unknown')} {hw.get('sysid', '')}"
            info_lines.append(f"Platform: {platform.strip()}")

            # Manufacture date
            year = hw.get("manufactureyear", "")
            month = hw.get("manufacturemonth", "")
            day = hw.get("manufactureday", "")
            if year and month and day:
                info_lines.append(f"Manufactured on: {year}/{month}/{day}")

            # CPU frequency
            cpu_freq = hw.get("cpufrequncy", "")  # Note: typo in API field name
            if cpu_freq:
                info_lines.append(f"CPU: {cpu_freq}MHz")

            # Serial number
            serial = hw.get("serialno", "")
            if serial:
                info_lines.append(f"Serial no: {serial}")

            # Build version
            version = ver.get("version", "Unknown")
            info_lines.append(f"Build Version: {version}")

            # Create single-line message for Nagios output
            message = "; ".join(info_lines)

            return CheckResult(
                status=STATE_OK,
                message=message,
            )

        except NITROException as e:
            return CheckResult(
                status=STATE_UNKNOWN,
                message=f"Error retrieving hardware info: {str(e)}",
            )
        except Exception as e:
            return CheckResult(
                status=STATE_UNKNOWN,
                message=f"Unexpected error: {str(e)}",
            )
