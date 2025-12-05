# hastatus - High Availability Status Monitoring

Monitor NetScaler High Availability (HA) configuration and sync status.

## Basic Usage

### Check HA status

```bash
check_netscaler -H 192.168.1.10 -s -C hastatus
```

**Output (OK - PRIMARY):**
```
OK: HA node PRIMARY/UP | hatotpktrx=1234567 hatotpkttx=9876543
```

**Output (OK - SECONDARY):**
```
OK: HA node SECONDARY/UP | hatotpktrx=1234567 hatotpkttx=9876543
```

**Output (WARNING):**
```
WARNING: HA node STAYSECONDARY/UP
```

**Output (CRITICAL):**
```
CRITICAL: HA node PRIMARY/PARTIALFAIL
```

## HA States

### Master States (hacurmasterstate)
- `PRIMARY` - OK (active node)
- `SECONDARY` - OK (standby node)
- `STAYSECONDARY` - WARNING (forced secondary)
- `CLAIMING` - WARNING (failover in progress)
- `FORCE CHANGE` - WARNING (forced state change)

### Node States (hacurstate)
- `UP` - OK (node operational)
- `DISABLED` - WARNING (HA disabled)
- `INIT` - WARNING (initializing)
- `DUMB` - WARNING (not synchronized)
- `PARTIALFAIL` - CRITICAL (partial failure)
- `COMPLETEFAIL` - CRITICAL (complete failure)
- `PARTIALFAILSSL` - CRITICAL (SSL sync failure)
- `ROUTEMONITORFAIL` - CRITICAL (route monitor failure)

## HA Issues Detection

The check monitors:
- **Sync failures** (haerrsyncfailure)
- **Propagation timeouts** (haerrproptimeout)
- **Configuration mismatch**
- **Node health**

**Warning conditions:**
- Sync failures detected
- Propagation timeouts
- Node in intermediate state

**Critical conditions:**
- Node failure states
- HA not configured properly

## Performance Data

```
| hatotpktrx=packets hatotpkttx=packets hapktrxrate=rate hapkttxrate=rate
```

- `hatotpktrx` - Total packets received
- `hatotpkttx` - Total packets transmitted
- `hapktrxrate` - Packet receive rate
- `hapkttxrate` - Packet transmit rate

## Advanced Usage

### Check with specific API endpoint

```bash
# Using stat endpoint (default)
check_netscaler -H 192.168.1.10 -s -C hastatus --api stat

# Using config endpoint
check_netscaler -H 192.168.1.10 -s -C hastatus --api config
```

### Custom object type

```bash
check_netscaler -H 192.168.1.10 -s -C hastatus -o hanode
```

## Common Use Cases

### 1. Basic HA health check

```bash
check_netscaler -H 192.168.1.10 -s -C hastatus
```

### 2. Monitor both nodes

```bash
# Check primary
check_netscaler -H 192.168.1.10 -s -C hastatus

# Check secondary
check_netscaler -H 192.168.1.11 -s -C hastatus
```

### 3. Sync status monitoring

The command automatically checks for sync errors and propagation issues.

## Exit Codes

- `0` (OK) - HA operational, node healthy
- `1` (WARNING) - Intermediate states, sync issues, or propagation timeouts
- `2` (CRITICAL) - Node failures or HA misconfiguration
- `3` (UNKNOWN) - Cannot retrieve HA status or API error

## Tips

- Monitor both HA nodes separately for complete visibility
- Check should always return consistent state on both nodes
- Sync failures are WARNING by default
- Node failure states are always CRITICAL
- HA must be configured on the NetScaler for this check to work
- Use in combination with `state` command for complete health monitoring
