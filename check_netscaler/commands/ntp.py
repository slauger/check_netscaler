"""
NTP synchronization status check command
"""

from typing import Dict

from check_netscaler.client.exceptions import NITROException
from check_netscaler.commands.base import BaseCommand, CheckResult
from check_netscaler.constants import (
    STATE_CRITICAL,
    STATE_OK,
    STATE_UNKNOWN,
    STATE_WARNING,
)


class NTPCommand(BaseCommand):
    """Check NTP synchronization status (compatible with check_ntp_peer)"""

    def execute(self) -> CheckResult:
        """
        Execute NTP check

        Returns:
            CheckResult indicating NTP synchronization status
        """
        try:
            # Check if NTP sync is enabled
            sync_data = self.client.get_config("ntpsync")

            if "ntpsync" not in sync_data:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message="ntp: ntpsync not found in API response",
                )

            ntpsync = sync_data["ntpsync"]
            if isinstance(ntpsync, list):
                ntpsync = ntpsync[0] if ntpsync else {}

            state = ntpsync.get("state", "")
            if state != "ENABLED":
                return CheckResult(
                    status=STATE_CRITICAL,
                    message=f"ntp: Sync {state}",
                )

            # Get NTP status (peer list)
            status_data = self.client.get_config("ntpstatus")

            if "ntpstatus" not in status_data:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message="ntp: ntpstatus not found in API response",
                )

            ntpstatus = status_data["ntpstatus"]
            if isinstance(ntpstatus, list):
                ntpstatus = ntpstatus[0] if ntpstatus else {}

            response_text = ntpstatus.get("response", "")

            # Parse NTP peer list
            ntp_info = self._parse_ntp_status(response_text)

            # Parse thresholds
            thresholds = self._parse_thresholds()

            # Check if synchronized
            if not ntp_info["synced_source"]:
                return CheckResult(
                    status=STATE_CRITICAL,
                    message=(
                        f"ntp: Server not synchronized, "
                        f"Offset {ntp_info['synced_offset']}, "
                        f"jitter={ntp_info['synced_jitter']}, "
                        f"stratum={ntp_info['synced_stratum']}, "
                        f"truechimers={ntp_info['truechimers']}"
                    ),
                )

            # Check thresholds
            status, messages = self._check_thresholds(ntp_info, thresholds)

            # Build performance data
            perfdata: Dict[str, float] = {
                "offset": float(ntp_info["synced_offset"]),
                "jitter": float(ntp_info["synced_jitter"]),
                "stratum": float(ntp_info["synced_stratum"]),
                "truechimers": float(ntp_info["truechimers"]),
            }

            message = "ntp: " + ", ".join(messages)

            return CheckResult(
                status=status,
                message=message,
                perfdata=perfdata,
            )

        except NITROException as e:
            return CheckResult(
                status=STATE_UNKNOWN,
                message=f"Error checking ntp: {str(e)}",
            )
        except Exception as e:
            return CheckResult(
                status=STATE_UNKNOWN,
                message=f"Unexpected error: {str(e)}",
            )

    def _parse_ntp_status(self, response_text: str) -> Dict:
        """Parse ntpstatus response text"""
        ntp_info = {
            "synced_source": None,
            "synced_stratum": -1,
            "synced_offset": "unknown",
            "synced_jitter": -1.0,
            "truechimers": 0,
        }

        peer_list_started = False

        for line in response_text.splitlines():
            line = line.strip()
            if not line:
                continue

            # Check if peer list has started (line starts with =)
            if line.startswith("="):
                peer_list_started = True
                continue

            if not peer_list_started:
                continue

            # Parse peer line
            if len(line) < 1:
                continue

            sync_status = line[0]
            parts = line[1:].split()

            if len(parts) < 10:
                continue

            ntp_source = parts[0]
            ntp_peer_stratum = parts[2]
            ntp_peer_offset = parts[8]  # in milliseconds
            ntp_peer_jitter = parts[9]

            # * = synchronized peer
            if sync_status == "*":
                try:
                    # Convert offset from ms to seconds
                    ntp_info["synced_source"] = ntp_source
                    ntp_info["synced_stratum"] = int(ntp_peer_stratum)
                    ntp_info["synced_offset"] = f"{float(ntp_peer_offset) / 1000:.6f}"
                    ntp_info["synced_jitter"] = float(ntp_peer_jitter)
                except (ValueError, TypeError):
                    pass

            # *, +, - are truechimers (possible sync sources)
            if sync_status in ["*", "+", "-"]:
                ntp_info["truechimers"] += 1

        return ntp_info

    def _parse_thresholds(self) -> Dict:
        """Parse threshold parameters (format: o=0.03,s=1,j=100,t=3)"""
        thresholds = {
            "offset_warning": None,
            "offset_critical": None,
            "jitter_warning": None,
            "jitter_critical": None,
            "stratum_warning": None,
            "stratum_critical": None,
            "truechimers_warning": None,
            "truechimers_critical": None,
        }

        # Parse warning thresholds
        warning = getattr(self.args, "warning", None)
        if warning:
            for item in warning.split(","):
                item = item.strip()
                if "=" in item:
                    key, value = item.split("=", 1)
                    key = key.strip()
                    try:
                        if key == "o":
                            thresholds["offset_warning"] = float(value)
                        elif key == "j":
                            thresholds["jitter_warning"] = float(value)
                        elif key == "s":
                            thresholds["stratum_warning"] = int(value)
                        elif key == "t":
                            thresholds["truechimers_warning"] = int(value)
                    except (ValueError, TypeError):
                        pass

        # Parse critical thresholds
        critical = getattr(self.args, "critical", None)
        if critical:
            for item in critical.split(","):
                item = item.strip()
                if "=" in item:
                    key, value = item.split("=", 1)
                    key = key.strip()
                    try:
                        if key == "o":
                            thresholds["offset_critical"] = float(value)
                        elif key == "j":
                            thresholds["jitter_critical"] = float(value)
                        elif key == "s":
                            thresholds["stratum_critical"] = int(value)
                        elif key == "t":
                            thresholds["truechimers_critical"] = int(value)
                    except (ValueError, TypeError):
                        pass

        return thresholds

    def _check_thresholds(self, ntp_info: Dict, thresholds: Dict) -> tuple:
        """Check NTP metrics against thresholds"""
        worst_status = STATE_OK
        messages = []

        # Check offset (absolute value)
        offset = float(ntp_info["synced_offset"])
        offset_text = f"Offset {ntp_info['synced_offset']} secs"

        if thresholds["offset_critical"] is not None:
            if abs(offset) >= thresholds["offset_critical"]:
                worst_status = STATE_CRITICAL
                offset_text += " (CRITICAL)"
        elif thresholds["offset_warning"] is not None:
            if abs(offset) >= thresholds["offset_warning"]:
                worst_status = STATE_WARNING
                offset_text += " (WARNING)"

        messages.append(offset_text)

        # Check jitter
        jitter = ntp_info["synced_jitter"]
        jitter_text = f"jitter={jitter}"

        if thresholds["jitter_critical"] is not None:
            if jitter >= thresholds["jitter_critical"]:
                if worst_status != STATE_CRITICAL:
                    worst_status = STATE_CRITICAL
                jitter_text += " (CRITICAL)"
        elif thresholds["jitter_warning"] is not None:
            if jitter >= thresholds["jitter_warning"]:
                if worst_status == STATE_OK:
                    worst_status = STATE_WARNING
                jitter_text += " (WARNING)"

        messages.append(jitter_text)

        # Check stratum (higher is worse)
        stratum = ntp_info["synced_stratum"]
        stratum_text = f"stratum={stratum}"

        if thresholds["stratum_critical"] is not None:
            if stratum > thresholds["stratum_critical"]:
                if worst_status != STATE_CRITICAL:
                    worst_status = STATE_CRITICAL
                stratum_text += " (CRITICAL)"
        elif thresholds["stratum_warning"] is not None:
            if stratum > thresholds["stratum_warning"]:
                if worst_status == STATE_OK:
                    worst_status = STATE_WARNING
                stratum_text += " (WARNING)"

        messages.append(stratum_text)

        # Check truechimers (lower is worse)
        truechimers = ntp_info["truechimers"]
        truechimers_text = f"truechimers={truechimers}"

        if thresholds["truechimers_critical"] is not None:
            if truechimers <= thresholds["truechimers_critical"]:
                if worst_status != STATE_CRITICAL:
                    worst_status = STATE_CRITICAL
                truechimers_text += " (CRITICAL)"
        elif thresholds["truechimers_warning"] is not None:
            if truechimers <= thresholds["truechimers_warning"]:
                if worst_status == STATE_OK:
                    worst_status = STATE_WARNING
                truechimers_text += " (WARNING)"

        messages.append(truechimers_text)

        return worst_status, messages
