# check_netscaler v2.0 (Python Rewrite)

> **Work in Progress - Complete Rewrite**
>
> This branch contains a complete rewrite of check_netscaler in Python.
> This is **not production-ready** and under active development.
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

### Core Infrastructure
- [ ] Python project setup (pyproject.toml, dependencies)
- [ ] NITRO API client implementation
- [ ] Mock testing framework
- [ ] CLI argument parser
- [ ] Plugin output formatting (Nagios/Icinga compatible)

### Check Commands
- [ ] `state` - Check vServer/service/servicegroup/server states
- [ ] `sslcert` - SSL certificate expiration
- [ ] `above/below` - Threshold checks
- [ ] `matches/matches_not` - String matching
- [ ] `nsconfig` - Unsaved configuration changes
- [ ] `hastatus` - High availability status
- [ ] `servicegroup` - ServiceGroup with quorum checks
- [ ] `hwinfo` - Hardware information
- [ ] `interfaces` - Network interface status
- [ ] `perfdata` - Performance data collection
- [ ] `license` - License expiration
- [ ] `staserver` - STA server availability
- [ ] `ntp` - NTP synchronization status
- [ ] `debug` - Debug output

### Testing & CI/CD
- [ ] Unit tests with pytest
- [ ] Mock NITRO API responses
- [ ] Integration tests
- [ ] GitHub Actions CI/CD pipeline
- [ ] Code coverage reporting

### Documentation
- [ ] API client documentation
- [ ] Usage examples
- [ ] Migration guide from v1.x
- [ ] Contributing guidelines

## Requirements

```
Python >= 3.8
requests
pytest (for testing)
pytest-mock (for testing)
```

## Installation (Future)

```bash
# Via pip (not yet available)
pip install check_netscaler

# Or from source
git clone https://github.com/slauger/check_netscaler.git
cd check_netscaler
git checkout v2-python-rewrite
pip install -e .
```

## Planned Usage

```bash
# Check load balancer vServer state
check_netscaler --hostname 192.168.1.10 --ssl --command state --objecttype lbvserver

# Check SSL certificates expiring in 30 days
check_netscaler -H 192.168.1.10 -s -C sslcert -w 30 -c 10

# Check system CPU usage
check_netscaler -H 192.168.1.10 -s -C above -o system -n cpuusagepcnt -w 75 -c 80
```

## Architecture (Planned)

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
