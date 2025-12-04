"""
Tests for perfdata command
"""

from argparse import Namespace
from unittest.mock import Mock

from check_netscaler.commands.perfdata import PerfdataCommand
from check_netscaler.constants import STATE_OK, STATE_UNKNOWN


class TestPerfdataCommand:
    """Test perfdata check command"""

    def create_mock_client(self):
        """Create a mock NITRO client"""
        client = Mock()
        client.get_config = Mock()
        client.get_stat = Mock()
        return client

    def create_args(self, **kwargs):
        """Create mock arguments"""
        defaults = {
            "command": "perfdata",
            "objecttype": None,
            "objectname": None,
            "endpoint": None,
            "warning": None,  # Used for field names
            "label": None,
            "separator": ".",
        }
        defaults.update(kwargs)
        return Namespace(**defaults)

    def test_single_field_single_object(self):
        """Test collecting single field from single object"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"nscapacity": {"numcpus": "8", "maxbandwidth": "1000"}}

        args = self.create_args(objecttype="nscapacity", warning="numcpus")
        command = PerfdataCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "numcpus" in result.perfdata
        assert result.perfdata["numcpus"] == 8.0

    def test_multiple_fields_single_object(self):
        """Test collecting multiple fields from single object"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "nscapacity": {"numcpus": "8", "maxbandwidth": "1000", "maxvcpucount": "4"}
        }

        args = self.create_args(
            objecttype="nscapacity", warning="numcpus,maxbandwidth,maxvcpucount"
        )
        command = PerfdataCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "numcpus" in result.perfdata
        assert "maxbandwidth" in result.perfdata
        assert "maxvcpucount" in result.perfdata
        assert result.perfdata["numcpus"] == 8.0
        assert result.perfdata["maxbandwidth"] == 1000.0

    def test_multiple_objects_with_label(self):
        """Test collecting from multiple objects with label field"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "lbvserver": [
                {"name": "lb1", "totalpktssent": "12345", "totalpktsrecvd": "67890"},
                {"name": "lb2", "totalpktssent": "11111", "totalpktsrecvd": "22222"},
            ]
        }

        args = self.create_args(
            objecttype="lbvserver", warning="totalpktssent,totalpktsrecvd", label="name"
        )
        command = PerfdataCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "lb1.totalpktssent" in result.perfdata
        assert "lb1.totalpktsrecvd" in result.perfdata
        assert "lb2.totalpktssent" in result.perfdata
        assert "lb2.totalpktsrecvd" in result.perfdata
        assert result.perfdata["lb1.totalpktssent"] == 12345.0
        assert result.perfdata["lb2.totalpktsrecvd"] == 22222.0

    def test_multiple_objects_without_label(self):
        """Test collecting from multiple objects without label field (uses index)"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"service": [{"throughput": "100"}, {"throughput": "200"}]}

        args = self.create_args(objecttype="service", warning="throughput")
        command = PerfdataCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "0.throughput" in result.perfdata
        assert "1.throughput" in result.perfdata
        assert result.perfdata["0.throughput"] == 100.0
        assert result.perfdata["1.throughput"] == 200.0

    def test_custom_separator(self):
        """Test with custom separator"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"lbvserver": [{"name": "lb1", "totalpktssent": "12345"}]}

        args = self.create_args(
            objecttype="lbvserver", warning="totalpktssent", label="name", separator="_"
        )
        command = PerfdataCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "lb1_totalpktssent" in result.perfdata

    def test_with_objectname(self):
        """Test with specific objectname"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"lbvserver": {"name": "lb1", "totalpktssent": "12345"}}

        args = self.create_args(objecttype="lbvserver", objectname="lb1", warning="totalpktssent")
        command = PerfdataCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "totalpktssent" in result.perfdata
        assert "lb1" in result.message

    def test_config_endpoint(self):
        """Test with config endpoint"""
        client = self.create_mock_client()
        client.get_config.return_value = {"nsconfig": {"configchanges": "5"}}

        args = self.create_args(objecttype="nsconfig", warning="configchanges", endpoint="config")
        command = PerfdataCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "configchanges" in result.perfdata
        client.get_config.assert_called_once()
        client.get_stat.assert_not_called()

    def test_missing_objecttype(self):
        """Test when objecttype is not provided"""
        client = self.create_mock_client()

        args = self.create_args(warning="field1")
        command = PerfdataCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "objecttype is required" in result.message

    def test_missing_fields(self):
        """Test when fields are not provided"""
        client = self.create_mock_client()

        args = self.create_args(objecttype="lbvserver")
        command = PerfdataCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "fields are required" in result.message

    def test_invalid_endpoint(self):
        """Test with invalid endpoint"""
        client = self.create_mock_client()

        args = self.create_args(objecttype="lbvserver", warning="field1", endpoint="invalid")
        command = PerfdataCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Invalid endpoint" in result.message

    def test_objecttype_not_in_response(self):
        """Test when objecttype is not in API response"""
        client = self.create_mock_client()
        client.get_stat.return_value = {}

        args = self.create_args(objecttype="lbvserver", warning="field1")
        command = PerfdataCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "not found in API response" in result.message

    def test_empty_response(self):
        """Test when response is empty"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"lbvserver": []}

        args = self.create_args(objecttype="lbvserver", warning="field1")
        command = PerfdataCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "no data found" in result.message

    def test_field_not_in_object(self):
        """Test when requested field is not in object"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"lbvserver": {"name": "lb1", "totalpktssent": "12345"}}

        args = self.create_args(objecttype="lbvserver", warning="nonexistent")
        command = PerfdataCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "no numeric values found" in result.message

    def test_non_numeric_values_skipped(self):
        """Test that non-numeric values are skipped"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "lbvserver": {
                "name": "lb1",
                "state": "UP",  # Non-numeric
                "totalpktssent": "12345",  # Numeric
            }
        }

        args = self.create_args(objecttype="lbvserver", warning="state,totalpktssent")
        command = PerfdataCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        # Non-numeric field should be skipped
        assert "state" not in result.perfdata
        # Numeric field should be included
        assert "totalpktssent" in result.perfdata

    def test_float_values(self):
        """Test with float values"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "nscapacity": {"cpuusagepcnt": "45.5", "memusagepcnt": "67.8"}
        }

        args = self.create_args(objecttype="nscapacity", warning="cpuusagepcnt,memusagepcnt")
        command = PerfdataCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert result.perfdata["cpuusagepcnt"] == 45.5
        assert result.perfdata["memusagepcnt"] == 67.8

    def test_fields_with_spaces(self):
        """Test fields parameter with spaces around commas"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"nscapacity": {"numcpus": "8", "maxbandwidth": "1000"}}

        args = self.create_args(
            objecttype="nscapacity", warning="numcpus , maxbandwidth"  # Spaces around comma
        )
        command = PerfdataCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "numcpus" in result.perfdata
        assert "maxbandwidth" in result.perfdata

    def test_response_as_dict(self):
        """Test when response is dict instead of list"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"nscapacity": {"numcpus": "8"}}  # Dict, not list

        args = self.create_args(objecttype="nscapacity", warning="numcpus")
        command = PerfdataCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "numcpus" in result.perfdata

    def test_cache_metrics_use_case(self):
        """Test common use case: cache hits/misses"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "cache": {"cachehits": "150000", "cachemisses": "5000", "cachetotalhits": "1500000"}
        }

        args = self.create_args(objecttype="cache", warning="cachehits,cachemisses,cachetotalhits")
        command = PerfdataCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert len(result.perfdata) == 3
        assert result.perfdata["cachehits"] == 150000.0

    def test_tcp_connections_use_case(self):
        """Test common use case: TCP connections"""
        client = self.create_mock_client()
        client.get_stat.return_value = {
            "nstcpstat": {
                "tcpcurclientconn": "1234",
                "tcpcurserverconn": "5678",
                "tcptotrxpkts": "9999999",
            }
        }

        args = self.create_args(
            objecttype="nstcpstat", warning="tcpcurclientconn,tcpcurserverconn,tcptotrxpkts"
        )
        command = PerfdataCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "tcpcurclientconn" in result.perfdata
        assert "tcpcurserverconn" in result.perfdata

    def test_api_error(self):
        """Test when API returns an error"""
        from check_netscaler.client.exceptions import NITROAPIError

        client = self.create_mock_client()
        client.get_stat.side_effect = NITROAPIError("API Error")

        args = self.create_args(objecttype="lbvserver", warning="field1")
        command = PerfdataCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Error collecting perfdata" in result.message

    def test_unexpected_exception(self):
        """Test handling of unexpected exceptions"""
        client = self.create_mock_client()
        client.get_stat.side_effect = Exception("Unexpected error")

        args = self.create_args(objecttype="lbvserver", warning="field1")
        command = PerfdataCommand(client, args)
        result = command.execute()

        assert result.status == STATE_UNKNOWN
        assert "Unexpected error" in result.message

    def test_message_format(self):
        """Test message format"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"nscapacity": {"numcpus": "8"}}

        args = self.create_args(objecttype="nscapacity", warning="numcpus")
        command = PerfdataCommand(client, args)
        result = command.execute()

        assert result.message.startswith("perfdata:")
        assert "collected" in result.message
        assert "nscapacity" in result.message

    def test_message_with_objectname(self):
        """Test message includes objectname if provided"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"lbvserver": {"name": "lb1", "totalpktssent": "12345"}}

        args = self.create_args(objecttype="lbvserver", objectname="lb1", warning="totalpktssent")
        command = PerfdataCommand(client, args)
        result = command.execute()

        assert "lbvserver" in result.message
        assert "(lb1)" in result.message

    def test_zero_values(self):
        """Test that zero values are collected"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"lbvserver": {"totalpktssent": "0"}}

        args = self.create_args(objecttype="lbvserver", warning="totalpktssent")
        command = PerfdataCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert "totalpktssent" in result.perfdata
        assert result.perfdata["totalpktssent"] == 0.0

    def test_negative_values(self):
        """Test that negative values are collected"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"custom": {"delta": "-42"}}

        args = self.create_args(objecttype="custom", warning="delta")
        command = PerfdataCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert result.perfdata["delta"] == -42.0

    def test_integer_values_as_int(self):
        """Test that integer values (not strings) are handled"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"nscapacity": {"numcpus": 8}}  # Integer, not string

        args = self.create_args(objecttype="nscapacity", warning="numcpus")
        command = PerfdataCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        assert result.perfdata["numcpus"] == 8.0

    def test_label_field_not_in_object(self):
        """Test when label field doesn't exist in object (falls back to index)"""
        client = self.create_mock_client()
        client.get_stat.return_value = {"service": [{"throughput": "100"}, {"throughput": "200"}]}

        args = self.create_args(objecttype="service", warning="throughput", label="nonexistent")
        command = PerfdataCommand(client, args)
        result = command.execute()

        assert result.status == STATE_OK
        # Should use index since label field doesn't exist
        assert "0.throughput" in result.perfdata
        assert "1.throughput" in result.perfdata
