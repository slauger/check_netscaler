# state - Object State Monitoring

The `state` command checks the operational state of NetScaler objects (vServers, services, servicegroups, servers).

**Most important command - covers 80% of monitoring use cases!**

> **Note**: All examples assume environment variables are set:
> ```bash
> export NETSCALER_HOST=192.168.1.10
> export NETSCALER_USER=nsroot
> export NETSCALER_PASS=nsroot
> ```
> See [Environment Variables](../../README.md#using-environment-variables-recommended) for details.

## Supported Object Types

- `lbvserver` - Load Balancing Virtual Servers
- `vpnvserver` - VPN Virtual Servers
- `gslbvserver` - GSLB Virtual Servers
- `csvserver` - Content Switching Virtual Servers
- `service` - Services
- `servicegroup` - Service Groups
- `server` - Servers

## Basic Usage

### Check all load balancing vServers

```bash
check_netscaler -C state -o lbvserver
```

**Output:**
```
OK: lbvserver - 5 UP (web_lb, app_lb, api_lb, admin_lb, monitoring_lb) | total=5 up=5 down=0
```

### Check specific vServer by name

```bash
check_netscaler -C state -o lbvserver -n web_lb
```

**Output:**
```
OK: lbvserver web_lb is UP | web_lb.activeconnections=42
```

### Check all services

```bash
check_netscaler -C state -o service
```

**Output:**
```
WARNING: service - 18 UP, 2 DOWN (web_svc_01, db_svc_backup) | total=20 up=18 down=2
```

## Advanced Usage

### Filter by regex pattern

Check only vServers matching a pattern:

```bash
check_netscaler -C state -o lbvserver --filter "^web_"
```

**Output:**
```
OK: lbvserver - 3 UP (web_lb_prod, web_lb_test, web_lb_dev) | total=3 up=3 down=0
```

### Limit results (inverse filter)

Check all vServers EXCEPT those matching a pattern:

```bash
check_netscaler -C state -o lbvserver --limit "^test_"
```

Excludes all vServers starting with "test_".

### Multiple object types

Check multiple object types in sequence:

```bash
# Check vServers
check_netscaler -C state -o lbvserver

# Check services
check_netscaler -C state -o service

# Check service groups
check_netscaler -C state -o servicegroup
```

## State Mappings

### vServer States
- `UP` - OK (vServer is operational)
- `DOWN` - CRITICAL (vServer is down)
- `OUT OF SERVICE` - WARNING (administratively disabled)
- `UNKNOWN` - UNKNOWN (state cannot be determined)

### Service States
- `UP` - OK
- `DOWN` - CRITICAL
- `OUT OF SERVICE` - WARNING
- `GOING OUT OF SERVICE` - WARNING
- `UNKNOWN` - UNKNOWN

## Performance Data

The command outputs performance data for active connections:

```
| objectname.activeconnections=<value>
```

For multiple objects:
```
| total=<total> up=<up_count> down=<down_count>
```

## Common Use Cases

### 1. Monitor production load balancers

```bash
check_netscaler -C state -o lbvserver --filter "^prod_"
```

### 2. Check database services

```bash
check_netscaler -C state -o service --filter "^db_"
```

### 3. Monitor all service groups

```bash
check_netscaler -C state -o servicegroup
```

### 4. Exclude test/dev environments

```bash
check_netscaler -C state -o lbvserver --limit "^(test_|dev_)"
```

## Exit Codes

- `0` (OK) - All objects are UP
- `1` (WARNING) - Some objects are OUT OF SERVICE
- `2` (CRITICAL) - One or more objects are DOWN
- `3` (UNKNOWN) - Cannot retrieve state or API error

## Tips

- Use `--filter` to monitor specific groups of objects
- Use `--limit` to exclude test/dev environments from production monitoring
- The `state` command is the most efficient for general health monitoring
- Combine with other commands (like `servicegroup`) for detailed member status
