# Architecture - check_netscaler v2.0

This document describes the architecture and design decisions for the Python rewrite.

## 🎯 Design Goals

1. **Maintainability**: Clean, readable Python code with type hints
2. **Testability**: Mock-based testing without requiring NetScaler hardware
3. **Compatibility**: Maintain CLI compatibility with v1.x where possible
4. **Extensibility**: Easy to add new check commands
5. **Standards**: Follow Nagios/Icinga plugin guidelines

## 📁 Project Structure

```
check_netscaler/
├── __init__.py              # Package initialization, version info
├── __main__.py              # CLI entry point
├── cli.py                   # Argument parser and CLI logic
├── constants.py             # Exit codes, defaults, constants
│
├── client/                  # NITRO API client
│   ├── __init__.py
│   ├── nitro.py            # Main NITRO client class
│   ├── session.py          # Session management (login/logout)
│   └── exceptions.py       # Custom exceptions
│
├── commands/               # Check command implementations
│   ├── __init__.py
│   ├── base.py            # Base command class
│   ├── state.py           # State checks
│   ├── sslcert.py         # SSL certificate checks
│   ├── threshold.py       # Above/below threshold checks
│   ├── matches.py         # String matching
│   ├── nsconfig.py        # Config status
│   ├── hastatus.py        # HA status
│   ├── servicegroup.py    # ServiceGroup checks
│   ├── interfaces.py      # Interface checks
│   ├── perfdata.py        # Performance data
│   ├── hwinfo.py          # Hardware info
│   ├── license.py         # License checks
│   ├── staserver.py       # STA server checks
│   ├── ntp.py             # NTP checks
│   └── debug.py           # Debug output
│
├── output/                 # Output formatters
│   ├── __init__.py
│   ├── nagios.py          # Nagios plugin output formatter
│   └── perfdata.py        # Performance data formatter
│
└── utils/                  # Utility functions
    ├── __init__.py
    ├── filters.py         # Regex filter/limit support
    └── helpers.py         # Common helper functions

tests/
├── __init__.py
├── conftest.py            # Pytest fixtures
│
├── mocks/                 # Mock NITRO server
│   ├── __init__.py
│   ├── nitro_server.py   # Mock HTTP server
│   └── responses.json    # Mock response data
│
├── fixtures/              # Test data
│   ├── lbvserver.json
│   ├── service.json
│   └── ...
│
├── test_cli.py           # CLI tests
├── test_constants.py     # Constants tests
├── test_client.py        # NITRO client tests
├── test_output.py        # Output formatter tests
└── test_commands/        # Command tests
    ├── test_state.py
    ├── test_sslcert.py
    └── ...
```

## 🏗️ Core Components

### 1. CLI Layer (`cli.py`)

**Responsibilities:**
- Parse command-line arguments
- Validate input
- Route to appropriate command handler
- Handle top-level errors

**Design:**
- Uses `argparse` for argument parsing
- Maintains backward compatibility with v1.x CLI
- All arguments from Perl version supported

### 2. NITRO API Client (`client/`)

**Responsibilities:**
- HTTP communication with NetScaler NITRO API
- Session management (login/logout)
- Request/response handling
- Error handling

**Design:**
```python
class NITROClient:
    def __init__(self, hostname, username, password, ssl=True, port=None, timeout=15):
        """Initialize NITRO client"""

    def login(self) -> None:
        """Authenticate and get session cookie"""

    def logout(self) -> None:
        """Logout and clear session"""

    def get(self, resource_type: str, resource_name: str = None,
            endpoint: str = "stat") -> dict:
        """GET request to NITRO API"""

    def post(self, resource_type: str, data: dict) -> dict:
        """POST request to NITRO API"""
```

**Key Features:**
- Context manager support (`with NITROClient(...) as client`)
- Automatic login/logout
- Request retry logic
- Proper timeout handling
- SSL certificate validation (optional)

### 3. Command Layer (`commands/`)

**Responsibilities:**
- Implement check logic for each command
- Call NITRO API via client
- Process response data
- Generate status and performance data

**Design:**
```python
class BaseCommand:
    """Base class for all check commands"""

    def __init__(self, client: NITROClient, args: Namespace):
        self.client = client
        self.args = args

    def execute(self) -> CheckResult:
        """Execute the check and return result"""
        raise NotImplementedError


class StateCommand(BaseCommand):
    """Implements 'state' check command"""

    def execute(self) -> CheckResult:
        # Get data from NITRO API
        data = self.client.get(self.args.objecttype, self.args.objectname)

        # Process and evaluate
        result = self._evaluate_state(data)

        # Return structured result
        return CheckResult(
            status=STATE_OK,
            message="All services UP",
            perfdata={"active": 10, "down": 0}
        )
```

**Key Features:**
- All commands inherit from `BaseCommand`
- Consistent interface
- Structured return values
- Easy to add new commands

