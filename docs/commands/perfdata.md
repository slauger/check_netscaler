# perfdata - Generic Performance Data Collection


> **Note**: All examples assume environment variables are set:
> ```bash
> export NETSCALER_HOST=192.168.1.10
> export NETSCALER_USER=nsroot
> export NETSCALER_PASS=nsroot
> ```
> See [Environment Variables](../../README.md#using-environment-variables-recommended) for details.

Collect arbitrary performance data from any NetScaler object type.

## Basic Usage

### Collect specific metrics from all objects

```bash
check_netscaler -C perfdata -o lbvserver -n totalhits,totalrequests
```

**Output:**
```
OK: perfdata: collected 4 metrics from lbvserver | '0.totalhits'=12345.0 '0.totalrequests'=67890.0 '1.totalhits'=23456.0 '1.totalrequests'=89012.0
```

### Collect metrics with custom labels

```bash
check_netscaler -C perfdata -o lbvserver -n totalhits,totalrequests --label name
```

**Output:**
```
OK: perfdata: collected 4 metrics from lbvserver | 'web_lb.totalhits'=12345.0 'web_lb.totalrequests'=67890.0 'api_lb.totalhits'=23456.0 'api_lb.totalrequests'=89012.0
```

## Advanced Usage

### Custom separator

```bash
check_netscaler -C perfdata -o lbvserver -n totalhits --label name --separator "_"
```

**Output:**
```
OK: perfdata collected | web_lb_totalhits=12345 api_lb_totalhits=23456
```

### Filter and limit objects

Filter out specific objects (exclude matching):
```bash
# Exclude test servers
check_netscaler -C perfdata -o lbvserver -n totalhits --label name --filter "test"
```

Limit to specific objects (include only matching):
```bash
# Only production servers
check_netscaler -C perfdata -o lbvserver -n totalhits --label name --limit "prod"
```

Combine filter and limit:
```bash
# Only production servers, exclude API servers
check_netscaler -C perfdata -o lbvserver -n totalhits --label name --limit "prod" --filter "api"
```

### Multiple fields from system stats

```bash
check_netscaler -C perfdata -o system -n cpuusagepcnt,memusagepcnt,disk0perusage
```

### Using different API endpoints

```bash
# Using stat endpoint (default, for performance counters)
check_netscaler -C perfdata -o lbvserver -n totalhits -e stat

# Using config endpoint (for configuration data)
check_netscaler -C perfdata -o lbvserver -n ipv46 -e config
```

## Common Use Cases

### 1. Load balancer metrics

```bash
check_netscaler -C perfdata -o lbvserver \
  -n totalhits,totalrequests,requestsrate --label name
```

### 2. Service statistics

```bash
check_netscaler -C perfdata -o service \
  -n totalrequests,requestsrate,avgttfb --label name
```

### 3. System metrics

```bash
check_netscaler -C perfdata -o system \
  -n tcpcurestablishedconn,tcpcurserverconn,tcpcurclientconn
```

### 4. SSL/TLS statistics

```bash
check_netscaler -C perfdata -o ssl \
  -n ssltotsessions,ssltothwsessions,ssltotswsessions
```

### 5. Cache statistics

```bash
check_netscaler -C perfdata -o cache \
  -n cachenumobjinmemory,cachebytesserved,cacherecentpercen
```

## Performance Data Format

Without label (uses numeric index):
```
| '0.metric1'=value '0.metric2'=value '1.metric1'=value '1.metric2'=value
```

With label (e.g., `--label name`):
```
| 'objectname.metric1'=value 'objectname.metric2'=value
```

With custom separator (e.g., `--separator "_"`):
```
| 'objectname_metric1'=value 'objectname_metric2'=value
```

## Label Options

- **No label**: Uses array index (`0.metric`, `1.metric`)
- **--label name**: Uses object's `name` field
- **--label <field>**: Uses any object field as label
- **--separator <char>**: Changes separator (default: `.`)

## Object Types

Common object types for perfdata:
- `system` - System-wide metrics
- `lbvserver` - Load balancer vServers
- `service` - Services
- `servicegroup` - Service groups
- `ssl` - SSL/TLS statistics
- `cache` - Cache statistics
- `aaa` - AAA statistics
- `gslb` - GSLB statistics

## Important Notes

- **Field Names**: Use `-n` with comma-separated field names (e.g., `-n field1,field2,field3`)
- **All Objects**: This command queries ALL objects of the specified type and collects the specified fields from each
- **Filtering**: Use `--filter` to exclude objects or `--limit` to include only specific objects (regex-based)

## Tips

- Use `-e stat` for performance counters (default)
- Use `-e config` for configuration values
- Use `--label` to make perfdata more readable (e.g., `--label name` uses object names instead of indices)
- Use `--separator` to customize the label separator (default is `.`)
- Use `--filter` to exclude objects matching a regex pattern
- Use `--limit` to include only objects matching a regex pattern
- This command always returns OK status (for data collection only)
- Combine with `above`/`below` commands for threshold-based alerting
- Query the NITRO API documentation for available field names
