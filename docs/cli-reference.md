# CLI Reference

Complete reference for all command-line options of check_netscaler.

## Synopsis

```bash
check_netscaler [OPTIONS] -C COMMAND [COMMAND_OPTIONS]
```

## Global Options

### Connection Options

#### `-H HOSTNAME`, `--hostname HOSTNAME`
Hostname or IP address of the NetScaler appliance.

**Environment Variable:** `NETSCALER_HOST`

**Example:**
```bash
check_netscaler -H 192.168.1.10 -C hastatus
# Or using environment variable:
export NETSCALER_HOST=192.168.1.10
check_netscaler -C hastatus
```

#### `-u USERNAME`, `--username USERNAME`
Username for NITRO API authentication.

**Environment Variable:** `NETSCALER_USER`
**Default:** `nsroot`

**Example:**
```bash
check_netscaler -H 192.168.1.10 -u monitoring -C state -o lbvserver
```

#### `-p PASSWORD`, `--password PASSWORD`
Password for NITRO API authentication.

**Environment Variable:** `NETSCALER_PASS`
**Default:** `nsroot`

**Security Note:** Using environment variables is recommended to avoid exposing credentials in process listings.

**Example:**
```bash
export NETSCALER_PASS=SecurePassword123
check_netscaler -H 192.168.1.10 -u monitoring -C state -o lbvserver
```

#### `--no-ssl`
Use HTTP instead of HTTPS for NITRO API connection.

**Default:** HTTPS is used

**Example:**
```bash
check_netscaler -H 192.168.1.10 --no-ssl -C state -o lbvserver
```

**Note:** This is the inverse of the v1.x `-s` flag. In v2.0, HTTPS is default.

#### `-P PORT`, `--port PORT`
TCP port to connect to for NITRO API.

**Default:**
- `443` when using HTTPS (default)
- `80` when using `--no-ssl`

**Example:**
```bash
check_netscaler -H 192.168.1.10 -P 8443 -C state -o lbvserver
```

#### `-a API`, `--api API`
NITRO API version to use.

**Default:** `v1`

**Example:**
```bash
check_netscaler -H 192.168.1.10 -a v2 -C state -o lbvserver
```

**Note:** Most NetScaler versions use API v1. Only change if you have specific requirements.

#### `-t TIMEOUT`, `--timeout TIMEOUT`
Connection timeout in seconds for NITRO API requests.

**Default:** `15`

**Example:**
```bash
check_netscaler -H 192.168.1.10 -t 30 -C state -o lbvserver
```

**Use Cases:**
- Slow network connections
- Large NetScaler configurations
- Overloaded NetScaler systems

### Command Selection

#### `-C COMMAND`, `--command COMMAND`
**Required.** Specifies which check command to execute.

**Available Commands:**
- `state` - Object state monitoring
- `above` / `below` - Threshold checks
- `sslcert` - SSL certificate expiration
- `hastatus` - High Availability status
- `interfaces` - Network interfaces
- `servicegroup` - Service group quorum
- `perfdata` - Performance data collection
- `license` - License expiration
- `ntp` - NTP synchronization
- `nsconfig` - Unsaved configuration
- `matches` / `matches_not` - String matching
- `staserver` - STA server availability
- `hwinfo` - Hardware information
- `debug` - Raw API output

**Example:**
```bash
check_netscaler -H 192.168.1.10 -C state -o lbvserver
```

See [Command Documentation](commands/) for detailed usage of each command.

## Command-Specific Options

### Object Selection

#### `-o OBJECTTYPE`, `--objecttype OBJECTTYPE`
NITRO API object type to query.

**Common Object Types:**
- `lbvserver` - Load Balancing Virtual Servers
- `service` - Services
- `servicegroup` - Service Groups
- `server` - Servers
- `vpnvserver` - VPN Virtual Servers
- `gslbvserver` - GSLB Virtual Servers
- `csvserver` - Content Switching Virtual Servers
- `system` - System metrics
- `sslcertkey` - SSL Certificates
- `interface` - Network Interfaces

**Example:**
```bash
check_netscaler -C state -o lbvserver
check_netscaler -C above -o system -n cpuusagepcnt -w 75 -c 90
```

#### `-n OBJECTNAME`, `--objectname OBJECTNAME`
Filter by specific object name or field name(s).

**Usage varies by command:**
- **state/above/below:** Specific object name
- **perfdata:** Comma-separated field names
- **matches:** Field name to check

**Examples:**
```bash
# Check specific vServer
check_netscaler -C state -o lbvserver -n web_lb

# Check multiple metrics
check_netscaler -C perfdata -o lbvserver -n totalhits,totalrequests,requestsrate --label name

# Check specific field value
check_netscaler -C matches -o hanode -n hacurstate -w UP -c DOWN
```

