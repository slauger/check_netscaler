"""
SSL certificate expiration monitoring command
"""

import re
from typing import List

from check_netscaler.client.exceptions import NITROException
from check_netscaler.commands.base import BaseCommand, CheckResult
from check_netscaler.constants import (
    STATE_CRITICAL,
    STATE_OK,
    STATE_UNKNOWN,
    STATE_WARNING,
)


class SSLCertCommand(BaseCommand):
    """Check SSL certificate expiration status"""

    def execute(self) -> CheckResult:
        """
        Execute sslcert check

        Returns:
            CheckResult indicating certificate expiration status
        """
        try:
            # Default thresholds
            warning = 30
            critical = 10

            # Parse thresholds from args
            if self.args.warning:
                try:
                    warning = int(self.args.warning)
                except ValueError:
                    return CheckResult(
                        status=STATE_UNKNOWN,
                        message=f"Invalid warning threshold: {self.args.warning}",
                    )

            if self.args.critical:
                try:
                    critical = int(self.args.critical)
                except ValueError:
                    return CheckResult(
                        status=STATE_UNKNOWN,
                        message=f"Invalid critical threshold: {self.args.critical}",
                    )

            # Get SSL certificates
            objecttype = getattr(self.args, "objecttype", None) or "sslcertkey"
            data = self.client.get_config(objecttype)

            if objecttype not in data:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message=f"{objecttype} data not found in API response",
                )

            certs = data[objecttype]

            # Handle both single object and list
            if not isinstance(certs, list):
                certs = [certs]

            if not certs:
                return CheckResult(
                    status=STATE_UNKNOWN,
                    message="No SSL certificates found",
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

            # Check each certificate
            critical_certs: List[str] = []
            warning_certs: List[str] = []
            ok_count = 0

            for cert in certs:
                certkey = cert.get("certkey", "Unknown")

                # Apply filter (skip if matches)
                if filter_regex and filter_regex.search(certkey):
                    continue

                # Apply limit (skip if doesn't match)
                if limit_regex and not limit_regex.search(certkey):
                    continue

                days_to_expiration = cert.get("daystoexpiration")

                if days_to_expiration is None:
                    # Certificate might not have expiration data
                    continue

                try:
                    days = int(days_to_expiration)
                except (ValueError, TypeError):
                    continue

                # Only count if we successfully processed the certificate
                if days <= 0:
                    critical_certs.append(f"{certkey} expired")
                elif days <= critical:
                    critical_certs.append(f"{certkey} expires in {days} days")
                elif days <= warning:
                    warning_certs.append(f"{certkey} expires in {days} days")
                else:
                    ok_count += 1

            # Determine overall status
            total_checked = ok_count + len(warning_certs) + len(critical_certs)

            if critical_certs:
                status = STATE_CRITICAL
                message = "CRITICAL: " + "; ".join(critical_certs)
                if warning_certs:
                    message += "; WARNING: " + "; ".join(warning_certs)
            elif warning_certs:
                status = STATE_WARNING
                message = "WARNING: " + "; ".join(warning_certs)
            else:
                status = STATE_OK
                message = "certificate lifetime OK"
                if total_checked > 0:
                    message = (
                        f"{total_checked} certificate(s) OK (warn={warning}d, crit={critical}d)"
                    )

            # Build long output if there are issues
            long_output: List[str] = []
            if critical_certs or warning_certs:
                for cert_msg in critical_certs:
                    long_output.append(f"CRITICAL: {cert_msg}")
                for cert_msg in warning_certs:
                    long_output.append(f"WARNING: {cert_msg}")

            return CheckResult(
                status=status,
                message=message,
                long_output=long_output,
            )

        except NITROException as e:
            return CheckResult(
                status=STATE_UNKNOWN,
                message=f"Error checking SSL certificates: {str(e)}",
            )
        except Exception as e:
            return CheckResult(
                status=STATE_UNKNOWN,
                message=f"Unexpected error: {str(e)}",
            )
