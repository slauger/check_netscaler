# nsconfig - Unsaved Configuration Detection

Check if there are unsaved configuration changes on the NetScaler.

## Basic Usage

```bash
check_netscaler -H 192.168.1.10 -s -C nsconfig
```

**Output (OK - No unsaved changes):**
```
OK: config saved
```

**Output (WARNING - Unsaved changes):**
```
WARNING: config not saved
```

## How It Works

The check queries the NetScaler configuration status to detect if there are pending changes that haven't been saved to disk.

**Status values:**
- Saved configuration = OK
- Unsaved changes = WARNING

## Use Cases

### 1. Post-change verification

Run after making configuration changes to ensure they've been saved:

```bash
check_netscaler -H 192.168.1.10 -s -C nsconfig
```

### 2. Scheduled monitoring

Monitor regularly to detect accidental unsaved changes:

```bash
# In cron or monitoring system
*/15 * * * * check_netscaler -H 192.168.1.10 -s -C nsconfig
```

### 3. Change management compliance

Ensure configuration is always saved as part of change control process.

## No Thresholds Required

This check does not accept warning/critical thresholds - it's a binary state:
- Saved = OK
- Not saved = WARNING

## Exit Codes

- `0` (OK) - Configuration is saved
- `1` (WARNING) - Configuration has unsaved changes
- `3` (UNKNOWN) - Cannot retrieve configuration status

## Tips

- Run this check after making any NetScaler configuration changes
- Unsaved changes are lost on reboot
- This check helps prevent accidental configuration loss
- No performance data is returned
- Very lightweight check, safe to run frequently
- Consider alerting on WARNING state in production environments
