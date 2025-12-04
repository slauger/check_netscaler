"""
Tests for CLI argument parsing and basic functionality
"""
import pytest
import sys
from io import StringIO

from check_netscaler.cli import create_parser, main
from check_netscaler.constants import STATE_UNKNOWN


class TestArgumentParser:
    """Test argument parser functionality"""

    def test_parser_creation(self):
        """Test that parser can be created"""
        parser = create_parser()
        assert parser is not None
        assert parser.prog == "check_netscaler"

    def test_required_arguments(self):
        """Test that required arguments are enforced"""
        parser = create_parser()

        # Missing hostname and command should fail
        with pytest.raises(SystemExit):
            parser.parse_args([])

        # Missing command should fail
        with pytest.raises(SystemExit):
            parser.parse_args(["-H", "192.168.1.1"])

        # Missing hostname should fail
        with pytest.raises(SystemExit):
            parser.parse_args(["-C", "state"])

    def test_minimal_valid_arguments(self):
        """Test parsing with minimal required arguments"""
        parser = create_parser()
        args = parser.parse_args(["-H", "192.168.1.1", "-C", "state"])

        assert args.hostname == "192.168.1.1"
        assert args.command == "state"
        assert args.username == "nsroot"  # default
        assert args.password == "nsroot"  # default
        assert args.ssl is False
        assert args.timeout == 15

    def test_ssl_flag(self):
        """Test SSL flag parsing"""
        parser = create_parser()
        args = parser.parse_args(["-H", "192.168.1.1", "-C", "state", "-s"])

        assert args.ssl is True

    def test_custom_credentials(self):
        """Test custom username and password"""
        parser = create_parser()
        args = parser.parse_args([
            "-H", "192.168.1.1",
            "-C", "state",
            "-u", "admin",
            "-p", "secret"
        ])

        assert args.username == "admin"
        assert args.password == "secret"

    def test_custom_port(self):
        """Test custom port"""
        parser = create_parser()
        args = parser.parse_args([
            "-H", "192.168.1.1",
            "-C", "state",
            "-P", "8080"
        ])

        assert args.port == 8080

    def test_command_choices(self):
        """Test valid command choices"""
        parser = create_parser()
        valid_commands = [
            "state", "sslcert", "above", "below", "matches", "matches_not",
            "nsconfig", "hastatus", "servicegroup", "hwinfo", "interfaces",
            "perfdata", "license", "staserver", "ntp", "debug"
        ]

        for cmd in valid_commands:
            args = parser.parse_args(["-H", "192.168.1.1", "-C", cmd])
            assert args.command == cmd

    def test_invalid_command(self):
        """Test that invalid command is rejected"""
        parser = create_parser()

        with pytest.raises(SystemExit):
            parser.parse_args(["-H", "192.168.1.1", "-C", "invalid_command"])

    def test_objecttype_and_objectname(self):
        """Test objecttype and objectname arguments"""
        parser = create_parser()
        args = parser.parse_args([
            "-H", "192.168.1.1",
            "-C", "state",
            "-o", "lbvserver",
            "-n", "my_vserver"
        ])

        assert args.objecttype == "lbvserver"
        assert args.objectname == "my_vserver"

    def test_thresholds(self):
        """Test warning and critical thresholds"""
        parser = create_parser()
        args = parser.parse_args([
            "-H", "192.168.1.1",
            "-C", "above",
            "-w", "75",
            "-c", "90"
        ])

        assert args.warning == "75"
        assert args.critical == "90"

    def test_verbose_flag(self):
        """Test verbose flag (can be repeated)"""
        parser = create_parser()

        # No verbose
        args = parser.parse_args(["-H", "192.168.1.1", "-C", "state"])
        assert args.verbose == 0

        # Single verbose
        args = parser.parse_args(["-H", "192.168.1.1", "-C", "state", "-v"])
        assert args.verbose == 1

        # Multiple verbose
        args = parser.parse_args(["-H", "192.168.1.1", "-C", "state", "-v", "-v", "-v"])
        assert args.verbose == 3

    def test_filter_and_limit(self):
        """Test filter and limit options"""
        parser = create_parser()
        args = parser.parse_args([
            "-H", "192.168.1.1",
            "-C", "interfaces",
            "-f", "(LO.1|0.1)",
            "-l", "(0.2|0.3)"
        ])

        assert args.filter == "(LO.1|0.1)"
        assert args.limit == "(0.2|0.3)"

    def test_separator(self):
        """Test custom separator"""
        parser = create_parser()

        # Default separator
        args = parser.parse_args(["-H", "192.168.1.1", "-C", "state"])
        assert args.separator == "."

        # Custom separator
        args = parser.parse_args([
            "-H", "192.168.1.1",
            "-C", "state",
            "--separator", "_"
        ])
        assert args.separator == "_"

    def test_api_version(self):
        """Test API version argument"""
        parser = create_parser()

        # Default version
        args = parser.parse_args(["-H", "192.168.1.1", "-C", "state"])
        assert args.api == "v1"

        # Custom version
        args = parser.parse_args([
            "-H", "192.168.1.1",
            "-C", "state",
            "-a", "v2"
        ])
        assert args.api == "v2"


class TestMainFunction:
    """Test main entry point"""

    def test_main_invalid_args(self):
        """Test that main exits on invalid arguments"""
        with pytest.raises(SystemExit):
            main([])  # Missing required arguments

    def test_main_unimplemented_command(self, capsys):
        """Test that unimplemented commands return UNKNOWN"""
        # Use a command that's not implemented yet (perfdata is still unimplemented)
        from unittest.mock import patch, Mock

        mock_client_class = Mock()
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client

        with patch("check_netscaler.client.NITROClient", mock_client_class):
            exit_code = main(["-H", "192.168.1.1", "-C", "perfdata"])

            captured = capsys.readouterr()
            assert "not yet implemented" in captured.out.lower()
            assert exit_code == STATE_UNKNOWN
