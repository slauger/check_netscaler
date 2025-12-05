# servicegroup - ServiceGroup Member Quorum Monitoring

Monitor ServiceGroup member availability and quorum (percentage of active members).

## Basic Usage

### Check servicegroup quorum

```bash
check_netscaler -H 192.168.1.10 -s -C servicegroup -n web_sg -w 50 -c 25
```

**Output (OK):**
```
OK: servicegroup web_sg: 8/10 members UP (80%) | web_sg.member_quorum=80;50;25
```

**Output (WARNING):**
```
WARNING: servicegroup web_sg: 4/10 members UP (40%) | web_sg.member_quorum=40;50;25
```

**Output (CRITICAL):**
```
CRITICAL: servicegroup web_sg: 2/10 members UP (20%) | web_sg.member_quorum=20;50;25
```

## Threshold Logic

Thresholds are **minimum percentages** of active members:

- **WARNING**: Alert if quorum falls BELOW warning %
- **CRITICAL**: Alert if quorum falls BELOW critical %

Example with `-w 50 -c 25`:
- OK: ≥50% members UP
- WARNING: 25-49% members UP
- CRITICAL: <25% members UP

## Advanced Usage

### Custom separator for perfdata

```bash
check_netscaler -H 192.168.1.10 -s -C servicegroup -n web_sg -w 50 -c 25 --separator "_"
```

**Output:**
```
OK: servicegroup web_sg: 8/10 members UP (80%) | web_sg_member_quorum=80;50;25
```

### Check without thresholds

```bash
check_netscaler -H 192.168.1.10 -s -C servicegroup -n web_sg
```

Returns OK with member count, no threshold checking.

## Member States

The check counts members as UP if their state is:
- `UP` - Member is operational
- `ENABLED` - Member is enabled and healthy

Members are DOWN if:
- `DOWN` - Member is down
- `OUT OF SERVICE` - Member is disabled
- `GOING OUT OF SERVICE` - Member is being drained

## Performance Data

```
| servicegroupname.member_quorum=percentage;warn;crit;0;100
```

Example:
```
| web_sg.member_quorum=80;50;25;0;100
```

## Common Use Cases

### 1. Production services (strict quorum)

```bash
check_netscaler -H 192.168.1.10 -s -C servicegroup -n prod_web_sg -w 75 -c 50
```

Requires at least 75% healthy, critical below 50%.

### 2. Development services (relaxed quorum)

```bash
check_netscaler -H 192.168.1.10 -s -C servicegroup -n dev_web_sg -w 25 -c 10
```

More tolerant of member failures.

### 3. Database cluster (high availability)

```bash
check_netscaler -H 192.168.1.10 -s -C servicegroup -n db_cluster_sg -w 66 -c 33
```

2 out of 3 nodes minimum (66%), critical if only 1 node (33%).

### 4. Information only (no thresholds)

```bash
check_netscaler -H 192.168.1.10 -s -C servicegroup -n monitoring_sg
```

## Quorum Calculation

```
quorum % = (UP members / total members) × 100
```

Examples:
- 8/10 members UP = 80% quorum
- 5/10 members UP = 50% quorum
- 1/10 members UP = 10% quorum

## Exit Codes

- `0` (OK) - Quorum above or equal to warning threshold
- `1` (WARNING) - Quorum below warning but above/equal critical threshold
- `2` (CRITICAL) - Quorum below critical threshold
- `3` (UNKNOWN) - Cannot retrieve servicegroup data

## Tips

- Set warning threshold based on acceptable degraded performance
- Set critical threshold based on minimum viable service level
- For N+1 redundancy: warn at 100%, crit at 50%
- For N+2 redundancy: warn at 66%, crit at 33%
- Use with `state` command for detailed member status
- ServiceGroup name is case-sensitive
- Members are bound to services, not servers directly
