# above / below - Threshold-Based Monitoring

The `above` and `below` commands monitor numeric metrics against thresholds (CPU, memory, disk usage, etc.).

> **Note**: All examples assume environment variables are set:
> ```bash
> export NETSCALER_HOST=192.168.1.10
> export NETSCALER_USER=nsroot
> export NETSCALER_PASS=nsroot
> ```
> See [Environment Variables](../../README.md#using-environment-variables-recommended) for details.

## Syntax

```bash
# Check if value is ABOVE threshold (alert when too high)
check_netscaler -C above -o <objecttype> -n <field> -w <warn> -c <crit>

# Check if value is BELOW threshold (alert when too low)
check_netscaler -C below -o <objecttype> -n <field> -w <warn> -c <crit>
```

## Common Metrics

### System Resources
- `cpuusagepcnt` - CPU usage percentage
- `mgmtcpuusagepcnt` - Management CPU usage
- `memusagepcnt` - Memory usage percentage
- `disk0perusage` - Disk 0 usage percentage
- `disk1perusage` - Disk 1 usage percentage

### Network & Performance
- `tcpcurestablishedconn` - Current TCP connections
- `rxbytesrate` - Receive bytes per second
- `txbytesrate` - Transmit bytes per second

## Basic Usage

### Check CPU usage

```bash
check_netscaler -C above -o system -n cpuusagepcnt -w 75 -c 90
```

**Output (OK):**
```
OK: system.cpuusagepcnt = 45 | cpuusagepcnt=45;75;90
```

**Output (WARNING):**
```
WARNING: system.cpuusagepcnt = 78 (above 75) | cpuusagepcnt=78;75;90
```

**Output (CRITICAL):**
```
CRITICAL: system.cpuusagepcnt = 92 (above 90) | cpuusagepcnt=92;75;90
```

### Check memory usage

```bash
check_netscaler -C above -o system -n memusagepcnt -w 80 -c 95
```

**Output:**
```
OK: system.memusagepcnt = 62 | memusagepcnt=62;80;95
```

### Check disk usage

```bash
check_netscaler -C above -o system -n disk0perusage -w 70 -c 85
```

**Output:**
```
WARNING: system.disk0perusage = 73 (above 70) | disk0perusage=73;70;85
```

## Advanced Usage

### Multiple metrics (comma-separated)

Monitor multiple metrics in a single check:

```bash
check_netscaler -C above -o system \
  -n cpuusagepcnt,memusagepcnt,disk0perusage \
  -w 75,80,70 \
  -c 90,95,85
```

**Output:**
```
OK: system.cpuusagepcnt = 45, system.memusagepcnt = 62, system.disk0perusage = 58 | cpuusagepcnt=45;75;90 memusagepcnt=62;80;95 disk0perusage=58;70;85
```

**Note:** Warning and critical thresholds must match the number of fields!

### Check TCP connections

```bash
check_netscaler -C above -o system -n tcpcurestablishedconn -w 5000 -c 8000
```

### Check management CPU

```bash
check_netscaler -C above -o system -n mgmtcpuusagepcnt -w 50 -c 75
```

## below Command

Use `below` to alert when values are TOO LOW (e.g., minimum connection thresholds):

### Example: Alert if connections drop too low

```bash
check_netscaler -C below -o lbvserver -n activeconnections -w 10 -c 5 --objectname web_lb
```

**Output (OK):**
```
OK: lbvserver.activeconnections = 50 | activeconnections=50;10;5
```

**Output (WARNING):**
```
WARNING: lbvserver.activeconnections = 8 (below 10) | activeconnections=8;10;5
```

**Output (CRITICAL):**
```
CRITICAL: lbvserver.activeconnections = 3 (below 5) | activeconnections=3;10;5
```

## Object Type Examples

### Check load balancer vServer metrics

```bash
# Check hit rate
check_netscaler -C above -o lbvserver -n totalhits --objectname web_lb -w 1000 -c 2000

# Check request rate
check_netscaler -C above -o lbvserver -n requestsrate --objectname api_lb -w 500 -c 1000
```

### Check service metrics

```bash
check_netscaler -C above -o service -n activeconns --objectname web_svc_01 -w 100 -c 200
```

## Performance Data Format

All checks output performance data in Nagios format:

```
| metric=value;warn;crit;min;max
```

Example:
```
| cpuusagepcnt=45;75;90;0;100 memusagepcnt=62;80;95;0;100
```

## Common Use Cases

### 1. System health monitoring

```bash
# CPU
check_netscaler -C above -o system -n cpuusagepcnt -w 75 -c 90

# Memory
check_netscaler -C above -o system -n memusagepcnt -w 80 -c 95

# Disk
check_netscaler -C above -o system -n disk0perusage -w 70 -c 85
```

### 2. All-in-one system check

```bash
check_netscaler -C above -o system \
  -n cpuusagepcnt,memusagepcnt,disk0perusage \
  -w 75,80,70 \
  -c 90,95,85
```

### 3. Network throughput monitoring

```bash
check_netscaler -C above -o system \
  -n rxbytesrate,txbytesrate \
  -w 1000000000,1000000000 \
  -c 1500000000,1500000000
```

### 4. Connection monitoring

```bash
check_netscaler -C above -o system -n tcpcurestablishedconn -w 5000 -c 8000
```

## Exit Codes

- `0` (OK) - All metrics within thresholds
- `1` (WARNING) - One or more metrics exceed warning threshold
- `2` (CRITICAL) - One or more metrics exceed critical threshold
- `3` (UNKNOWN) - Cannot retrieve metrics or API error

## Tips

- Use `above` for "high is bad" metrics (CPU, memory, disk)
- Use `below` for "low is bad" metrics (connections, throughput)
- Combine multiple metrics in one check for efficiency
- Warning threshold must be less severe than critical for `above`
- Warning threshold must be more severe than critical for `below`
- Object type is typically `system` for resource monitoring
- Use `--objectname` when checking specific objects (vServers, services)
