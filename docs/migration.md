# Migration Guide - v1.x to v2.0

This guide helps you migrate from check_netscaler v1.x (Perl) to v2.0 (Python).

## Breaking Changes

### 1. HTTPS is now the default protocol

**Old behavior (v1.x):** HTTP was default, `-s/--ssl` flag required for HTTPS
**New behavior (v2.0):** HTTPS is default, `--no-ssl` flag for HTTP

**Rationale:** HTTPS is the standard for NetScaler management interfaces in production environments. Making it the default improves security and simplifies command syntax.

**Migration:**

**Before (v1.x):**
```bash
check_netscaler -H 192.168.1.10 -s -C state -o lbvserver
```

**After (v2.0):**
```bash
# HTTPS is now default
check_netscaler -H 192.168.1.10 -C state -o lbvserver

# For HTTP (rare cases):
check_netscaler -H 192.168.1.10 --no-ssl -C state -o lbvserver
```

### 2. Python 3.8+ required

**Old:** Perl 5.x
**New:** Python 3.8, 3.9, 3.10, 3.11, or 3.12

Ensure Python 3.8+ is available on your monitoring server.

### 3. Command naming changes

- `string` → `matches`
- `string_not` → `matches_not`

Old command names are not supported in v2.0.

### 4. Environment variable changes

**Old (v1.x):**
- `NETSCALER_USERNAME`

**New (v2.0):**
- `NETSCALER_USER` (changed for consistency)
- `NETSCALER_HOST` (new)
- `NETSCALER_PASS` (new)

## Step-by-Step Migration

### 1. Update Nagios Command Definitions

Remove `-s/--ssl` flags from all command definitions:

```diff
define command {
    command_name check_netscaler_state
-   command_line /usr/bin/check_netscaler -H $HOSTADDRESS$ -s -C state -o $ARG1$ -n $ARG2$
+   command_line /usr/bin/check_netscaler -H $HOSTADDRESS$ -C state -o $ARG1$ -n $ARG2$
}

define command {
    command_name check_netscaler_sslcert
-   command_line /usr/bin/check_netscaler -H $HOSTADDRESS$ -u $ARG1$ -p $ARG2$ -s -C sslcert -w $ARG3$ -c $ARG4$
+   command_line /usr/bin/check_netscaler -H $HOSTADDRESS$ -u $ARG1$ -p $ARG2$ -C sslcert -w $ARG3$ -c $ARG4$
}
```

### 2. Update Icinga 2 CheckCommand Templates

Change SSL argument from opt-in to opt-out:

```diff
template CheckCommand "netscaler-common" {
  arguments = {
    "-H" = "$netscaler_host$"
    "-u" = "$netscaler_username$"
    "-p" = "$netscaler_password$"
-   "--ssl" = {
-     set_if = "$netscaler_ssl$"
+   "--no-ssl" = {
+     set_if = "$netscaler_no_ssl$"
    }
    "-t" = "$netscaler_timeout$"
  }

  vars.netscaler_username = "nsroot"
  vars.netscaler_password = "nsroot"
- vars.netscaler_ssl = true
  vars.netscaler_timeout = 15
}
```

### 3. Update Command Names

If using the old command names:

```diff
# Nagios/Icinga
- check_netscaler -H 192.168.1.10 -C string -o hanode -n hacurmasterstate -s PRIMARY
+ check_netscaler -H 192.168.1.10 -C matches -o hanode -n hacurmasterstate -s PRIMARY

- check_netscaler -H 192.168.1.10 -C string_not -o hanode -n hacurstate -s UNKNOWN
+ check_netscaler -H 192.168.1.10 -C matches_not -o hanode -n hacurstate -s UNKNOWN
```

### 4. Consider Using Environment Variables (Recommended)

For improved security, use environment variables instead of command-line arguments:

**Benefits:**
- Credentials not visible in process listings (`ps`, `top`, `/proc`)
- Set once, use in multiple commands
- Works seamlessly with Icinga 2 `env` attribute and Nagios/systemd

