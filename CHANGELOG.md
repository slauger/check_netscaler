# CHANGELOG

## v2.5.1 (2026-02-09)

### Bug Fixes

* update python-semantic-release/python-semantic-release action to v10 (#153)
### Continuous Integration

* update github actions dependencies (#154)
## v2.5.0 (2026-01-11)

### Features

* add filter and limit support for perfdata and matches commands (#145)
## v2.4.0 (2026-01-09)

### Bug Fixes

* fix ruff linting errors
* fix integration tests and command bugs
### Code Style

* apply black code formatting
### Continuous Integration

* increase pytest verbosity to -vv for better test visibility
* add flask dependency to release workflow
* add flask dependency to PyInstaller workflow
### Documentation

* add objectname example for sslcert command
* link to releases page instead of workflow artifacts
* add information about pre-built binaries
### Features

* add mock NITRO API server for integration testing
### Refactoring

* split integration tests into separate files
### Testing

* add nsconfig, hwinfo, debug tests
* add above/below threshold command tests
## v2.3.1 (2026-01-09)

### Bug Fixes

* use 'context' instead of 'ctx' in changelog template
## v2.3.0 (2026-01-08)

### Bug Fixes

* use 'context' instead of 'ctx' in changelog template
### Continuous Integration

* use custom changelog template to show only commit subject lines
* add SHA256 checksums for binaries
* remove pull_request trigger from workflows, push is sufficient
### Features

* add PyInstaller builds for Linux, macOS, and Windows
## v2.2.1 (2026-01-08)

### Bug Fixes

* use -n for field names to match Perl v1 behavior
### Documentation

* cleanup TODO.md - remove completed v2.0 tasks
* restructure documentation into docs/ directory
* remove hardcoded test count from README
* add backup vServer monitoring examples to integration configs
* standardize binary path across all documentation
* update installation instructions for v2.0 release
## v2.2.0 (2025-12-09)

### Code Style

* Apply black formatting to backup vServer feature
### Documentation

* add backup vserver monitoring examples to state command
### Features

* Add backup vServer monitoring for lbvserver state checks
## v2.1.0 (2025-12-08)

### Bug Fixes

* Remove unused loop variable idx in servicegroup command
### Features

* Add Icinga2-compatible status tags to multiline output
## v2.0.0 (2025-12-08)

### Bug Fixes

* update semantic-release monorepo
### Chores

* Make TestPyPI upload non-blocking in release workflow
* add renovate.json
### Continuous Integration

* explicitly set angular commit parser for semantic-release
* configure semantic-release commit parser options
### Features

* complete rewrite from Perl to Python 3.8+
* remove -s flag for SSL, replaced with --no-ssl
* change default protocol from HTTP to HTTPS
## v1.6.2 (2021-09-27)

### Bug Fixes

* correct interface resource type casing for NITRO API
* measurement should be undef for hapktrxrate and hapkttxrate (#47)
### Chores

* 1.6.2 [skip ci]
* add renovate.json
* add GitHub Sponsors funding and fix linting issues
* add CLAUDE.md and AGENT.md to .gitignore
* remove string 'current branch only' (#58)
* add additional icinga2 example (icinga2_command_advanced.conf) (#59)
### Continuous Integration

* add complete release pipeline with PyPI deployment
* add GitHub Actions CI/CD pipeline and fix code quality issues
* upgrade to node-version 14
### Documentation

* use static MIT license badge
* add status badges to README.md
* replace CHANGELOG.md with MIGRATION.md
* update documentation to reflect 100% completion
* add integration examples and contributing guidelines
* add remaining command examples
* add comprehensive command examples and streamline README
* update TODO.md with Phase 4 completion status
* update README.md with current implementation status
* mark Phase 3 (Advanced Features) as complete
* update TODO.md with threshold command completion
* add TODO and architecture documentation
* fix cmdPolicy for the license check (fixes #83)
### Features

* add environment variable support and make HTTPS default
* add ntp command for NTP synchronization status checking
* add perfdata command for generic performance data collection
* add interfaces command for network interface monitoring
* add license command for license expiration monitoring
* add hastatus command for High Availability monitoring
* implement staserver command
* implement matches/matches_not commands
* implement servicegroup command
* implement debug command
* implement sslcert command
* implement hwinfo command
* implement nsconfig command
* implement above/below threshold commands
* implement state command with Nagios output
* implement NITRO API client
* add Python package structure and core modules
* initial Python rewrite (v2.0)
## v1.6.1 (2020-09-18)

### Bug Fixes

* get host, user and password from environment variables (NETSCALER_HOST, NETSCALER_USERNAME, NETSCALER_PASSWORD)
* add release automation via semantic-release-bot
* add support for limit in more subs
* add --seperator to allow to configure a custom perfdata seperator (#47)
* add limit switch ('--limit', '-l') and change spec for label switch from '-l' to '-L'
* replace hardcoded id with $plugin->opts->label
* add the ability to set a custom perfdata label for sub check_keyword and check_threshold_and_get_perfdata (#56)
### Chores

* 1.6.1 [skip ci]
* add more advanced tests
* additional tests for advanced switches
* replace NETSCALER_IP with NETSCALER_HOST in our tests
* run perltidy
* run perltidy
* add docs for advanced switches
## v1.6.0 (2019-10-04)

### Bug Fixes

* perltidy broke the file permissions for check_netscaler.pl
## v1.5.1 (2018-06-10)

## v1.5.0 (2018-03-10)

## v1.4.0 (2017-08-20)

## v1.3.0 (2017-08-13)

## v1.2.0 (2017-08-12)

## v1.1.1 (2017-06-11)

## v1.1.0 (2017-05-13)

## v1.0.0 (2017-02-02)
