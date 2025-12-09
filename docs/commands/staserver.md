# staserver - STA Server Availability


> **Note**: All examples assume environment variables are set:
> ```bash
> export NETSCALER_HOST=192.168.1.10
> export NETSCALER_USER=nsroot
> export NETSCALER_PASS=nsroot
> ```
> See [Environment Variables](../../README.md#using-environment-variables-recommended) for details.

Monitor Secure Ticket Authority (STA) server availability for NetScaler Gateway.

## Basic Usage

### Check all STA servers

```bash
check_netscaler -C staserver
```

**Output (OK):**
```
OK: 2 STA servers available
```

**Output (WARNING):**
```
WARNING: 1 STA server unavailable (sta02.example.com)
```

**Output (CRITICAL):**
```
CRITICAL: All STA servers unavailable
```

## What are STA Servers?

Secure Ticket Authority (STA) servers:
- Validate authentication tickets for XenApp/XenDesktop
- Required for Citrix Virtual Apps and Desktops access through NetScaler Gateway
- Multiple STAs provide redundancy

## Advanced Usage

### Filter by vServer

Check STA servers for a specific VPN vServer:

```bash
check_netscaler -C staserver --filter "vpn_gateway_vserver"
```

### Check specific STA server

```bash
check_netscaler -C staserver --filter "^sta01.example.com$"
```

### Exclude test STA servers

```bash
check_netscaler -C staserver --limit "^test-"
```

## STA Server States

The check monitors STA server availability through NetScaler's `staauthid` binding:

**States:**
- Available/Reachable = OK
- Unavailable/Unreachable = WARNING/CRITICAL
- All servers down = CRITICAL

## Binding Types

STA servers can be bound:
- **Globally** - Available to all VPN vServers
- **Per vServer** - Specific to one VPN vServer

The check retrieves both binding types.

## Common Use Cases

### 1. Monitor all STA servers

```bash
check_netscaler -C staserver
```

### 2. Check production STA servers only

```bash
check_netscaler -C staserver --filter "^prod-"
```

### 3. Monitor specific VPN vServer's STAs

```bash
check_netscaler -C staserver --filter "vpn_prod"
```

### 4. Exclude development STAs

```bash
check_netscaler -C staserver --limit "^(dev-|test-)"
```

## Status Logic

- **OK**: All STA servers are available
- **WARNING**: One or more STA servers unavailable (but not all)
- **CRITICAL**: All STA servers unavailable
- **UNKNOWN**: Cannot retrieve STA server data

## Exit Codes

- `0` (OK) - All STA servers available
- `1` (WARNING) - Some STA servers unavailable
- `2` (CRITICAL) - All STA servers unavailable
- `3` (UNKNOWN) - Cannot retrieve STA server status

## Tips

- Deploy at least 2 STA servers for redundancy
- Monitor both global and vServer-specific STA bindings
- Use `--filter` to focus on production STAs
- STA server availability is critical for Citrix Virtual Apps/Desktops access
- Unavailable STAs will cause authentication failures
- NetScaler polls STA servers periodically
- Check should correlate with Citrix infrastructure monitoring
- STA servers are typically Citrix StoreFront or Delivery Controller servers
