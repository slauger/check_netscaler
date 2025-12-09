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

### Backup vServer Monitoring

Monitor backup load balancers and alert when they become active (only for `lbvserver` objects):

```bash
# Alert with WARNING severity when backup is active
check_netscaler -C state -o lbvserver -n web_lb --check-backup warning

# Alert with CRITICAL severity when backup is active
check_netscaler -C state -o lbvserver -n api_lb --check-backup critical
```

**Normal output (backup not active):**
```
OK: lbvserver is UP | total=1 ok=1 warning=0 critical=0 unknown=0
```

**Backup active output (WARNING):**
```
WARNING: lbvserver is UP; Backup vServer active: web_lb_backup | total=1 ok=1 warning=0 critical=0 unknown=0
[OK] web_lb: UP
[WARNING] web_lb: Backup vServer 'web_lb_backup' is active
```

**Backup active output (CRITICAL):**
```
CRITICAL: lbvserver is UP; Backup vServer active: api_lb_backup | total=1 ok=1 warning=0 critical=0 unknown=0
[OK] api_lb: UP
[CRITICAL] api_lb: Backup vServer 'api_lb_backup' is active
```

**Use cases:**
- Detect failover scenarios where primary vServer has failed
- Monitor high availability configurations
- Alert when traffic is being served by backup infrastructure
- Track when primary services have been restored (backup no longer active)

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

### 5. Monitor backup vServer status for critical applications

```bash
# Critical alert when backup becomes active for production web tier
check_netscaler -C state -o lbvserver -n prod_web_lb --check-backup critical

# Warning alert for less critical applications
check_netscaler -C state -o lbvserver -n test_api_lb --check-backup warning
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
