# TODO - Python Rewrite v2.0

This document tracks all tasks for the complete rewrite from Perl to Python.

## 📊 Current Status

**Code:**
- ~3000 lines of Python code
- 195 tests passing
- **9 commands fully implemented: `state`, `above`/`below`, `nsconfig`, `hwinfo`, `sslcert`, `debug`, `servicegroup`, `matches`/`matches_not`, `staserver`**

**Original Perl Script:**
- 1,449 lines of code
- 12 check functions
- 15 different commands

**Progress:** ~60% of commands implemented (9/15)

## 🎯 Implementation Tasks

### Phase 1: Core Infrastructure

#### 1.1 NITRO API Client ✅ DONE
- [x] HTTP client implementation (requests library)
- [x] Session management (login/logout)
- [x] Request handling (GET/POST)
- [x] Error handling and HTTP status codes
- [x] Timeout handling
- [x] SSL/TLS support
- [x] API version routing (v1, v2)
- [x] Endpoint routing (stat vs config)

**Files:**
- ✅ `check_netscaler/client/nitro.py`
- ✅ `check_netscaler/client/session.py`
- ✅ `check_netscaler/client/exceptions.py`

#### 1.2 Nagios Output Formatter ✅ DONE
- [x] Status line formatting (OK, WARNING, CRITICAL, UNKNOWN)
- [x] Performance data formatting (Nagios format)
- [x] Multi-line output support
- [x] Proper exit codes
- [x] Message aggregation for multiple objects

**Files:**
- ✅ `check_netscaler/output/nagios.py`

#### 1.3 Mock NITRO Server
- [ ] Mock HTTP server for testing
- [ ] Response fixtures for all object types
- [ ] Error scenario simulation
- [ ] Fixture data management

**Files to create:**
- `tests/mocks/nitro_server.py`
- `tests/mocks/responses.json`
- `tests/fixtures/` (directory for response data)

---

### Phase 2: Check Commands Implementation

All commands from the Perl script need to be ported to Python.

#### Priority: HIGH

##### 2.1 `state` Command ✅ DONE
**Most important check - 80% of use cases**

- [x] vServer state checking (lbvserver, vpnvserver, gslbvserver, csvserver, sslvserver, authenticationvserver)
- [x] Service state checking
- [x] ServiceGroup state checking
- [x] Server state checking
- [x] State aggregation (UP, DOWN, OUT OF SERVICE, etc.)
- [x] Performance data for active connections
- [x] Filter/limit regex support

**File:** ✅ `check_netscaler/commands/state.py`

##### 2.2 `above` / `below` Commands ✅ DONE
**System resource monitoring**

- [x] Threshold comparison logic
- [x] Support for multiple fields (comma-separated)
- [x] Common checks:
  - CPU usage (cpuusagepcnt, mgmtcpuusagepcnt)
  - Memory usage (memusagepcnt)
  - Disk usage (disk0perusage, disk1perusage)
- [x] Performance data output
- [x] Both above and below modes

**File:** ✅ `check_netscaler/commands/threshold.py`

##### 2.3 `sslcert` Command ✅ DONE
**SSL certificate expiration monitoring**

- [x] Certificate list retrieval
- [x] Expiration date parsing
- [x] Days until expiration calculation
- [x] Warning/Critical threshold comparison
- [x] Filter by certificate name
- [x] Default thresholds (30/10 days)

**File:** ✅ `check_netscaler/commands/sslcert.py`

##### 2.4 `nsconfig` Command ✅ DONE
**Unsaved configuration detection**

- [x] Check for unsaved NS config
- [x] Simple OK/WARNING output
- [x] No thresholds needed

**File:** ✅ `check_netscaler/commands/nsconfig.py`

#### Priority: MEDIUM

##### 2.5 `hastatus` Command
**High Availability monitoring**

- [ ] HA node status retrieval
- [ ] HA state checking (PRIMARY, SECONDARY)
- [ ] Sync status
- [ ] Failover detection

**File:** `check_netscaler/commands/hastatus.py`

##### 2.6 `servicegroup` Command ✅ DONE
**ServiceGroup with member quorum**

- [x] ServiceGroup state
- [x] Member count (total, active)
- [x] Quorum calculation (percentage of active members)
- [x] Warning/Critical thresholds for quorum
- [x] Performance data

**File:** ✅ `check_netscaler/commands/servicegroup.py`

##### 2.7 `interfaces` Command
**Network interface monitoring**

- [ ] Interface state (UP, DOWN)
- [ ] Interface statistics
- [ ] Performance data per interface
- [ ] Filter by interface name/pattern

**File:** `check_netscaler/commands/interfaces.py`

##### 2.8 `perfdata` Command
**Generic performance data collection**

- [ ] Arbitrary field collection
- [ ] Support for multiple fields
- [ ] Object type specification
- [ ] Label support
- [ ] Common use cases:
  - Cache hits/misses
  - TCP connections
  - Network throughput
  - AAA sessions

**File:** `check_netscaler/commands/perfdata.py`

#### Priority: LOW

##### 2.9 `matches` / `matches_not` Commands ✅ DONE
**String matching in API responses**

