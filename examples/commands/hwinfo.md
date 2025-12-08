# hwinfo - Hardware Information


> **Note**: All examples assume environment variables are set:
> ```bash
> export NETSCALER_HOST=192.168.1.10
> export NETSCALER_USER=nsroot
> export NETSCALER_PASS=nsroot
> ```
> See [Environment Variables](../../README.md#using-environment-variables-recommended) for details.

Display NetScaler hardware and software information.

## Basic Usage

```bash
check_netscaler -C hwinfo
```

**Output:**
```
OK: NetScaler VPX: version 13.0-58.30 (build 30)
```

## Information Displayed

The command retrieves and displays:
- Platform type (MPX, VPX, SDX, CPX)
- Model number
- Software version
- Build number

## Use Cases

### 1. Inventory management

Collect hardware information across NetScaler fleet:

```bash
check_netscaler -C hwinfo
```

### 2. Version verification

Verify NetScaler version for compliance or upgrade planning:

```bash
check_netscaler -C hwinfo
```

### 3. Platform identification

Identify whether appliance is physical (MPX), virtual (VPX), or containerized (CPX):

```bash
check_netscaler -C hwinfo
```

## Platform Types

- **MPX** - Physical NetScaler appliance
- **VPX** - Virtual NetScaler appliance (VMware, Hyper-V, KVM, etc.)
- **SDX** - NetScaler SDX platform (multi-tenant)
- **CPX** - Containerized NetScaler (Docker, Kubernetes)

## Example Outputs

### VPX (Virtual Appliance)
```
OK: NetScaler VPX: version 13.0-58.30 (build 30)
```

### MPX (Physical Appliance)
```
OK: NetScaler MPX 5550: version 13.1-21.50 (build 50)
```

### CPX (Container)
```
OK: NetScaler CPX: version 13.0-47.22 (build 22)
```

## No Thresholds

This is an informational command only:
- No warning or critical thresholds
- Always returns OK (unless API error)
- No performance data

## Exit Codes

- `0` (OK) - Information retrieved successfully
- `3` (UNKNOWN) - Cannot retrieve hardware/version information

## Tips

- Useful for documentation and inventory
- Run once per appliance for asset tracking
- Helps identify upgrade candidates
- Can be used to verify deployment types
- Lightweight informational check
- No impact on NetScaler performance
- Combine with other tools for fleet management
- Version format: `major.minor-build.release`
