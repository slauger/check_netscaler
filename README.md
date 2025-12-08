# check_netscaler

[![CI](https://github.com/slauger/check_netscaler/actions/workflows/lint-and-type-check.yml/badge.svg?branch=master)](https://github.com/slauger/check_netscaler/actions/workflows/lint-and-type-check.yml)
[![PyPI](https://img.shields.io/pypi/v/check_netscaler)](https://pypi.org/project/check_netscaler/)
[![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Nagios/Icinga monitoring plugin for Citrix NetScaler (ADC) using the NITRO REST API.

## Version 2.0 - Python Rewrite

This is a complete Python rewrite of check_netscaler. **All 16 check commands are implemented** with 343 passing tests and full CI/CD integration.

> **Looking for the stable Perl version (v1.x)?**
> See tags < 2.0.0 for the legacy Perl implementation.

### Breaking Changes from v1.x

- **HTTPS is now default** - Use `--no-ssl` for HTTP instead of `-s` for HTTPS
- Environment variable support added: `NETSCALER_HOST`, `NETSCALER_USER`, `NETSCALER_PASS`

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
check_netscaler -H 192.168.1.10 -u nsroot -p nsroot -C state -o lbvserver

# Check SSL certificate expiration
check_netscaler -H 192.168.1.10 -C sslcert -w 60 -c 30

# Check CPU usage
check_netscaler -H 192.168.1.10 -C above -o system -n cpuusagepcnt -w 75 -c 90

# Check HA status
check_netscaler -H 192.168.1.10 -C hastatus

# Check NTP sync
check_netscaler -H 192.168.1.10 -C ntp -w "o=0.03" -c "o=0.05"
```

### Using Environment Variables (Recommended)

For improved security and convenience, use environment variables instead of command-line arguments:

```bash
# Export credentials once
export NETSCALER_HOST=192.168.1.10
export NETSCALER_USER=monitoring
export NETSCALER_PASS=SecurePassword123

# Now run checks without passing credentials
check_netscaler -C state -o lbvserver
check_netscaler -C sslcert -w 60 -c 30
check_netscaler -C hastatus
```

**Why use environment variables?**

- **Security**: Credentials are not visible in process listings (`ps`, `top`, `/proc`)
- **Convenience**: Set once, use in multiple commands
- **Best Practice**: Follows patterns from other monitoring plugins (PostgreSQL, MySQL)
- **Integration**: Works seamlessly with Icinga 2 `env` attribute, Nagios/systemd environments

Command-line arguments always override environment variables if both are provided.

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
- Full test suite (343 tests)

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
