# ntp - NTP Synchronization Monitoring


> **Note**: All examples assume environment variables are set:
> ```bash
> export NETSCALER_HOST=192.168.1.10
> export NETSCALER_USER=nsroot
> export NETSCALER_PASS=nsroot
> ```
> See [Environment Variables](../../README.md#using-environment-variables-recommended) for details.

Monitor NTP synchronization status on NetScaler (compatible with check_ntp_peer format).

## Basic Usage

### Check NTP synchronization

```bash
check_netscaler -C ntp
```

**Output (OK):**
```
OK: NTP OK: offset=0.0234s, jitter=12ms, stratum=2, truechimers=4 | offset=0.0234s jitter=12ms stratum=2 truechimers=4
```

**Output (WARNING):**
```
WARNING: offset=0.042s (above 0.03s) | offset=0.042s;0.03;0.05 jitter=15ms stratum=2 truechimers=4
```

**Output (CRITICAL):**
```
CRITICAL: Sync DISABLED
```

## Threshold Format

Thresholds use comma-separated key=value pairs:

```
o=offset,s=stratum,j=jitter,t=truechimers
```

**Keys:**
- `o` - Offset in seconds (e.g., 0.03 = 30ms)
- `s` - Stratum level (1-16)
- `j` - Jitter in milliseconds
- `t` - Truechimers count (number of valid peers)

## Basic Thresholds

### Default check with offset only

```bash
check_netscaler -C ntp -w "o=0.03" -c "o=0.05"
```

- WARNING if offset > 30ms
- CRITICAL if offset > 50ms

### Check all metrics

```bash
check_netscaler -C ntp \
  -w "o=0.03,s=2,j=100,t=3" \
  -c "o=0.05,s=3,j=200,t=2"
```

**Thresholds:**
- Offset: WARN >30ms, CRIT >50ms
- Stratum: WARN >2, CRIT >3
- Jitter: WARN >100ms, CRIT >200ms
- Truechimers: WARN ≤3, CRIT ≤2

## NTP Metrics Explained

### Offset
Time difference between system clock and NTP time.
- Typical: <30ms
- WARNING: 30-50ms
- CRITICAL: >50ms

### Jitter
Variation in offset over time (clock stability).
- Typical: <50ms
- WARNING: 50-100ms
- CRITICAL: >100ms

### Stratum
Distance from reference clock (lower is better).
- 1: Reference clock (GPS, atomic)
- 2: Primary server (synced to stratum 1)
- 3+: Secondary servers
- 16: Unsynchronized

### Truechimers
Number of valid NTP peers being used.
- Peers marked with *, +, or - in ntpq output
- More truechimers = more reliable synchronization
- Minimum recommended: 3-4

## Advanced Usage

### Strict offset monitoring

```bash
check_netscaler -C ntp -w "o=0.01" -c "o=0.02"
```

Very tight offset requirements (10ms/20ms).

### Stratum monitoring only

```bash
check_netscaler -C ntp -w "s=2" -c "s=3"
```

Alert if stratum is too high.

### Complete monitoring

```bash
check_netscaler -C ntp \
  -w "o=0.03,s=2,j=100,t=4" \
  -c "o=0.05,s=3,j=200,t=2"
```

## Synchronization States

### Sync Enabled
- **Offset**: Time difference in seconds
- **Jitter**: Clock stability in milliseconds
- **Stratum**: Distance from reference
- **Truechimers**: Valid peer count

### Sync Disabled or Not Synchronized
- Returns CRITICAL immediately
- No metrics available

## Performance Data

```
| offset=<seconds>s;<warn>;<crit> jitter=<ms>ms stratum=<level> truechimers=<count>
```

Example:
```
| offset=0.0234s;0.03;0.05 jitter=12ms;100;200 stratum=2;2;3 truechimers=4;3;2
```

## Common Use Cases

### 1. Basic offset monitoring

```bash
check_netscaler -C ntp -w "o=0.03" -c "o=0.05"
```

### 2. Recommended full monitoring

```bash
check_netscaler -C ntp \
  -w "o=0.03,s=2,j=100,t=3" \
  -c "o=0.05,s=3,j=200,t=2"
```

### 3. Strict requirements

```bash
check_netscaler -C ntp \
  -w "o=0.01,s=1,j=50,t=4" \
  -c "o=0.02,s=2,j=100,t=3"
```

## Exit Codes

- `0` (OK) - NTP synchronized, all thresholds within limits
- `1` (WARNING) - One or more metrics exceed warning threshold
- `2` (CRITICAL) - Sync disabled/not synchronized OR critical threshold exceeded
- `3` (UNKNOWN) - Cannot retrieve NTP status or API error

## Tips

- Start with basic offset monitoring: `-w "o=0.03" -c "o=0.05"`
- Add jitter and stratum for comprehensive monitoring
- Truechimers count indicates peer reliability
- NTP sync must be ENABLED on NetScaler
- Compatible with check_ntp_peer output format
- Offset is converted from milliseconds to seconds automatically
- Use multiple NTP servers (3-4) for best reliability