#### `-e ENDPOINT`, `--endpoint ENDPOINT`
NITRO API endpoint type to use.

**Options:** `stat` | `config`

**Default:** Automatically selected based on command:
- Most commands use `stat` (statistics endpoint)
- Some commands use `config` (configuration endpoint)

**Example:**
```bash
check_netscaler -C debug -o lbvserver -e config
```

**When to use:**
- Debugging API responses
- Accessing config-only attributes
- Troubleshooting missing data

### Thresholds

#### `-w WARNING`, `--warning WARNING`
Warning threshold for the check.

**Format varies by command:**
- **Numeric:** Simple number (`75`)
- **Complex:** Key-value pairs (`o=0.03,s=2,j=100`)

**Examples:**
```bash
# Simple numeric threshold
check_netscaler -C above -o system -n cpuusagepcnt -w 75 -c 90

# SSL certificate days
check_netscaler -C sslcert -w 60 -c 30

# NTP with multiple thresholds
check_netscaler -C ntp -w "o=0.03,s=2,j=100,t=3" -c "o=0.05,s=3,j=200,t=2"

# ServiceGroup quorum percentage
check_netscaler -C servicegroup -n web_sg -w 50 -c 25
```

#### `-c CRITICAL`, `--critical CRITICAL`
Critical threshold for the check.

**Format:** Same as `-w/--warning`

**Logic:**
- **above:** Alert if value is above threshold
- **below:** Alert if value is below threshold
- **sslcert/license:** Alert if days remaining below threshold
- **servicegroup:** Alert if available percentage below threshold

**Example:**
```bash
check_netscaler -C below -o system -n memusagepcnt -w 10 -c 5
```

### Filtering

#### `-f FILTER`, `--filter FILTER`
Regular expression to **exclude** objects from monitoring.

**Use Case:** Filter out test/dev environments

**Examples:**
```bash
# Exclude all vServers starting with "test_"
check_netscaler -C state -o lbvserver --filter "^test_"

# Exclude interfaces 0/1 and 0/2
check_netscaler -C interfaces --filter "^0/[12]$"

# Exclude SSL certificates with "internal" in name
check_netscaler -C sslcert --filter "internal"
```

#### `-l LIMIT`, `--limit LIMIT`
Regular expression to **include only** matching objects.

**Use Case:** Monitor only production systems

**Examples:**
```bash
# Only check production vServers
check_netscaler -C state -o lbvserver --limit "^prod_"

# Only check 10G interfaces
check_netscaler -C interfaces --limit "^10/"

# Only check services in specific cluster
check_netscaler -C state -o service --limit "^cluster[12]_"
```

**Note:** `--filter` and `--limit` can be combined:
```bash
# Check prod vServers but exclude test subdomains
check_netscaler -C state -o lbvserver --limit "^prod_" --filter "test\."
```

### Output Customization

#### `-L LABEL`, `--label LABEL`
Field name to use as label in performance data output.

**Use Case:** Make perfdata more readable by using object names instead of indices

**Examples:**
```bash
# Use vServer name as perfdata label
check_netscaler -C perfdata -o lbvserver -n totalhits,totalrequests --label name

# Use service name
check_netscaler -C perfdata -o service -n throughput --label name
```

**Output without --label:**
```
OK | 0.totalhits=1234 0.totalrequests=5678
```

**Output with --label name:**
```
OK | web_lb.totalhits=1234 web_lb.totalrequests=5678
```

#### `--separator SEPARATOR`
Character to use as separator in performance data labels.

**Default:** `.` (dot)

**Use Case:** Some monitoring systems don't handle dots well in metric names

**Examples:**
```bash
# Use underscore instead of dot
check_netscaler -C interfaces --separator "_"

# Use dash
check_netscaler -C perfdata -o lbvserver -n totalhits --label name --separator "-"
```

**Output with default separator:**
```
OK | web_lb.totalhits=1234
```

**Output with --separator "_":**
```
OK | web_lb_totalhits=1234
```

### Special Options

#### `--check-backup {warning|critical}`
Check if backup vServer is active and alert with specified severity.

**Only for:** `state` command with `lbvserver` objects

**Use Case:** Detect failover scenarios where backup load balancer has taken over

**Examples:**
```bash
# Alert as WARNING when backup is active
check_netscaler -C state -o lbvserver -n web_lb --check-backup warning

# Alert as CRITICAL when backup is active
check_netscaler -C state -o lbvserver -n api_lb --check-backup critical
```

**Output when backup is active:**
```
WARNING: lbvserver is UP; Backup vServer active: web_lb_backup
```

