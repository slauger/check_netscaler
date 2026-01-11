# matches / matches_not - String Matching Checks


> **Note**: All examples assume environment variables are set:
> ```bash
> export NETSCALER_HOST=192.168.1.10
> export NETSCALER_USER=nsroot
> export NETSCALER_PASS=nsroot
> ```
> See [Environment Variables](../../README.md#using-environment-variables-recommended) for details.

Check if API field values match (or don't match) expected strings.

## Basic Usage

### matches - Alert when value EQUALS keyword

```bash
check_netscaler -C matches -o hanode -n hacurstate -w UP -c DOWN
```

**Logic:**
- CRITICAL if value = "DOWN"
- WARNING if value = "UP"
- OK otherwise

### matches_not - Alert when value DOES NOT EQUAL keyword

```bash
check_netscaler -C matches_not -o hanode -n hacurmasterstate -w SECONDARY -c PRIMARY
```

**Logic:**
- CRITICAL if value ≠ "PRIMARY"
- WARNING if value ≠ "SECONDARY"
- OK if value = "PRIMARY" or "SECONDARY"

## Syntax

```bash
# matches: value EQUALS keyword → alert
check_netscaler -C matches -o <objecttype> -n <field> -w <warn_keyword> -c <crit_keyword>

# matches_not: value NOT EQUALS keyword → alert
check_netscaler -C matches_not -o <objecttype> -n <field> -w <warn_keyword> -c <crit_keyword>
```

## Advanced Usage

### Multiple fields

```bash
check_netscaler -C matches -o hanode \
  -n hacurstate,hacurmasterstate \
  -w "UP,SECONDARY" \
  -c "DOWN,UNKNOWN"
```

Checks multiple fields against keywords.

### Arrays with labels

```bash
check_netscaler -C matches -o service \
  -n state \
  -w "OUT OF SERVICE" \
  -c DOWN \
  --label name
```

Checks field in multiple objects, uses `name` field for labeling.

### Custom separator

```bash
check_netscaler -C matches -o hanode -n hacurstate -w UP -c DOWN --separator "_"
```

### Filter and limit objects (for multiple objects)

Filter out specific objects (exclude matching):
```bash
# Exclude test services
check_netscaler -C matches -o service \
  -n state \
  -w "OUT OF SERVICE" \
  -c DOWN \
  --label name \
  --filter "test"
```

Limit to specific objects (include only matching):
```bash
# Only production services
check_netscaler -C matches -o service \
  -n state \
  -w "OUT OF SERVICE" \
  -c DOWN \
  --label name \
  --limit "prod"
```

Combine filter and limit:
```bash
# Only production services, exclude API services
check_netscaler -C matches -o service \
  -n state \
  -w "OUT OF SERVICE" \
  -c DOWN \
  --label name \
  --limit "prod" \
  --filter "api"
```

## Use Cases

### 1. HA Master State

```bash
# Alert if node is not PRIMARY
check_netscaler -C matches_not -o hanode \
  -n hacurmasterstate \
  -w SECONDARY \
  -c PRIMARY
```

### 2. Service State

```bash
# Alert if service state matches problem states
check_netscaler -C matches -o service \
  -n state \
  -w "OUT OF SERVICE" \
  -c DOWN \
  --objectname web_svc_01
```

### 3. Configuration Validation

```bash
# Check if setting has expected value
check_netscaler -C matches_not -o nsparam \
  -n httponlycookieflag \
  -w "" \
  -c ENABLED
```

Critical if not ENABLED.

### 4. Multiple Services

```bash
check_netscaler -C matches -o service \
  -n state \
  -w "GOING OUT OF SERVICE" \
  -c DOWN \
  --label name
```

## matches vs matches_not

### matches (equals)
Use when you want to alert ON a specific value:
- "Alert me when state = DOWN"
- "Alert me when status = FAILED"

### matches_not (not equals)
Use when you want to alert when value is NOT expected:
- "Alert me when state ≠ UP"
- "Alert me when master ≠ PRIMARY"

## Performance Data

Single object:
```
| objecttype.field="value"
```

Multiple objects with label:
```
| objectname.field="value1" objectname2.field="value2"
```

## Exit Codes

### matches
- `0` (OK) - Value does NOT match warning or critical keywords
- `1` (WARNING) - Value EQUALS warning keyword
- `2` (CRITICAL) - Value EQUALS critical keyword
- `3` (UNKNOWN) - Cannot retrieve data or field missing

### matches_not
- `0` (OK) - Value EQUALS warning or critical keyword (as expected)
- `1` (WARNING) - Value DOES NOT EQUAL warning keyword
- `2` (CRITICAL) - Value DOES NOT EQUAL critical keyword
- `3` (UNKNOWN) - Cannot retrieve data or field missing

## Tips

- `matches` = "alert when value IS this"
- `matches_not` = "alert when value is NOT this"
- String matching is exact (case-sensitive)
- Use for checking specific states or configuration values
- Combine with `--label` for meaningful output with arrays
- Use `--separator` to customize perfdata labels
- Use `--filter` to exclude objects matching a regex pattern (when checking multiple objects)
- Use `--limit` to include only objects matching a regex pattern (when checking multiple objects)
- Query NetScaler API to find available fields
- Use `debug` command to see raw API response first
