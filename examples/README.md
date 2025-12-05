# check_netscaler Examples

This directory contains usage examples and configuration templates for check_netscaler v2.0.

## Directory Structure

```
examples/
├── commands/          # Command-line usage examples for all check commands
├── icinga2/          # Icinga 2 CheckCommand definitions and service examples
├── nagios/           # Nagios command and service definitions
└── README.md         # This file
```

## Quick Start

### Basic Usage

All commands follow this general pattern:

```bash
check_netscaler -H <hostname> -u <username> -p <password> -C <command> [options]
```

**Common Options:**
- `-H, --hostname` - NetScaler hostname or IP (env: `NETSCALER_HOST`)
- `-u, --username` - Username (env: `NETSCALER_USER`, default: nsroot)
- `-p, --password` - Password (env: `NETSCALER_PASS`, default: nsroot)
- `--no-ssl` - Use HTTP instead of HTTPS (HTTPS is default)
- `-C, --command` - Check command to execute
- `-w, --warning` - Warning threshold
- `-c, --critical` - Critical threshold

**Environment Variables:**
```bash
export NETSCALER_HOST=192.168.1.10
export NETSCALER_USER=monitoring
export NETSCALER_PASS=SecurePassword123

# Now you can omit -H, -u, and -p from commands
check_netscaler -C state -o lbvserver
```

### Example Commands

See the `commands/` directory for detailed examples of each check command.

### Monitoring System Integration

- **Icinga 2**: See `icinga2/` directory for CheckCommand definitions
- **Nagios**: See `nagios/` directory for command and service definitions

## Command Categories

### State Monitoring
- `state` - vServer/service/servicegroup/server states
- `hastatus` - High Availability status
- `nsconfig` - Unsaved configuration detection

### Certificate & License
- `sslcert` - SSL certificate expiration
- `license` - License expiration

### Performance & Resources
- `above/below` - Threshold-based monitoring (CPU, memory, disk)
- `perfdata` - Generic performance data collection
- `servicegroup` - ServiceGroup member quorum

### Network
- `interfaces` - Network interface status
- `ntp` - NTP synchronization

### Advanced
- `matches/matches_not` - String matching in API responses
- `staserver` - STA server availability
- `hwinfo` - Hardware information
- `debug` - Raw API output for troubleshooting

## Documentation

For complete documentation, see the main [README.md](../README.md).