- [x] Field value retrieval
- [x] String comparison (exact match)
- [x] WARNING/CRITICAL on match/not match
- [x] Support for HA status checks
- [x] Multiple fields support
- [x] Array support with custom labels

**File:** ✅ `check_netscaler/commands/matches.py`

##### 2.10 `hwinfo` Command ✅ DONE
**Hardware information display**

- [x] System information retrieval
- [x] Simple info output (always OK)
- [x] No thresholds

**File:** ✅ `check_netscaler/commands/hwinfo.py`

##### 2.11 `license` Command
**License expiration monitoring**

- [ ] License file reading via systemfile API
- [ ] Expiration date parsing
- [ ] Warning/Critical thresholds
- [ ] Multiple license support

**File:** `check_netscaler/commands/license.py`

##### 2.12 `staserver` Command ✅ DONE
**STA server availability check**

- [x] STA server list retrieval
- [x] Server state checking (staauthid)
- [x] Filter by vServer name
- [x] Global and vServer-specific binding support
- [x] Filter/limit regex support

**File:** ✅ `check_netscaler/commands/staserver.py`

##### 2.13 `ntp` Command
**NTP synchronization status**

- [ ] NTP peer information
- [ ] Offset calculation
- [ ] Jitter calculation
- [ ] Stratum checking
- [ ] Truechimers count
- [ ] Compatible with check_ntp_peer output format

**File:** `check_netscaler/commands/ntp.py`

##### 2.14 `debug` Command ✅ DONE
**Raw API output for debugging**

- [x] Raw JSON output from API
- [x] Support for stat and config endpoints
- [x] Pretty-print JSON
- [x] Always returns OK

**File:** ✅ `check_netscaler/commands/debug.py`

---

### Phase 3: Advanced Features

#### 3.1 Filter/Limit Support
- [ ] Regex filter implementation (`--filter`)
- [ ] Regex limit implementation (`--limit`)
- [ ] Apply to all commands supporting multiple objects

**File:** `check_netscaler/utils/filters.py`

#### 3.2 Label Support
- [ ] Custom label for performance data (`--label`)
- [ ] Use object field as label
- [ ] Default to array index if no label

**Enhancement to:** `check_netscaler/output/perfdata.py`

#### 3.3 Separator Customization
- [ ] Custom separator for perfdata (`--separator`)
- [ ] Default to dot (.)
- [ ] Apply to all perfdata output

**Enhancement to:** `check_netscaler/output/perfdata.py`

---

### Phase 4: Testing & Quality

#### 4.1 Unit Tests
- [ ] NITRO client tests
- [ ] Output formatter tests
- [ ] Each command implementation tests
- [ ] Utility function tests
- [ ] Target: >80% code coverage

**Files:** `tests/test_*.py`

#### 4.2 Integration Tests
- [ ] End-to-end tests with mock server
- [ ] All commands tested
- [ ] Error scenarios
- [ ] Edge cases

**Files:** `tests/integration/test_*.py`

#### 4.3 CI/CD
- [ ] GitHub Actions workflow
- [ ] Test on multiple Python versions (3.8, 3.9, 3.10, 3.11, 3.12)
- [ ] Linting (ruff, black)
- [ ] Type checking (mypy)
- [ ] Coverage reporting

**File:** `.github/workflows/test.yml`

---

### Phase 5: Documentation

#### 5.1 Code Documentation
- [ ] Docstrings for all modules
- [ ] API client documentation
- [ ] Command implementation docs
- [ ] Type hints everywhere

#### 5.2 User Documentation
- [ ] README updates
- [ ] Usage examples for all commands
- [ ] Migration guide from v1.x
- [ ] Troubleshooting guide

#### 5.3 Examples
- [ ] Icinga 2 configuration examples
- [ ] Nagios configuration examples
- [ ] Common use case examples

**Files:** `examples/` directory

---

## 🚀 Recommended Implementation Order

### Sprint 1: Foundation
1. NITRO API Client
2. Nagios Output Formatter
3. Mock Server
4. Basic tests

### Sprint 2: Core Commands
1. `state` command (most important!)
2. `above`/`below` commands
3. Integration tests for core commands

### Sprint 3: Common Commands
1. `sslcert` command
2. `nsconfig` command
3. `hastatus` command
4. `servicegroup` command

### Sprint 4: Advanced Commands
1. `interfaces` command
2. `perfdata` command
3. Filter/Limit support
4. Label/Separator support

### Sprint 5: Remaining Commands
1. `matches`/`matches_not`
2. `hwinfo`
3. `license`
4. `staserver`
5. `ntp`
6. `debug`

### Sprint 6: Polish
1. Complete test coverage
2. CI/CD pipeline
3. Documentation
4. Examples

---

## 📝 Notes

- Original Perl script is in `master` branch for reference
- All new code in `v2-python-rewrite` branch
- Issue #134 tracks overall progress
- No PRs until at least core commands are functional

## 🔗 References

- Issue: https://github.com/slauger/check_netscaler/issues/134
- Branch: `v2-python-rewrite`
- Perl reference: `master` branch `check_netscaler.pl`
