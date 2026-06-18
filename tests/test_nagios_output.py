"""
Tests for Nagios output formatting.
"""

from check_netscaler.output.nagios import NagiosOutput


class TestNagiosOutput:
    """Test Nagios perfdata formatting helpers."""

    def test_format_perfdata_with_threshold_metadata(self):
        """Perfdata dict items can include threshold metadata."""
        output = NagiosOutput.format_output(
            status=0,
            message="web_lb state: UP, Health: 95%",
            perfdata={
                "web_lb.health": {
                    "value": "95",
                    "uom": "%",
                    "warn": "95",
                    "crit": "80",
                    "min": "0",
                    "max": "100",
                },
                "total": 1,
            },
        )

        assert "'web_lb.health'=95%;95;80;0;100" in output
        assert "'total'=1;;" in output
