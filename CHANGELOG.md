# Changelog

All notable changes to check_netscaler v2.0 will be documented in this file.

## [Unreleased] - v2.0.0

### Breaking Changes

#### HTTPS is now the default protocol
- **Old behavior**: HTTP was default, `-s/--ssl` flag required for HTTPS
- **New behavior**: HTTPS is default, `--no-ssl` flag for HTTP
- **Migration**: Remove `-s` flags from all command invocations and monitoring configurations

**Before (v1.x):**
```bash
check_netscaler -H 192.168.1.10 -s -C state -o lbvserver
```

**After (v2.0):**
```bash
check_netscaler -H 192.168.1.10 -C state -o lbvserver

# For HTTP (rare):
check_netscaler -H 192.168.1.10 --no-ssl -C state -o lbvserver
```

**Rationale**: HTTPS is the standard for NetScaler management interfaces in production environments. Making it the default improves security and simplifies command syntax.

### Added

#### Environment Variable Support
- `NETSCALER_HOST` - NetScaler hostname or IP address
- `NETSCALER_USER` - Username for authentication
- `NETSCALER_PASS` - Password for authentication

These variables provide fallback values when command-line arguments are not provided. CLI arguments always take precedence.

**Usage:**
```bash
export NETSCALER_HOST=192.168.1.10
export NETSCALER_USER=monitoring
export NETSCALER_PASS=SecurePassword123

# Credentials are read from environment
check_netscaler -C state -o lbvserver
```

**Benefits:**
- **Security**: Credentials not visible in process listings (`ps`, `top`)
- **Convenience**: Set once, use in multiple commands
- **Compatibility**: Works with Icinga 2 `env` attribute and Nagios/systemd environments

#### Complete Python Rewrite
- All 16 check commands from Perl version implemented
- Modern Python 3.8+ codebase
- Type hints and comprehensive documentation
- 336 unit tests with mock-based testing
- Full CI/CD integration with GitHub Actions

#### New Commands
- `ntp` - NTP synchronization monitoring (new in v2)
- `perfdata` - Generic performance data collection (enhanced)
- `matches/matches_not` - String matching (replaces `string/string_not`)

#### Advanced Features
- Regex filtering with `--filter` and `--limit`
- Custom performance data labels with `--label`
- Flexible separators for performance data with `--separator`
- Comprehensive error handling and logging

### Changed

- **Command naming**: `string` → `matches`, `string_not` → `matches_not`
- **Default timeout**: Increased to 15 seconds (was 10 seconds)
- **Exit codes**: More consistent Nagios plugin compliance
- **Performance data**: Improved formatting and labeling
- **Error messages**: More descriptive and actionable

### Improved

- **Test Coverage**: 336 comprehensive unit tests
- **Code Quality**: Linting with ruff, formatting with black, type checking with mypy
- **Documentation**:
  - 14 detailed command usage examples
  - Icinga 2 integration guide with CheckCommand definitions
  - Nagios integration guide with command and service examples
  - Contributing guidelines for developers
- **CI/CD**: Automated testing on Python 3.8, 3.9, 3.10, 3.11, 3.12

### Migration Guide

#### For Existing v1.x Users

1. **Update command invocations** - Remove `-s/--ssl` flags:
   ```diff
   - check_netscaler -H 192.168.1.10 -s -C state -o lbvserver
   + check_netscaler -H 192.168.1.10 -C state -o lbvserver
   ```

2. **Update Nagios/Icinga configs** - Remove `-s` from command definitions:
   ```diff
   define command {
       command_name check_netscaler_state
   -   command_line /usr/bin/check_netscaler -H $HOSTADDRESS$ -s -C state ...
   +   command_line /usr/bin/check_netscaler -H $HOSTADDRESS$ -C state ...
   }
   ```

3. **Update Icinga 2 CheckCommands**:
   ```diff
   template CheckCommand "netscaler-common" {
     arguments = {
   -   "--ssl" = {
   -     set_if = "$netscaler_ssl$"
   +   "--no-ssl" = {
   +     set_if = "$netscaler_no_ssl$"
       }
     }
   - vars.netscaler_ssl = true
   }
   ```

4. **Consider using environment variables** for improved security:
   ```bash
   # In systemd service or shell profile
   export NETSCALER_HOST=192.168.1.10
   export NETSCALER_USER=monitoring
   export NETSCALER_PASS=SecurePassword123
   ```

5. **Update command names** if using deprecated aliases:
   - `string` → `matches`
   - `string_not` → `matches_not`

### Compatibility

- **Python**: 3.8, 3.9, 3.10, 3.11, 3.12
- **NetScaler/ADC**: 11.x, 12.x, 13.x, 14.x
- **NITRO API**: v1 (default), v2 (via `-a v2`)
- **Monitoring Systems**: Nagios, Icinga, Icinga 2, Naemon, Shinken, Sensu

### Known Issues

- SSL certificate verification is currently disabled by default (self-signed certs common)
- `--insecure` flag for explicit SSL verification control planned for future release

---

## [1.x] - Perl Version

See [master branch](../../tree/master) for the legacy Perl implementation and its changelog.