### 4. Output Layer (`output/`)

**Responsibilities:**
- Format check results for Nagios/Icinga
- Generate performance data strings
- Handle multi-line output

**Design:**
```python
class NagiosOutput:
    """Format output according to Nagios plugin guidelines"""

    @staticmethod
    def format_output(result: CheckResult) -> str:
        """Format final plugin output"""
        # Format: STATUS - message | perfdata

    @staticmethod
    def format_perfdata(data: dict, label: str = None,
                       separator: str = ".") -> str:
        """Format performance data"""
        # Format: 'label'=value[UOM];[warn];[crit];[min];[max]
```

**Nagios Plugin Guidelines:**
- First line: `STATUS - message`
- Optional: `| perfdata`
- Multi-line: Additional info on subsequent lines
- Exit code: 0=OK, 1=WARNING, 2=CRITICAL, 3=UNKNOWN

### 5. Utilities (`utils/`)

**Responsibilities:**
- Common helper functions
- Regex filtering
- Data transformation

**Examples:**
- `apply_filter()` - Regex filtering
- `apply_limit()` - Regex limiting
- `parse_threshold()` - Threshold parsing
- `calculate_days_until()` - Date calculations

## 🔄 Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. CLI Entry Point (__main__.py)                           │
│    - Parse arguments                                        │
│    - Validate required parameters                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. NITRO Client Initialization (client/nitro.py)           │
│    - Create connection                                      │
│    - Login to NetScaler                                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Command Dispatch (cli.py)                               │
│    - Route to appropriate command class                     │
│    - Pass client and arguments                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Command Execution (commands/*.py)                        │
│    - Call NITRO API                                         │
│    - Process response                                       │
│    - Evaluate thresholds                                    │
│    - Generate result                                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Output Formatting (output/nagios.py)                    │
│    - Format status message                                  │
│    - Format performance data                                │
│    - Generate multi-line output if needed                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Exit                                                     │
│    - Print output to stdout                                 │
│    - Return exit code (0-3)                                 │
│    - Logout from NetScaler                                  │
└─────────────────────────────────────────────────────────────┘
```

## 🧪 Testing Strategy

### Unit Tests
- Test each component in isolation
- Mock NITRO API responses
- Test all code paths
- Edge cases and error handling

### Integration Tests
- End-to-end tests with mock NITRO server
- Test complete execution flow
- Test all commands with realistic data
- Error scenarios (timeouts, auth failures, etc.)

### Mock NITRO Server
```python
class MockNITROServer:
    """HTTP server that mimics NetScaler NITRO API"""

    def __init__(self, port: int = 8080):
        self.fixtures = self.load_fixtures()

    def handle_get(self, resource_type: str, resource_name: str = None):
        """Return mock response for GET request"""

    def handle_post(self, endpoint: str, data: dict):
        """Handle POST requests (login, etc.)"""
```

**Fixtures:**
- JSON files with realistic NetScaler responses
- Cover all object types
- Include error scenarios
- Easy to update/extend

## 🔐 Security Considerations

1. **Credentials:**
   - Support environment variables
   - Support config file
   - Warn about default credentials
   - No credentials in logs

2. **SSL/TLS:**
   - Default to HTTPS
   - Certificate validation (with option to disable)
   - Support for custom CA certificates

3. **Session Management:**
   - Automatic logout on exit
   - Session timeout handling
   - Proper cleanup on errors

## 📊 Performance Considerations

1. **Connection Reuse:**
   - Single session per execution
   - Connection pooling via requests library

2. **Parallel Checks:**
   - Future: Support checking multiple objects in parallel
   - Use asyncio or threading

3. **Caching:**
   - Future: Cache API responses for multi-check scenarios
   - TTL-based cache

## 🔄 Migration from v1.x

### CLI Compatibility
- All v1.x arguments supported
- Same command names
- Same output format
- Drop-in replacement

### Breaking Changes
- None intended for basic usage
- Advanced features may differ
- Python 3.8+ required (vs Perl)

### Migration Path
1. Test v2.0 in parallel with v1.x
2. Verify output matches
3. Switch monitoring configs to v2.0
4. Deprecate v1.x

## 🚀 Future Enhancements

1. **JSON Output Mode:**
   - Machine-readable output
   - For automation/integration

2. **Configuration File:**
   - Store connection details
   - Reusable profiles

3. **Batch Mode:**
   - Check multiple objects in one call
   - Aggregate results

4. **Plugin Extensions:**
   - Custom check plugins
   - User-defined commands

5. **Prometheus Exporter:**
   - Export metrics in Prometheus format
   - Long-running exporter mode

## 📚 References

- [Nagios Plugin Guidelines](https://nagios-plugins.org/doc/guidelines.html)
- [NetScaler NITRO API](https://developer-docs.citrix.com/projects/netscaler-nitro-api/)
- [Python Packaging](https://packaging.python.org/)
