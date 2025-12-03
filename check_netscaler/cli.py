"""
Command-line interface for check_netscaler
"""
import argparse
import sys
from typing import List, Optional

from check_netscaler import __version__
from check_netscaler.constants import (
    DEFAULT_USERNAME,
    DEFAULT_PASSWORD,
    DEFAULT_TIMEOUT,
    DEFAULT_API_VERSION,
    STATE_UNKNOWN,
)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser"""
    parser = argparse.ArgumentParser(
        prog="check_netscaler",
        description="Nagios/Icinga monitoring plugin for Citrix NetScaler ADC",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Version
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    # Connection arguments
    parser.add_argument(
        "-H", "--hostname",
        required=True,
        help="Hostname or IP address of the NetScaler appliance",
    )

    parser.add_argument(
        "-u", "--username",
        default=DEFAULT_USERNAME,
        help=f"Username for authentication (default: {DEFAULT_USERNAME})",
    )

    parser.add_argument(
        "-p", "--password",
        default=DEFAULT_PASSWORD,
        help=f"Password for authentication (default: {DEFAULT_PASSWORD})",
    )

    parser.add_argument(
        "-s", "--ssl",
        action="store_true",
        help="Use HTTPS instead of HTTP",
    )

    parser.add_argument(
        "-P", "--port",
        type=int,
        help="TCP port to connect to (default: 80 for HTTP, 443 for HTTPS)",
    )

    parser.add_argument(
        "-a", "--api",
        default=DEFAULT_API_VERSION,
        help=f"NITRO API version (default: {DEFAULT_API_VERSION})",
    )

    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Connection timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )

    # Check command arguments
    parser.add_argument(
        "-C", "--command",
        required=True,
        choices=[
            "state", "sslcert", "above", "below", "matches", "matches_not",
            "nsconfig", "hastatus", "servicegroup", "hwinfo", "interfaces",
            "perfdata", "license", "staserver", "ntp", "debug"
        ],
        help="Check command to execute",
    )

    parser.add_argument(
        "-o", "--objecttype",
        help="Object type to check (e.g., lbvserver, service, servicegroup)",
    )

    parser.add_argument(
        "-n", "--objectname",
        help="Filter by specific object name",
    )

    parser.add_argument(
        "-e", "--endpoint",
        choices=["stat", "config"],
        help="API endpoint type (stat or config)",
    )

    # Threshold arguments
    parser.add_argument(
        "-w", "--warning",
        help="Warning threshold",
    )

    parser.add_argument(
        "-c", "--critical",
        help="Critical threshold",
    )

    # Additional options
    parser.add_argument(
        "-f", "--filter",
        help="Filter objects using regular expression",
    )

    parser.add_argument(
        "-l", "--limit",
        help="Limit check to objects matching pattern (regex)",
    )

    parser.add_argument(
        "-L", "--label",
        help="Field name to use as label in output",
    )

    parser.add_argument(
        "--separator",
        default=".",
        help="Separator for performance data labels (default: .)",
    )

    parser.add_argument(
        "-x", "--urlopts",
        help="Additional URL options for API requests",
    )

    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help="Increase output verbosity (can be repeated)",
    )

    return parser


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for CLI"""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # TODO: Implement actual check logic
    # For now, just print a message
    print(f"check_netscaler v{__version__}")
    print(f"Command: {parsed_args.command}")
    print(f"Host: {parsed_args.hostname}")
    print("UNKNOWN - Not yet implemented")

    return STATE_UNKNOWN


if __name__ == "__main__":
    sys.exit(main())