See [docs/commands/state.md](commands/state.md#backup-vserver-monitoring) for details.

#### `-x URLOPTS`, `--urlopts URLOPTS`
Additional URL options to append to NITRO API requests.

**Use Case:** Advanced NITRO API features like filtering, pagination, or bulk operations

**Example:**
```bash
check_netscaler -C debug -o lbvserver -x "?filter=name:web_"
```

**Warning:** This is an advanced option. Incorrect usage may break API requests.

#### `-v`, `--verbose`
Increase output verbosity for debugging.

**Can be repeated:** `-vv`, `-vvv` for more verbosity

**Use Case:** Troubleshooting plugin behavior or API communication issues

**Example:**
```bash
check_netscaler -v -C state -o lbvserver
check_netscaler -vv -C debug -o system
```

### Information Options

#### `-h`, `--help`
Show help message and exit.

**Example:**
```bash
check_netscaler --help
```

#### `-V`, `--version`
Show program version number and exit.

**Example:**
```bash
check_netscaler --version
```

## Environment Variables

check_netscaler supports environment variables for credentials and connection settings. This is the **recommended** method for security reasons.

| Environment Variable | CLI Equivalent | Description |
|---------------------|----------------|-------------|
| `NETSCALER_HOST` | `-H/--hostname` | NetScaler hostname or IP |
| `NETSCALER_USER` | `-u/--username` | NITRO API username |
| `NETSCALER_PASS` | `-p/--password` | NITRO API password |

**Priority:** Command-line arguments always override environment variables.

**Example Setup:**
```bash
# Add to ~/.bashrc or monitoring system environment
export NETSCALER_HOST=192.168.1.10
export NETSCALER_USER=monitoring
export NETSCALER_PASS=SecurePassword123

# Now run checks without exposing credentials
check_netscaler -C state -o lbvserver
check_netscaler -C sslcert -w 60 -c 30
```

**Integration Examples:**
- [Icinga 2 Integration](../examples/icinga2/)
- [Nagios Integration](../examples/nagios/)

## Exit Codes

check_netscaler follows standard Nagios/Icinga plugin exit codes:

| Code | Status | Description |
|------|--------|-------------|
| 0 | OK | Check passed successfully |
| 1 | WARNING | Warning threshold exceeded |
| 2 | CRITICAL | Critical threshold exceeded or object down |
| 3 | UNKNOWN | Invalid arguments, API error, or cannot determine state |

## Examples by Use Case

### Basic Monitoring

```bash
# Check all load balancers
check_netscaler -H 192.168.1.10 -u nsroot -p nsroot -C state -o lbvserver

# Check SSL certificates (warn at 60 days, critical at 30 days)
check_netscaler -H 192.168.1.10 -C sslcert -w 60 -c 30

# Check CPU usage (warn at 75%, critical at 90%)
check_netscaler -H 192.168.1.10 -C above -o system -n cpuusagepcnt -w 75 -c 90

# Check HA status
check_netscaler -H 192.168.1.10 -C hastatus
```

### Using Environment Variables

```bash
export NETSCALER_HOST=192.168.1.10
export NETSCALER_USER=monitoring
export NETSCALER_PASS=SecurePassword123

check_netscaler -C state -o lbvserver
check_netscaler -C sslcert -w 60 -c 30
check_netscaler -C hastatus
```

### Advanced Filtering

```bash
# Only monitor production vServers
check_netscaler -C state -o lbvserver --limit "^prod_"

# Monitor all except test environments
check_netscaler -C state -o service --filter "^test_"

# Check only 10G interfaces
check_netscaler -C interfaces --limit "^10/"
```

### Performance Data Collection

```bash
# Collect vServer metrics with readable labels
check_netscaler -C perfdata -o lbvserver \
  -n totalhits,totalrequests,requestsrate \
  --label name

# System metrics
check_netscaler -C perfdata -o system \
  -n cpuusagepcnt,memusagepcnt,disk0perusage \
  --label hostname
```

### Service Group Quorum

```bash
# Warn if less than 50% members available, critical below 25%
check_netscaler -C servicegroup -n web_sg -w 50 -c 25
```

### NTP Synchronization

```bash
# Complex thresholds: offset, stratum, jitter, truechimers
check_netscaler -C ntp \
  -w "o=0.03,s=2,j=100,t=3" \
  -c "o=0.05,s=3,j=200,t=2"
```

### Backup vServer Monitoring

```bash
# Alert when backup vServer becomes active
check_netscaler -C state -o lbvserver -n web_lb --check-backup critical
```

## See Also

- [Command Documentation](commands/) - Detailed guide for each command
- [Icinga 2 Integration](../examples/icinga2/)
- [Nagios Integration](../examples/nagios/)
- [NetScaler NITRO API Documentation](http://docs.citrix.com/en-us/netscaler/)
