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

### Collect specific metrics

```bash
check_netscaler -C perfdata -o lbvserver -n totalhits,totalrequests
```

**Output:**
```
OK: perfdata collected | 0.totalhits=12345 0.totalrequests=67890 1.totalhits=23456 1.totalrequests=89012
```

### Single object with label

```bash
check_netscaler -C perfdata -o lbvserver -n totalhits,totalrequests --label name
```

**Output:**
```
OK: perfdata collected | web_lb.totalhits=12345 web_lb.totalrequests=67890 api_lb.totalhits=23456
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

### Multiple fields

```bash
check_netscaler -C perfdata -o system -n cpuusagepcnt,memusagepcnt,disk0perusage
```

### Specific API endpoint

```bash
# Using stat endpoint (default, for performance counters)
check_netscaler -C perfdata -o lbvserver -n totalhits --api stat

# Using config endpoint (for configuration data)
check_netscaler -C perfdata -o lbvserver -n ipv46 --api config
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

Without label:
```
| 0.metric1=value 0.metric2=value 1.metric1=value 1.metric2=value
```

With label:
```
| objectname.metric1=value objectname.metric2=value
```

With custom separator:
```
| objectname_metric1=value objectname_metric2=value
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

## Tips

- Use `--api stat` for performance counters (default)
- Use `--api config` for configuration values
- Use `--label` to make perfdata more readable
- Use `--separator` to avoid special characters in metric names
- This command is for collecting data only (always returns OK)
- Combine with threshold checks using `above`/`below` for alerting
- Query the NITRO API documentation for available fields
