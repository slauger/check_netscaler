# Mock NITRO API Server

A Flask-based mock server that simulates the NetScaler NITRO REST API for testing purposes.

## Features

- ✅ Full NITRO API authentication (login/logout)
- ✅ Session cookie management
- ✅ Config and Stat endpoints
- ✅ Realistic fixture data (30 resource types)
- ✅ Query parameter support (args, filelocation, filename)
- ✅ Standalone mode or pytest fixture
- ✅ Resource name filtering

## Supported Resource Types

### Tier 1: Core Resources
**Config endpoints:**
- `lbvserver` - Load Balancer virtual servers
- `service` - Backend services
- `servicegroup` - Service groups
- `interface` - Network interfaces
- `sslcertkey` - SSL certificates (with expiry dates)
- `nsconfig` - System configuration
- `nshardware` - Hardware information
- `nsversion` - Version information
- `ntpsync` - NTP sync status
- `ntpstatus` - NTP peer status
- `systemfile` - System files (includes license files)

**Stat endpoints:**
- `lbvserver` - LB statistics
- `service` - Service statistics
- `servicegroup` - ServiceGroup statistics
- `interface` - Interface statistics
- `hanode` - HA cluster statistics

### Tier 2: Extended Resources
**Config + Stat endpoints:**
- `vpnvserver` - VPN virtual servers
- `authenticationvserver` - Authentication vServers
- `csvserver` - Content Switching vServers
- `gslbvserver` - GSLB vServers
- `staserver` - STA (Secure Ticket Authority) servers
- `sslvserver` - SSL vServer bindings

**Config only:**
- `server` - Backend servers
- `nsfeature` - Enabled features

## Usage

### Standalone Mode

Start the mock server on port 8080:

```bash
python -m tests.mocks.nitro_server --port 8080
```

Then test with curl:

```bash
# Login
curl -c cookies.txt -X POST http://localhost:8080/nitro/v1/config/login \\
  -H "Content-Type: application/json" \\
  -d '{"login": {"username": "nsroot", "password": "nsroot"}}'

# Get load balancers
curl -b cookies.txt http://localhost:8080/nitro/v1/config/lbvserver | jq

# Get load balancer stats
curl -b cookies.txt http://localhost:8080/nitro/v1/stat/lbvserver | jq

# Get specific resource
curl -b cookies.txt http://localhost:8080/nitro/v1/config/lbvserver/lb_web | jq

# Get license files
curl -b cookies.txt "http://localhost:8080/nitro/v1/config/systemfile?args=filelocation:/nsconfig/license" | jq
```

### Pytest Fixture

Use in tests with the `mock_nitro_server` fixture:

```python
def test_my_check(mock_nitro_server):
    from check_netscaler.client import NITROClient

    # Get mock server URL
    host, port = mock_nitro_server.host, mock_nitro_server.port

    # Use with real NITRO client
    with NITROClient(hostname=f"{host}:{port}",
                      username="nsroot",
                      password="nsroot",
                      ssl=False) as client:
        data = client.get_config("lbvserver")
        assert "lbvserver" in data
```

### Integration with check_netscaler CLI

Test check_netscaler commands against the mock server:

```bash
# Start mock server
python -m tests.mocks.nitro_server --port 9999 &

# Run checks against it
check_netscaler state -H localhost:9999 --no-ssl -u nsroot -p nsroot \\
  --objecttype lbvserver --objectname lb_web

# Output: NetScaler OK - lb_web: UP

# Check SSL certificates
check_netscaler sslcert -H localhost:9999 --no-ssl -u nsroot -p nsroot \\
  -w 30 -c 10

# Output: NetScaler OK - cert_web expires in 60 days, cert_warning expires in 20 days...

# Kill server
pkill -f nitro_server
```

## Fixture Data

Fixtures are stored as JSON files in `tests/mocks/fixtures/`:

