# check_netscaler

Nagios/Icinga monitoring plugin for Citrix NetScaler (ADC) using the NITRO REST API.

## Version 2.0 - Python Rewrite

This is a complete Python rewrite of check_netscaler. **All 16 check commands are implemented** with 336 passing tests and full CI/CD integration.

> **Looking for the stable Perl version (v1.x)?**
> See the [master branch](../../tree/master) or tags < 2.0.0 for the legacy Perl implementation.

## Features

Monitor your NetScaler without SNMP:

- **Virtual Servers** - Load balancer, VPN, GSLB, Content Switching, AAA
- **Services & Service Groups** - State and member quorum monitoring
- **SSL Certificates** - Expiration warnings
- **High Availability** - HA status and sync monitoring
- **System Resources** - CPU, memory, disk usage thresholds
- **Network Interfaces** - Interface status and statistics
- **License Management** - License expiration tracking
- **NTP Synchronization** - Time sync validation
- **Configuration** - Unsaved config detection
- **Performance Data** - Generic metric collection for any NITRO object

### Advanced Features

- Regex-based filtering (`--filter` / `--limit`)
- Custom performance data labels
- Flexible threshold formats
- Multiple Python versions supported (3.8-3.12)

## Requirements

```
Python >= 3.8
requests >= 2.31.0
```

## Installation

```bash
git clone https://github.com/slauger/check_netscaler.git
cd check_netscaler
git checkout v2-python-rewrite

# Install
pip install -e .

# For development
pip install -e ".[dev]"
```

## Quick Start

```bash
# Check all load balancer vServers
check_netscaler -H 192.168.1.10 -s -u nsroot -p nsroot -C state -o lbvserver

# Check SSL certificate expiration
check_netscaler -H 192.168.1.10 -s -C sslcert -w 60 -c 30

# Check CPU usage
check_netscaler -H 192.168.1.10 -s -C above -o system -n cpuusagepcnt -w 75 -c 90

# Check HA status
check_netscaler -H 192.168.1.10 -s -C hastatus

# Check NTP sync
check_netscaler -H 192.168.1.10 -s -C ntp -w "o=0.03" -c "o=0.05"
```

## Available Commands

| Command | Description |
|---------|-------------|
| `state` | vServer/service/servicegroup/server state monitoring |
| `above`/`below` | Threshold-based checks (CPU, memory, disk, etc.) |
| `sslcert` | SSL certificate expiration |
| `hastatus` | High availability status |
| `interfaces` | Network interface monitoring |
| `servicegroup` | Service group member quorum |
| `perfdata` | Generic performance data collection |
| `license` | License expiration |
| `ntp` | NTP synchronization status |
| `nsconfig` | Unsaved configuration detection |
| `matches`/`matches_not` | String matching in API responses |
| `staserver` | STA server availability |
| `hwinfo` | Hardware information |
| `debug` | Raw API output for troubleshooting |

## Documentation

- **[Command Examples](examples/commands/)** - Detailed usage for every command
- **[Icinga 2 Integration](examples/icinga2/)** - CheckCommand definitions
- **[Nagios Integration](examples/nagios/)** - Command and service configurations

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# With coverage
pytest tests/ --cov=check_netscaler --cov-report=html

# Linting
ruff check check_netscaler/ tests/

# Formatting
black check_netscaler/ tests/
```

### CI/CD

GitHub Actions pipeline runs automatically on every push:
- Matrix testing on Python 3.8, 3.9, 3.10, 3.11, 3.12
- Linting with ruff
- Code formatting with black
- Type checking with mypy
- Full test suite (336 tests)

## License

MIT License - See [LICENSE](LICENSE)

## Contributors

- [slauger](https://github.com/slauger) - Original author
- [macampo](https://github.com/macampo)
- [Velociraptor85](https://github.com/Velociraptor85)
- [bb-ricardo](https://github.com/bb-ricardo)
- [DerInti](https://github.com/DerInti)

## Links

- [Issue Tracker](https://github.com/slauger/check_netscaler/issues)
- [Pull Requests](https://github.com/slauger/check_netscaler/pulls)
- [NetScaler NITRO API Documentation](http://docs.citrix.com/en-us/netscaler/)
