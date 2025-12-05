# debug - Raw API Output


> **Note**: All examples assume environment variables are set:
> ```bash
> export NETSCALER_HOST=192.168.1.10
> export NETSCALER_USER=nsroot
> export NETSCALER_PASS=nsroot
> ```
> See [Environment Variables](../../README.md#using-environment-variables-recommended) for details.

Display raw JSON output from the NITRO API for troubleshooting and discovery.

## Basic Usage

```bash
check_netscaler -C debug -o lbvserver
```

**Output:**
```
OK: debug output
{
  "lbvserver": [
    {
      "name": "web_lb",
      "ipv46": "192.168.10.10",
      "port": 80,
      "servicetype": "HTTP",
      "state": "UP",
      "curstate": "UP",
      ...
    }
  ]
}
```

## Use Cases

### 1. Discover available fields

Find out what fields are available for an object type:

```bash
check_netscaler -C debug -o system
```

### 2. Troubleshoot API responses

See exactly what the NITRO API returns:

```bash
check_netscaler -C debug -o hanode
```

### 3. Check specific object

View details of a specific named object:

```bash
check_netscaler -C debug -o lbvserver -n web_lb
```

### 4. Test API connectivity

Verify API access and authentication:

```bash
check_netscaler -C debug -o nsversion
```

## Advanced Usage

### Specify API endpoint

```bash
# Using stat endpoint (performance counters)
check_netscaler -C debug -o lbvserver --api stat

# Using config endpoint (configuration data)
check_netscaler -C debug -o lbvserver --api config
```

### Pretty-printed JSON

The output is automatically pretty-printed for readability.

## Common Object Types

### System Information
```bash
check_netscaler -C debug -o nsversion
check_netscaler -C debug -o nshardware
check_netscaler -C debug -o system
```

### Load Balancing
```bash
check_netscaler -C debug -o lbvserver
check_netscaler -C debug -o service
check_netscaler -C debug -o servicegroup
```

### SSL/Certificates
```bash
check_netscaler -C debug -o sslcertkey
check_netscaler -C debug -o sslvserver
```

### High Availability
```bash
check_netscaler -C debug -o hanode
check_netscaler -C debug -o hasync
```

### Network
```bash
check_netscaler -C debug -o interface
check_netscaler -C debug -o vlan
```

## Output Format

The debug command returns:
- Status: Always OK (unless API error)
- Message: "debug output"
- JSON: Pretty-printed NITRO API response

## Exit Codes

- `0` (OK) - API request successful, data displayed
- `3` (UNKNOWN) - API error or cannot retrieve data

## Tips

- Use `debug` before creating new monitoring checks
- Helps identify correct field names for `perfdata`, `matches`, etc.
- Shows actual NITRO API response structure
- Always returns OK status (for successful API calls)
- Output is JSON-formatted for easy parsing
- Use `--api stat` for performance counters
- Use `--api config` for configuration data
- Combine with `jq` for advanced JSON filtering: `check_netscaler ... | jq`
- Very useful for building custom `perfdata` or `matches` checks