```
fixtures/
├── config/          # Config endpoint responses
│   ├── lbvserver.json
│   ├── service.json
│   ├── servicegroup.json
│   ├── interface.json
│   ├── sslcertkey.json      # With realistic expiry dates
│   ├── nsconfig.json
│   ├── nshardware.json
│   ├── nsversion.json
│   ├── ntpsync.json
│   ├── ntpstatus.json        # With NTP peer response format
│   ├── systemfile.json       # With base64-encoded license
│   ├── vpnvserver.json
│   ├── authenticationvserver.json
│   ├── csvserver.json
│   ├── gslbvserver.json
│   ├── staserver.json
│   ├── sslvserver.json
│   ├── server.json
│   └── nsfeature.json
└── stat/            # Stat endpoint responses
    ├── lbvserver.json
    ├── service.json
    ├── servicegroup.json
    ├── interface.json
    ├── hanode.json
    ├── vpnvserver.json
    ├── authenticationvserver.json
    ├── csvserver.json
    ├── gslbvserver.json
    ├── staserver.json
    └── sslvserver.json
```

### Generating Fixtures

Regenerate all fixtures from templates:

```bash
python tests/mocks/generate_fixtures.py
```

Output:
```
Generating fixtures...
  - service (config + stat)
  - servicegroup (config + stat)
  - interface (config + stat)
  - sslcertkey (config)
  - ...

✅ All fixtures generated!
📁 Total fixtures:
   - config: 19 files
   - stat: 11 files
```

## Authentication

The mock server requires authentication for all API calls (except login/logout):

1. **POST** `/nitro/v1/config/login` with credentials
2. Server returns `NITRO_AUTH_TOKEN` cookie
3. Include cookie in subsequent requests
4. **POST** `/nitro/v1/config/logout` to end session

Default credentials: `nsroot` / `nsroot` (any username/password works)

## Query Parameters

### systemfile (License Check)

Get license files from specific location:

```bash
curl -b cookies.txt "http://localhost:8080/nitro/v1/config/systemfile?args=filelocation:/nsconfig/license"
```

Get specific license file with content:

```bash
curl -b cookies.txt "http://localhost:8080/nitro/v1/config/systemfile?args=filelocation:/nsconfig/license,filename:license.lic"
```

The `systemfile` fixture includes:
- FLEXlm format license content
- Base64-encoded `filecontent`
- INCREMENT lines with feature names and expiry dates
- Supports testing license expiry warnings

## Running Tests

Run the integration test suite:

```bash
# All tests
pytest tests/mocks/test_mock_server.py -v

# Specific test
pytest tests/mocks/test_mock_server.py::test_login_success -v
```

Test coverage:
- ✅ Login/logout authentication
- ✅ Config endpoint (lbvserver)
- ✅ Stat endpoint (lbvserver)
- ✅ Resource name filtering
- ✅ Query parameters (systemfile)
- ✅ NTP status format
- ✅ Unauthenticated requests (401)
- ✅ Non-existent resources (404)

## Development

### Adding New Resource Types

1. Create fixture JSON file in `tests/mocks/fixtures/config/` or `stat/`
2. Follow the NITRO API response format:

```json
{
  "errorcode": 0,
  "message": "Done",
  "severity": "NONE",
  "resourcetype": [
    {
      "name": "resource_name",
      "field1": "value1",
      "field2": "value2"
    }
  ]
}
```

3. The mock server will automatically serve it at:
   - `/nitro/v1/config/resourcetype`
   - `/nitro/v1/stat/resourcetype`

### Extending Query Parameter Support

Add custom parameter parsing in `nitro_server.py`:

```python
def _load_fixture(self, endpoint, resource_type, resource_name, query_params):
    # Add custom handling here
    if resource_type == "myresource" and query_params:
        return self._load_myresource_fixture(query_params)
    # ...
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8080
lsof -i :8080

# Kill it
kill -9 <PID>
```

### Server Not Starting

Check Flask is installed:

```bash
pip install flask
```

### Fixture Not Found (404)

1. Check fixture file exists: `tests/mocks/fixtures/{endpoint}/{resource_type}.json`
2. Verify JSON format is valid: `cat fixtures/config/lbvserver.json | jq`
3. Regenerate fixtures: `python tests/mocks/generate_fixtures.py`

## License

Same as check_netscaler (see repository LICENSE).
