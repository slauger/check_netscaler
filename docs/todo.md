# TODO

Future improvements and enhancements for check_netscaler.

## Testing Improvements

### Integration Tests
- [ ] End-to-end tests with mock NITRO server
- [ ] Complete command integration tests
- [ ] Error scenario coverage
- [ ] Edge case testing

**Context:** Currently all tests use mocked API responses. True integration tests with a mock NITRO HTTP server would provide better coverage.

**Files to create:**
- `tests/integration/test_e2e.py`
- `tests/mocks/nitro_server.py` (optional mock HTTP server)
- `tests/fixtures/` (response data)

## Future Features

### Potential Enhancements
- [ ] Graphite/InfluxDB output format support
- [ ] JSON output mode for automation
- [ ] Bulk operations (check multiple objects in one call)
- [ ] Connection pooling for multiple checks
- [ ] Custom output templates

## Documentation

- [ ] Performance tuning guide
- [ ] Troubleshooting guide with common issues

## Notes

All core functionality (16 commands, 349 tests) is complete and production-ready. Items above are optional enhancements.
