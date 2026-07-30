# license - License Expiration Monitoring


> **Note**: All examples assume environment variables are set:
> ```bash
> export NETSCALER_HOST=192.168.1.10
> export NETSCALER_USER=nsroot
> export NETSCALER_PASS=nsroot
> ```
> See [Environment Variables](../../README.md#using-environment-variables-recommended) for details.

Monitor NetScaler license expiration directly via the NITRO API. Instead of
reading and parsing `*.lic` files, the check queries the appliance's own license
state, which already exposes a computed `daystoexpiration`.

Two resources can be checked. `-o/--objecttype` names the NITRO config resource
to query:

| `-o` value (default `nslicense`) | Reports |
| -------------------------------- | ------- |
| `nslicense` | base platform license: `modelid`, `licensingmode`, `daystoexpiration` |
| `nslaslicense` | LAS / pooled ("ADM") license lease: `status`, `daystoexpiration`, next renewal |

Only the selected resource is queried, so each maps cleanly to its own
Nagios/Icinga service with its own thresholds and perfdata.

## Basic Usage

### Check the base platform license (default)

```bash
check_netscaler -C license
# identical to:
check_netscaler -C license -o nslicense
```

**Output (OK):**
```
OK - license: nslicense modelid=200 mode=LAS (Fixed Bandwidth) expires in 113 days | 'nslicense_daystoexpiration'=113;30;10;;
```

**Output (WARNING):**
```
WARNING - license: nslicense modelid=200 mode=LAS (Fixed Bandwidth) expires in 25 days | 'nslicense_daystoexpiration'=25;30;10;;
```

**Output (CRITICAL):**
```
CRITICAL - license: nslicense modelid=200 mode=LAS (Fixed Bandwidth) expires in 5 days | 'nslicense_daystoexpiration'=5;30;10;;
```

### Check the LAS / pooled license lease

```bash
check_netscaler -C license -o nslaslicense
```

**Output (OK):**
```
OK - license: nslaslicense status=ACTIVE entitlement expires in 546 days (renewal Thu Oct 29 14:33:06 2026) | 'nslaslicense_daystoexpiration'=546;30;10;;
```

A lease whose `status` is not `ACTIVE` is reported **CRITICAL** regardless of the
days remaining.

### Custom thresholds

```bash
check_netscaler -C license -w 60 -c 30
```

**Default thresholds:** `-w 30 -c 10` (30 days warning, 10 days critical).
Thresholds are in **days** and apply to `daystoexpiration`.

## Status Logic

- `daystoexpiration < critical` → **CRITICAL**
- `daystoexpiration < warning` → **WARNING**
- otherwise → **OK**
- `nslaslicense.status != ACTIVE` → **CRITICAL** (overrides days)
- selected resource not returned by the appliance → **UNKNOWN**
- non-numeric `daystoexpiration` → **UNKNOWN**

## Performance Data

```
'nslicense_daystoexpiration'=<days>;<warn>;<crit>;;
'nslaslicense_daystoexpiration'=<days>;<warn>;<crit>;;
```

Only the metric for the selected resource is emitted.

## Common Use Cases

### 1. Platform license, production thresholds

```bash
check_netscaler -C license -o nslicense -w 60 -c 30
```

### 2. Pooled/ADM lease as a separate service

```bash
check_netscaler -C license -o nslaslicense -w 30 -c 10
```

## Exit Codes

- `0` (OK) - selected license valid beyond the warning threshold
- `1` (WARNING) - expiring within the warning threshold
- `2` (CRITICAL) - expiring within the critical threshold, or lease not `ACTIVE`
- `3` (UNKNOWN) - missing thresholds, invalid `-o`, or the resource/value is unavailable

## Notes

- The appliance computes `daystoexpiration`; no local date parsing is involved.
- Appliances without pooled/ADM licensing do not return `nslaslicense`; querying
  it with `-o nslaslicense` on such a system yields UNKNOWN.
- The check monitors expiration only, not individual feature enablement.
