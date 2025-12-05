# sslcert - SSL Certificate Expiration Monitoring

Monitor SSL certificate expiration dates on your NetScaler.

## Basic Usage

### Check all certificates

```bash
check_netscaler -H 192.168.1.10 -s -C sslcert
```

**Output (OK):**
```
OK: 5 certificates valid (wildcard.example.com: 87 days, api.example.com: 245 days, ...)
```

**Output (WARNING):**
```
WARNING: wildcard.example.com expires in 25 days | wildcard.example.com=25;30;10
```

**Output (CRITICAL):**
```
CRITICAL: old-cert.example.com expires in 5 days | old-cert.example.com=5;30;10
```

### Check with custom thresholds

```bash
check_netscaler -H 192.168.1.10 -s -C sslcert -w 60 -c 30
```

Warns if certificate expires within 60 days, critical if within 30 days.

**Default thresholds:** `-w 30 -c 10` (30 days warning, 10 days critical)

## Advanced Usage

### Filter specific certificates

Check only certificates matching a pattern:

```bash
check_netscaler -H 192.168.1.10 -s -C sslcert --filter "^wildcard"
```

### Exclude test certificates

```bash
check_netscaler -H 192.168.1.10 -s -C sslcert --limit "^test-"
```

### Check single certificate

```bash
check_netscaler -H 192.168.1.10 -s -C sslcert --filter "^wildcard.example.com$"
```

## Certificate Status

The check evaluates certificates based on days until expiration:

- **OK**: Expires in more than WARNING days
- **WARNING**: Expires within WARNING days but more than CRITICAL days
- **CRITICAL**: Expires within CRITICAL days
- **UNKNOWN**: Cannot retrieve certificate data

## Performance Data

```
| certname=days_until_expiry;warn;crit
```

Example:
```
| wildcard.example.com=87;30;10 api.example.com=245;30;10
```

## Common Use Cases

### 1. Production certificates (60/30 day thresholds)

```bash
check_netscaler -H 192.168.1.10 -s -C sslcert -w 60 -c 30 --filter "^prod-"
```

### 2. Wildcard certificates

```bash
check_netscaler -H 192.168.1.10 -s -C sslcert --filter "wildcard"
```

### 3. All certificates (default 30/10)

```bash
check_netscaler -H 192.168.1.10 -s -C sslcert
```

### 4. Exclude dev/test environments

```bash
check_netscaler -H 192.168.1.10 -s -C sslcert --limit "^(dev-|test-)"
```

## Exit Codes

- `0` (OK) - All certificates valid beyond warning threshold
- `1` (WARNING) - One or more certificates expiring within warning threshold
- `2` (CRITICAL) - One or more certificates expiring within critical threshold
- `3` (UNKNOWN) - Cannot retrieve certificate data

## Tips

- Set warning threshold high enough for renewal process (60 days recommended)
- Use `--filter` to monitor specific certificate groups
- Monitor all certificates by default, exclude test certs with `--limit`
- Certificates are identified by their common name (CN)
- The check retrieves certificate data from NetScaler's certificate store
