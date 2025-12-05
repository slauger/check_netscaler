# Icinga 2 Integration

CheckCommand definitions and service examples for check_netscaler in Icinga 2.

## Installation

1. Install check_netscaler on your Icinga 2 server or satellite:

```bash
cd /opt
git clone https://github.com/slauger/check_netscaler.git
cd check_netscaler
git checkout v2-python-rewrite
pip3 install -e .
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

  vars.netscaler_ssl = true
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

  assign where host.vars.netscaler_ssl
}
```

## Command Variables

All CheckCommands support these common variables:

- `vars.netscaler_hostname` - NetScaler hostname/IP (default: `host.address`)
- `vars.netscaler_username` - Username (default: `nsroot`)
- `vars.netscaler_password` - Password (default: `nsroot`)
- `vars.netscaler_ssl` - Use HTTPS (default: `true`)
- `vars.netscaler_port` - TCP port (default: auto)
- `vars.netscaler_timeout` - Timeout in seconds (default: `10`)

## Available CheckCommands

| CheckCommand | Description |
|--------------|-------------|
| `netscaler_state` | Monitor object states |
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
