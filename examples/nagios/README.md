# Nagios Integration

Command and service definitions for check_netscaler in Nagios.

## Installation

1. Install check_netscaler on your Nagios server:

```bash
# From PyPI (recommended)
pip3 install check_netscaler

# Or from source
git clone https://github.com/slauger/check_netscaler.git
cd check_netscaler
pip3 install .
```

2. Copy configurations to Nagios:

```bash
cp commands.cfg /usr/local/nagios/etc/objects/
cp services.cfg.example /usr/local/nagios/etc/objects/netscaler-services.cfg
cp hosts.cfg.example /usr/local/nagios/etc/objects/netscaler-hosts.cfg
```

3. Add to nagios.cfg:

```
cfg_file=/usr/local/nagios/etc/objects/commands.cfg
cfg_file=/usr/local/nagios/etc/objects/netscaler-services.cfg
cfg_file=/usr/local/nagios/etc/objects/netscaler-hosts.cfg
```

4. Validate and reload:

```bash
/usr/local/nagios/bin/nagios -v /usr/local/nagios/etc/nagios.cfg
systemctl reload nagios
```

## Files

- `commands.cfg` - Command definitions for all checks
- `services.cfg.example` - Service definition examples
- `hosts.cfg.example` - Host definition example

## Quick Example

### Define a command

```
define command {
    command_name    check_netscaler_state
    command_line    check_netscaler -H $HOSTADDRESS$ -u $ARG1$ -p $ARG2$ -C state -o $ARG3$
}
```

### Define a host

```
define host {
    use                     generic-host
    host_name               netscaler01
    alias                   NetScaler Production 01
    address                 192.168.1.10
    _netscaler_user         nsroot
    _netscaler_pass         nsroot
}
```

### Define a service

```
define service {
    use                     generic-service
    host_name               netscaler01
    service_description     LB vServers
    check_command           check_netscaler_state!$_HOSTNETSCALER_USER$!$_HOSTNETSCALER_PASS$!lbvserver
}
```

## Custom Variables

Store credentials in host custom variables:

- `_netscaler_user` - NetScaler username
- `_netscaler_pass` - NetScaler password
- `_netscaler_ssl` - Use SSL (yes/no)

## Tips

- Store credentials in resource.cfg for better security
- Use host templates for common NetScaler configurations
- Group NetScaler hosts with hostgroups
- Use servicegroups for related checks
- Set appropriate check intervals for each metric type
- Consider using a dedicated monitoring user with read-only permissions
