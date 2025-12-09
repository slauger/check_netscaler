# Icinga 2 Integration

CheckCommand definitions and service examples for check_netscaler in Icinga 2.

## Installation

1. Install check_netscaler on your Icinga 2 server or satellite:

```bash
# From PyPI (recommended)
pip3 install check_netscaler

# Or from source
git clone https://github.com/slauger/check_netscaler.git
cd check_netscaler
pip3 install .
```

2. Copy CheckCommand definitions to your Icinga 2 configuration:

```bash
cp check_netscaler.conf /etc/icinga2/conf.d/commands/
icinga2 daemon -C  # Validate configuration
systemctl reload icinga2
```

## Files

- `check_netscaler.conf` - CheckCommand definitions for all commands
- `services.conf.example` - Service definition examples
- `host.conf.example` - Host definition example

## Quick Example

### Define a NetScaler host

```
object Host "netscaler01" {
  import "generic-host"
  address = "192.168.1.10"

  vars.netscaler = true
  vars.netscaler_username = "nsroot"
  vars.netscaler_password = "password"
}
```

### Define a service

```
apply Service "netscaler-lbvservers" {
  import "generic-service"
  check_command = "netscaler_state"

  vars.netscaler_objecttype = "lbvserver"

  assign where host.vars.netscaler
}
```

### Monitor backup vServer activation

```
apply Service "netscaler-web-lb-backup" {
  import "generic-service"
  check_command = "netscaler_state_backup"

  vars.netscaler_objectname = "web_lb"
  vars.netscaler_check_backup = "critical"

  assign where host.vars.netscaler
}
```

## Command Variables

All CheckCommands support these common variables:

- `vars.netscaler_hostname` - NetScaler hostname/IP (default: `host.address`)
- `vars.netscaler_username` - Username (default: `nsroot`)
- `vars.netscaler_password` - Password (default: `nsroot`)
- `vars.netscaler_no_ssl` - Use HTTP instead of HTTPS (default: HTTPS is used)
- `vars.netscaler_port` - TCP port (default: auto - 443 for HTTPS, 80 for HTTP)
- `vars.netscaler_timeout` - Timeout in seconds (default: `10`)

## Available CheckCommands

| CheckCommand | Description |
|--------------|-------------|
| `netscaler_state` | Monitor object states |
| `netscaler_state_backup` | Monitor backup vServer activation |
| `netscaler_above` | Threshold checks (high values) |
| `netscaler_below` | Threshold checks (low values) |
| `netscaler_sslcert` | SSL certificate expiration |
| `netscaler_hastatus` | HA status monitoring |
| `netscaler_interfaces` | Network interfaces |
| `netscaler_servicegroup` | ServiceGroup quorum |
| `netscaler_perfdata` | Performance data collection |
| `netscaler_license` | License expiration |
| `netscaler_ntp` | NTP synchronization |
| `netscaler_nsconfig` | Unsaved configuration |
| `netscaler_matches` | String matching (equals) |
| `netscaler_matches_not` | String matching (not equals) |
| `netscaler_staserver` | STA server availability |
| `netscaler_hwinfo` | Hardware information |
| `netscaler_debug` | Raw API output |

## Tips

- Store credentials in Icinga 2 constants or use credential stores
- Use host templates for common NetScaler variables
- Leverage Icinga 2's apply rules for auto-configuration
- Group related checks with service templates
- Use check intervals appropriate for each metric type
- Consider using API-only monitoring user with read-only permissions
