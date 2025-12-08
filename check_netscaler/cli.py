"""
Command-line interface for check_netscaler
"""

import argparse
import os
import sys
from typing import List, Optional

from check_netscaler import __version__
from check_netscaler.constants import (
    DEFAULT_API_VERSION,
    DEFAULT_PASSWORD,
    DEFAULT_TIMEOUT,
    DEFAULT_USERNAME,
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
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    # Connection arguments
    parser.add_argument(
        "-H",
        "--hostname",
        default=os.getenv("NETSCALER_HOST"),
        help="Hostname or IP address of the NetScaler appliance (env: NETSCALER_HOST)",
    )

    parser.add_argument(
        "-u",
        "--username",
        default=os.getenv("NETSCALER_USER", DEFAULT_USERNAME),
        help=f"Username for authentication (env: NETSCALER_USER, default: {DEFAULT_USERNAME})",
    )

    parser.add_argument(
        "-p",
        "--password",
        default=os.getenv("NETSCALER_PASS", DEFAULT_PASSWORD),
        help=f"Password for authentication (env: NETSCALER_PASS, default: {DEFAULT_PASSWORD})",
    )

    parser.add_argument(
        "--no-ssl",
        dest="ssl",
        action="store_false",
        default=True,
        help="Use HTTP instead of HTTPS (default: HTTPS)",
    )

    parser.add_argument(
        "-P",
        "--port",
        type=int,
        help="TCP port to connect to (default: 80 for HTTP, 443 for HTTPS)",
    )

    parser.add_argument(
        "-a",
        "--api",
        default=DEFAULT_API_VERSION,
        help=f"NITRO API version (default: {DEFAULT_API_VERSION})",
    )

    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Connection timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )

    # Check command arguments
    parser.add_argument(
        "-C",
        "--command",
        required=True,
        choices=[
            "state",
            "sslcert",
            "above",
            "below",
            "matches",
            "matches_not",
            "nsconfig",
            "hastatus",
            "servicegroup",
            "hwinfo",
            "interfaces",
            "perfdata",
            "license",
            "staserver",
            "ntp",
            "debug",
        ],
        help="Check command to execute",
    )

    parser.add_argument(
        "-o",
        "--objecttype",
        help="Object type to check (e.g., lbvserver, service, servicegroup)",
    )

    parser.add_argument(
        "-n",
        "--objectname",
        help="Filter by specific object name",
    )

    parser.add_argument(
        "-e",
        "--endpoint",
        choices=["stat", "config"],
        help="API endpoint type (stat or config)",
    )

    # Threshold arguments
    parser.add_argument(
        "-w",
        "--warning",
        help="Warning threshold",
    )

    parser.add_argument(
        "-c",
        "--critical",
        help="Critical threshold",
    )

    # Additional options
    parser.add_argument(
        "-f",
        "--filter",
        help="Filter objects using regular expression",
    )

    parser.add_argument(
        "-l",
        "--limit",
        help="Limit check to objects matching pattern (regex)",
    )

    parser.add_argument(
        "-L",
        "--label",
        help="Field name to use as label in output",
    )

    parser.add_argument(
        "--separator",
        default=".",
        help="Separator for performance data labels (default: .)",
    )

    parser.add_argument(
        "-x",
        "--urlopts",
        help="Additional URL options for API requests",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase output verbosity (can be repeated)",
    )

    return parser


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for CLI"""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Validate required arguments
    if not parsed_args.hostname:
        parser.error("argument -H/--hostname is required (or set NETSCALER_HOST)")

    try:
        # Import here to avoid circular dependencies
        from check_netscaler.client import NITROClient
        from check_netscaler.commands.state import StateCommand
        from check_netscaler.output.nagios import NagiosOutput

        # Create NITRO client
        client = NITROClient(
            hostname=parsed_args.hostname,
            username=parsed_args.username,
            password=parsed_args.password,
            ssl=parsed_args.ssl,
            port=parsed_args.port,
            timeout=parsed_args.timeout,
            verify_ssl=not parsed_args.ssl,  # TODO: Add --insecure flag
            api_version=parsed_args.api,
        )

        # Execute command
        with client:
            if parsed_args.command == "state":
                command = StateCommand(client, parsed_args)
                result = command.execute()
            elif parsed_args.command in ["above", "below"]:
                from check_netscaler.commands.threshold import ThresholdCommand

                command = ThresholdCommand(client, parsed_args)
                result = command.execute()
            elif parsed_args.command == "nsconfig":
                from check_netscaler.commands.nsconfig import NSConfigCommand

                command = NSConfigCommand(client, parsed_args)
                result = command.execute()
            elif parsed_args.command == "hwinfo":
                from check_netscaler.commands.hwinfo import HWInfoCommand

                command = HWInfoCommand(client, parsed_args)
                result = command.execute()
            elif parsed_args.command == "sslcert":
                from check_netscaler.commands.sslcert import SSLCertCommand

                command = SSLCertCommand(client, parsed_args)
                result = command.execute()
            elif parsed_args.command == "servicegroup":
                from check_netscaler.commands.servicegroup import ServiceGroupCommand

                command = ServiceGroupCommand(client, parsed_args)
                result = command.execute()
            elif parsed_args.command in ["matches", "matches_not"]:
                from check_netscaler.commands.matches import MatchesCommand

                command = MatchesCommand(client, parsed_args)
                result = command.execute()
            elif parsed_args.command == "staserver":
                from check_netscaler.commands.staserver import STAServerCommand

                command = STAServerCommand(client, parsed_args)
                result = command.execute()
            elif parsed_args.command == "hastatus":
                from check_netscaler.commands.hastatus import HAStatusCommand

                command = HAStatusCommand(client, parsed_args)
                result = command.execute()
            elif parsed_args.command == "license":
                from check_netscaler.commands.license import LicenseCommand

                command = LicenseCommand(client, parsed_args)
                result = command.execute()
            elif parsed_args.command == "interfaces":
                from check_netscaler.commands.interfaces import InterfacesCommand

                command = InterfacesCommand(client, parsed_args)
                result = command.execute()
            elif parsed_args.command == "perfdata":
                from check_netscaler.commands.perfdata import PerfdataCommand

                command = PerfdataCommand(client, parsed_args)
                result = command.execute()
            elif parsed_args.command == "ntp":
                from check_netscaler.commands.ntp import NTPCommand

                command = NTPCommand(client, parsed_args)
                result = command.execute()
            elif parsed_args.command == "debug":
                from check_netscaler.commands.debug import DebugCommand

                command = DebugCommand(client, parsed_args)
                result = command.execute()
            else:
                print(f"UNKNOWN - Command '{parsed_args.command}' not yet implemented")
                return STATE_UNKNOWN

        # Format and print output
        output = NagiosOutput.format_output(
            status=result.status,
            message=result.message,
            perfdata=result.perfdata,
            long_output=result.long_output,
            separator=parsed_args.separator,
        )
        print(output)

        return result.status

    except KeyboardInterrupt:
        print("UNKNOWN - Interrupted by user")
        return STATE_UNKNOWN
    except Exception as e:
        print(f"UNKNOWN - Unexpected error: {e}")
        if parsed_args.verbose > 0:
            import traceback

            traceback.print_exc()
        return STATE_UNKNOWN


if __name__ == "__main__":
    sys.exit(main())