**Usage:**

```bash
# In systemd service file or shell profile
export NETSCALER_HOST=192.168.1.10
export NETSCALER_USER=monitoring
export NETSCALER_PASS=SecurePassword123

# Now run checks without passing credentials
check_netscaler -C state -o lbvserver
check_netscaler -C sslcert -w 60 -c 30
check_netscaler -C hastatus
```

**Icinga 2 example:**

```icinga2
object CheckCommand "netscaler-state" {
  import "netscaler-common"

  command = [ PluginDir + "/check_netscaler" ]
  arguments += {
    "-C" = "state"
    "-o" = "$netscaler_objecttype$"
    "-n" = "$netscaler_objectname$"
  }

  # Set credentials via environment
  env = {
    NETSCALER_HOST = "$netscaler_host$"
    NETSCALER_USER = "$netscaler_username$"
    NETSCALER_PASS = "$netscaler_password$"
  }
}
```

### 5. Test in Parallel

Before fully migrating:

1. Install v2.0 alongside v1.x (e.g., `/usr/local/bin/check_netscaler_v2`)
2. Test v2.0 commands manually
3. Verify output matches v1.x expectations
4. Update a few services to use v2.0
5. Monitor for issues
6. Gradually migrate remaining services
7. Remove v1.x when complete

## New Features in v2.0

### Environment Variable Support

- `NETSCALER_HOST` - NetScaler hostname or IP address
- `NETSCALER_USER` - Username for authentication
- `NETSCALER_PASS` - Password for authentication

CLI arguments always take precedence over environment variables.

### Enhanced Commands

- **`ntp`** - NTP synchronization monitoring (new command)
- **`perfdata`** - Enhanced generic performance data collection
- **Advanced filtering** - Regex support with `--filter` and `--limit`
- **Custom labels** - Performance data labels with `--label`
- **Custom separators** - Flexible separators with `--separator`

## Compatibility

### Supported Versions

- **Python:** 3.8, 3.9, 3.10, 3.11, 3.12
- **NetScaler/ADC:** 11.x, 12.x, 13.x, 14.x
- **NITRO API:** v1 (default), v2 (via `-a v2`)
- **Monitoring Systems:** Nagios, Icinga, Icinga 2, Naemon, Shinken, Sensu

### Command Compatibility

All 16 commands from v1.x are available in v2.0:

| Command | v1.x | v2.0 | Notes |
|---------|------|------|-------|
| `state` | ✅ | ✅ | Fully compatible |
| `above`/`below` | ✅ | ✅ | Fully compatible |
| `sslcert` | ✅ | ✅ | Fully compatible |
| `nsconfig` | ✅ | ✅ | Fully compatible |
| `debug` | ✅ | ✅ | Fully compatible |
| `hwinfo` | ✅ | ✅ | Fully compatible |
| `servicegroup` | ✅ | ✅ | Fully compatible |
| `string` / `matches` | ✅ | ✅ | Renamed to `matches` |
| `string_not` / `matches_not` | ✅ | ✅ | Renamed to `matches_not` |
| `staserver` | ✅ | ✅ | Fully compatible |
| `hastatus` | ✅ | ✅ | Fully compatible |
| `license` | ✅ | ✅ | Fully compatible |
| `interfaces` | ✅ | ✅ | Fully compatible |
| `perfdata` | ✅ | ✅ | Enhanced with more features |
| `ntp` | ✅ | ✅ | Fully compatible |

## Need Help?

- **Documentation:** See [commands/](commands/) for detailed usage examples
- **Issues:** Report problems at https://github.com/slauger/check_netscaler/issues
- **Integration:** See [examples/icinga2/](examples/icinga2/) and [examples/nagios/](examples/nagios/) for configuration examples

## Rollback

If you need to rollback to v1.x:

1. Checkout a v1.x tag: `git checkout v1.6.2`
2. Or download from releases: https://github.com/slauger/check_netscaler/releases
3. Restore your previous Nagios/Icinga configuration
