# license - License Expiration Monitoring

Monitor NetScaler license file expiration dates.

## Basic Usage

### Check all licenses

```bash
check_netscaler -H 192.168.1.10 -s -C license
```

**Output (OK):**
```
OK: license.lic: 245 days until expiry | license.lic=245;30;10
```

**Output (WARNING):**
```
WARNING: license.lic expires in 25 days | license.lic=25;30;10
```

**Output (CRITICAL):**
```
CRITICAL: license.lic expires in 5 days | license.lic=5;30;10
```

### Check with custom thresholds

```bash
check_netscaler -H 192.168.1.10 -s -C license -w 60 -c 30
```

**Default thresholds:** `-w 30 -c 10` (30 days warning, 10 days critical)

## Advanced Usage

### Check specific license file

```bash
check_netscaler -H 192.168.1.10 -s -C license -n license.lic
```

### Multiple license files

NetScaler may have multiple `.lic` files:

```bash
check_netscaler -H 192.168.1.10 -s -C license
```

Checks all `.lic` files automatically.

## License Types

### Time-based Licenses
- Have expiration date in INCREMENT line
- Format: `dd-mmm-yyyy` (e.g., `31-dec-2025`)
- Checked against thresholds

### Permanent Licenses
- Contain "PERMANENT" keyword
- Never expire
- Always return OK

## License File Format

The check reads license files via NetScaler's systemfile API and parses:

```
INCREMENT feature_name vendor/version expiry=dd-mmm-yyyy
```

Or:

```
INCREMENT feature_name vendor/version PERMANENT
```

## Performance Data

```
| filename=days_until_expiry;warn;crit
```

Example:
```
| license.lic=245;30;10
```

For permanent licenses:
```
| license.lic=999999;30;10
```

## Common Use Cases

### 1. Production environment (60/30 day thresholds)

```bash
check_netscaler -H 192.168.1.10 -s -C license -w 60 -c 30
```

### 2. Default monitoring (30/10 days)

```bash
check_netscaler -H 192.168.1.10 -s -C license
```

### 3. Specific license file

```bash
check_netscaler -H 192.168.1.10 -s -C license -n CNS_V3000_SERVER_PLT_Retail.lic
```

### 4. Check all licenses in /nsconfig/license/

```bash
check_netscaler -H 192.168.1.10 -s -C license
```

Auto-discovers all `.lic` files.

## Exit Codes

- `0` (OK) - All licenses valid beyond warning threshold or permanent
- `1` (WARNING) - One or more licenses expiring within warning threshold
- `2` (CRITICAL) - One or more licenses expiring within critical threshold
- `3` (UNKNOWN) - Cannot retrieve license data or parse error

## Tips

- Set warning threshold high enough for procurement/renewal process
- 60-day warning recommended for enterprise licensing
- Permanent licenses always return OK
- License files are read from `/nsconfig/license/` directory
- Files are base64-decoded automatically
- Multiple INCREMENT lines are all checked
- The check only monitors expiration, not feature enablement
- Ensure NetScaler user has read access to license files
