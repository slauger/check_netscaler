# interfaces - Network Interface Monitoring


> **Note**: All examples assume environment variables are set:
> ```bash
> export NETSCALER_HOST=192.168.1.10
> export NETSCALER_USER=nsroot
> export NETSCALER_PASS=nsroot
> ```
> See [Environment Variables](../../README.md#using-environment-variables-recommended) for details.

Monitor network interface status and statistics on NetScaler.

## Basic Usage

### Check all interfaces

```bash
check_netscaler -C interfaces
```

**Output (OK):**
```
OK: 4 interfaces UP (1/1, 1/2, 10/1, 10/2) | 1/1.rxbytes=... 1/1.txbytes=... 1/2.rxbytes=...
```

**Output (CRITICAL):**
```
CRITICAL: 3 UP, 1 DOWN (10/2) | 1/1.rxbytes=... 1/2.rxbytes=... 10/1.rxbytes=...
```

### Check specific interface

```bash
check_netscaler -C interfaces --filter "^1/1$"
```

## Interface States

The check evaluates multiple state indicators:

- `linkstate` - Physical link state (1=UP, 0=DOWN)
- `intfstate` - Interface state (1=UP, 0=DOWN)
- `state` - Administrative state (ENABLED/DISABLED)

**Status logic:**
- CRITICAL if linkstate=0 or intfstate=0
- WARNING if state=DISABLED
- OK if all states indicate UP/ENABLED

## Advanced Usage

### Filter by pattern

Check only uplink interfaces:

```bash
check_netscaler -C interfaces --filter "^10/"
```

### Exclude management interfaces

```bash
check_netscaler -C interfaces --limit "^0/"
```

### Custom separator for perfdata

```bash
check_netscaler -C interfaces --separator "_"
```

Output: `1_1.rxbytes=...` instead of `1/1.rxbytes=...`

## Performance Data

Per interface:
```
| devicename.rxbytes=bytes devicename.txbytes=bytes
  devicename.rxpkts=packets devicename.txpkts=packets
  devicename.rxerrors=errors devicename.txerrors=errors
```

Example:
```
| 1/1.rxbytes=12345678 1/1.txbytes=87654321 1/1.rxpkts=9876 1/1.txpkts=5432
  1/1.rxerrors=0 1/1.txerrors=0
```

## Common Use Cases

### 1. Monitor all production interfaces

```bash
check_netscaler -C interfaces
```

### 2. Check 10GbE uplinks only

```bash
check_netscaler -C interfaces --filter "^10/"
```

### 3. Monitor specific interface

```bash
check_netscaler -C interfaces --filter "^1/1$"
```

### 4. Exclude VLAN interfaces

```bash
check_netscaler -C interfaces --limit "^LA/"
```

### 5. Custom perfdata separator (for Icinga/Nagios compatibility)

```bash
check_netscaler -C interfaces --separator "_"
```

## Interface Naming

NetScaler interface formats:
- Physical: `1/1`, `1/2`, `10/1`, `10/2`
- Link Aggregation (LA): `LA/1`, `LA/2`
- VLANs: Various formats depending on configuration

## Exit Codes

- `0` (OK) - All interfaces UP and ENABLED
- `1` (WARNING) - One or more interfaces DISABLED
- `2` (CRITICAL) - One or more interfaces DOWN
- `3` (UNKNOWN) - Cannot retrieve interface status

## Tips

- Use `--filter` to monitor specific interface groups
- Use `--limit` to exclude management or VLAN interfaces
- The `--separator` option helps with special characters in perfdata
- Physical interfaces use `slot/port` notation
- Link state DOWN is always CRITICAL
- Administrative DISABLED is WARNING
- Performance data includes bytes, packets, and errors
