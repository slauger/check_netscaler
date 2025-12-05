# check_netscaler v2.0 (Python Rewrite)

> **Nearly Complete - 93% Implemented!** 🎉
>
> This branch contains a complete rewrite of check_netscaler in Python.
> **14 out of 15 commands are fully implemented with 336 passing tests and CI/CD pipeline.**
>
> **Looking for the stable Perl version?** See the [master branch](../../tree/master).

## Why v2.0?

This is a ground-up rewrite with the following goals:

- **Modern Language**: Python 3.8+ instead of Perl for better maintainability and wider adoption
- **Mock-based Testing**: NetScaler CPX container image is no longer publicly available, requiring a new testing approach with comprehensive mock services
- **Improved Architecture**: Cleaner code structure, better error handling, type hints
- **Enhanced Features**: Building on the solid foundation of v1.x with new capabilities

## Original Project

check_netscaler is a Nagios/Icinga monitoring plugin for Citrix NetScaler Application Delivery Controllers. It uses the NITRO REST API (no SNMP required) to monitor:

- Virtual Servers (LB, VPN, GSLB, AAA, CS)
- Services and Service Groups
- SSL Certificates
- High Availability Status
- System Resources (CPU, Memory, Disk)
- Network Interfaces
- Configuration Changes
- License Expiration
- NTP Synchronization
- And much more...

## Development Status

**Progress: 14/15 commands (93%) - 336 tests passing ✅**

### Core Infrastructure ✅ COMPLETE
- [x] Python project setup (pyproject.toml, dependencies)
- [x] NITRO API client implementation
- [x] Mock testing framework (pytest-based)
- [x] CLI argument parser (argparse)
- [x] Plugin output formatting (Nagios/Icinga compatible)

### Check Commands (14/15 implemented)
- [x] `state` - Check vServer/service/servicegroup/server states
- [x] `sslcert` - SSL certificate expiration
- [x] `above/below` - Threshold checks
- [x] `matches/matches_not` - String matching
- [x] `nsconfig` - Unsaved configuration changes
- [x] `hastatus` - High availability status
- [x] `servicegroup` - ServiceGroup with quorum checks
- [x] `hwinfo` - Hardware information
- [x] `interfaces` - Network interface status
- [x] `perfdata` - Performance data collection
- [x] `license` - License expiration
- [x] `staserver` - STA server availability
- [x] `ntp` - NTP synchronization status
- [x] `debug` - Debug output

### Advanced Features ✅ COMPLETE
- [x] Filter/Limit support (regex-based filtering)
- [x] Label support (custom perfdata labels)
- [x] Separator customization (perfdata formatting)

### Testing & CI/CD ✅ COMPLETE
- [x] 336 unit tests with pytest
- [x] Mock NITRO API responses
- [x] GitHub Actions CI/CD pipeline
- [x] Linting with ruff
- [x] Code formatting with black
- [x] Type checking with mypy
- [ ] Integration tests
- [ ] Code coverage reporting

### Documentation 🚧 IN PROGRESS
- [ ] API client documentation
- [ ] Usage examples for all commands
- [ ] Migration guide from v1.x
- [ ] Contributing guidelines

## Requirements

```
Python >= 3.8
requests >= 2.31.0
```

**Development dependencies:**
```
pytest >= 7.4.0
pytest-cov >= 4.1.0
pytest-mock >= 3.11.0
black >= 23.7.0
ruff >= 0.0.285
mypy >= 1.5.0
```

## Installation

```bash
# Clone repository
git clone https://github.com/slauger/check_netscaler.git
cd check_netscaler
git checkout v2-python-rewrite

# Install dependencies
pip install -e .

# For development
pip install -e ".[dev]"
```

## Usage

```bash
# Check load balancer vServer state
check_netscaler --hostname 192.168.1.10 --ssl --command state --objecttype lbvserver

# Check SSL certificates expiring in 30 days
check_netscaler -H 192.168.1.10 -s -C sslcert -w 30 -c 10

# Check system CPU usage
check_netscaler -H 192.168.1.10 -s -C above -o system -n cpuusagepcnt -w 75 -c 90

# Check HA status
check_netscaler -H 192.168.1.10 -s -C hastatus

# Check NTP synchronization
check_netscaler -H 192.168.1.10 -s -C ntp -w "o=0.03,s=2,j=100,t=3" -c "o=0.05,s=3,j=200,t=2"

# Check interface status with filter
check_netscaler -H 192.168.1.10 -s -C interfaces --filter "^(1/1|10/1)"

# Generic perfdata collection
check_netscaler -H 192.168.1.10 -s -C perfdata -o lbvserver -n totalhits,totalrequests --label name
```

## Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=check_netscaler --cov-report=html

# Run linting
ruff check check_netscaler/ tests/

# Format code
black check_netscaler/ tests/
```

## Architecture

```
check_netscaler/
├── __init__.py
├── __main__.py           # CLI entry point
├── client/
│   ├── __init__.py
│   ├── nitro.py          # NITRO API client
│   └── session.py        # Session management
├── commands/
│   ├── __init__.py
│   ├── base.py           # Base command class
│   ├── state.py          # State checks
│   ├── sslcert.py        # SSL certificate checks
│   ├── threshold.py      # Above/below checks
│   └── ...               # Other check commands
├── output/
│   ├── __init__.py
│   └── nagios.py         # Nagios plugin output formatter
└── utils/
    ├── __init__.py
    └── helpers.py        # Utility functions

tests/
├── __init__.py
├── conftest.py           # pytest fixtures
├── mocks/
│   └── responses.json    # Mock NITRO API responses
├── test_client.py
├── test_commands.py
└── ...
```

## Contributing

This is a work in progress. Contributions are welcome! Please:

1. Check existing issues or create a new one to discuss your idea
2. Fork the repository and create a feature branch
3. Write tests for your changes
4. Submit a pull request against the `v2-python-rewrite` branch

## Original Authors & Contributors

- [slauger](https://github.com/slauger) - Original author
- [macampo](https://github.com/macampo)
- [Velociraptor85](https://github.com/Velociraptor85)
- [bb-ricardo](https://github.com/bb-ricardo)
- [DerInti](https://github.com/DerInti)

## License

MIT License - See [LICENSE](LICENSE)

## Related Projects

- [check_netscaler_gateway](https://github.com/slauger/check_netscaler_gateway) - NetScaler Gateway and Storefront testing

## NITRO API Documentation

Full NITRO API documentation is available on your NetScaler appliance:
`http://NSIP/nitro-rest.tgz`

---

**Note**: This v2.0 rewrite is being developed to ensure the long-term viability of this monitoring plugin with modern tooling and testing approaches.
