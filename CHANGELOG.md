# CHANGELOG

## v2.2.0 (2025-12-09)

### Documentation

* docs: add backup vserver monitoring examples to state command ([`507d295`](https://github.com/slauger/check_netscaler/commit/507d295c5161c8dab14ee7fb656c86b9de6ae35b))

### Feature

* feat: Add backup vServer monitoring for lbvserver state checks

Add --check-backup flag to monitor backup vServer status in lbvserver
state checks. When a backup vServer is active, the check can be
configured to return WARNING or CRITICAL status.

Features:
- Optional --check-backup [warning|critical] flag
- Only active for lbvserver objecttype
- Checks /config endpoint for backupvserverstatus field
- Adds backup status to message and long_output
- Fully backward compatible (opt-in feature)

Tests:
- 6 new tests covering all backup scenarios
- All 349 tests passing

Closes #133 ([`2df236e`](https://github.com/slauger/check_netscaler/commit/2df236e7958710671649ad2fe84e7bf02ed526a3))

### Style

* style: Apply black formatting to backup vServer feature ([`ce3dd58`](https://github.com/slauger/check_netscaler/commit/ce3dd58390c645c0ad0c6384cf42566690daa178))

### Unknown

* Merge pull request #138 from slauger/feature/backup-vserver-check

feat: Add backup vServer monitoring for lbvserver state checks ([`884a7c9`](https://github.com/slauger/check_netscaler/commit/884a7c90301a52ab8422651d580a5a26c02edabd))

## v2.1.0 (2025-12-08)

### Feature

* feat: Add Icinga2-compatible status tags to multiline output

Add [OK], [WARNING], and [CRITICAL] status tags to long_output in
state, servicegroup, and sslcert commands. These tags enable automatic
color-coding in Icinga Web 2 for improved visibility of issues.

Changes:
- state: Add status tags to each object&#39;s state line
- servicegroup: Add status tags to member health details
- sslcert: Add status tags to certificate expiration warnings

This implements the feature requested in issue #28 for better
multiline output formatting in Icinga Web 2.

Refs: #28 ([`4dc7454`](https://github.com/slauger/check_netscaler/commit/4dc7454441ffe288f7e2dd3990b5717c4342e0a1))

### Fix

* fix: Remove unused loop variable idx in servicegroup command

Remove unused enumerate index to fix ruff B007 linting error. ([`a1b6315`](https://github.com/slauger/check_netscaler/commit/a1b631512354832f162985b15c4b61531734e425))

### Unknown

* Merge pull request #137 from slauger/feature/icinga-status-tags

feat: Add Icinga2-compatible status tags to multiline output ([`05bf4bb`](https://github.com/slauger/check_netscaler/commit/05bf4bb66205e70cdbf7cff587b7b00888d93418))

## v2.0.0 (2025-12-08)

### Breaking

* feat!: complete rewrite from Perl to Python 3.8+ ([`81652c9`](https://github.com/slauger/check_netscaler/commit/81652c9f2cbd73cea4da8f29d43a08969702ceaa))

* feat!: remove -s flag for SSL, replaced with --no-ssl ([`3745e66`](https://github.com/slauger/check_netscaler/commit/3745e662ee6ce6bf8dd5bb6111ff32b0bad35d3a))

* feat!: change default protocol from HTTP to HTTPS ([`ad578d8`](https://github.com/slauger/check_netscaler/commit/ad578d81ec377c574b2324f849f27416f1d02697))

### Chore

* chore: Make TestPyPI upload non-blocking in release workflow

TestPyPI upload failures should not block the production PyPI upload.
This change makes the TestPyPI job optional by adding continue-on-error
and removing it as a dependency for the PyPI upload job.

Reason: TestPyPI has strict file-name-reuse policies that can block
uploads of previously deleted versions, but this should not prevent
production releases. ([`c38f3c1`](https://github.com/slauger/check_netscaler/commit/c38f3c1fd020771a733a63daa9ced185d17b9352))

* chore(deps): add renovate.json ([`bbee674`](https://github.com/slauger/check_netscaler/commit/bbee674b15a6aa76c5522385bd0b8d29a4e5614f))

### Ci

* ci: explicitly set angular commit parser for semantic-release ([`a9e06a8`](https://github.com/slauger/check_netscaler/commit/a9e06a850b29ea75d820cb8accb723db97f1068a))

* ci: configure semantic-release commit parser options ([`a8a6929`](https://github.com/slauger/check_netscaler/commit/a8a6929b7c32a56beb8d9f2d229ba5a0df3ccc20))

### Fix

* fix(deps): update semantic-release monorepo ([`616542d`](https://github.com/slauger/check_netscaler/commit/616542d99d98182a40794257fd00ba9d302f50dd))

### Unknown

* Merge pull request #136 from slauger/v2-python-rewrite

Python Rewrite v2.0 - Complete - fixes #134 ([`e3e39a4`](https://github.com/slauger/check_netscaler/commit/e3e39a43ade3283f0f11b974af3bd23e24425f0e))

* Merge branch &#39;master&#39; into v2-python-rewrite ([`d009986`](https://github.com/slauger/check_netscaler/commit/d00998695a9741363a00f9e1825a9e50700d081f))

* Merge pull request #97 from slauger/dependabot/npm_and_yarn/semantic-release/git-10.0.1

Bump @semantic-release/git from 9.0.1 to 10.0.1 ([`e24f3c2`](https://github.com/slauger/check_netscaler/commit/e24f3c2276a2c03b495e5cc022eacae39aa93c8d))

* Bump @semantic-release/git from 9.0.1 to 10.0.1

Bumps [@semantic-release/git](https://github.com/semantic-release/git) from 9.0.1 to 10.0.1.
- [Release notes](https://github.com/semantic-release/git/releases)
- [Commits](https://github.com/semantic-release/git/compare/v9.0.1...v10.0.1)

---
updated-dependencies:
- dependency-name: &#34;@semantic-release/git&#34;
  dependency-type: direct:production
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt; ([`e4a77bf`](https://github.com/slauger/check_netscaler/commit/e4a77bf3d75784f160fabbafd6ae04bbc253b4a1))

* Merge pull request #108 from slauger/renovate/major-semantic-release-monorepo

fix(deps): update semantic-release monorepo (major) ([`2224067`](https://github.com/slauger/check_netscaler/commit/2224067afa95b799e3260cb6b4146475012938f6))

* Merge pull request #104 from slauger/dependabot/npm_and_yarn/semantic-release-19.0.3

Bump semantic-release from 18.0.0 to 19.0.3 ([`fb45faf`](https://github.com/slauger/check_netscaler/commit/fb45faff44afa5689d972f7b76a65ec113479dbf))

* Bump semantic-release from 18.0.0 to 19.0.3

Bumps [semantic-release](https://github.com/semantic-release/semantic-release) from 18.0.0 to 19.0.3.
- [Release notes](https://github.com/semantic-release/semantic-release/releases)
- [Commits](https://github.com/semantic-release/semantic-release/compare/v18.0.0...v19.0.3)

---
updated-dependencies:
- dependency-name: semantic-release
  dependency-type: direct:production
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt; ([`083789f`](https://github.com/slauger/check_netscaler/commit/083789f1acc9a7880115082d2be36726e980eee6))

* Merge pull request #109 from slauger/dependabot/npm_and_yarn/semantic-release/github-8.0.5

Bump @semantic-release/github from 7.2.3 to 8.0.5 ([`0913f56`](https://github.com/slauger/check_netscaler/commit/0913f56da396417815db1b191a80b01a3687001c))

* Bump @semantic-release/github from 7.2.3 to 8.0.5

Bumps [@semantic-release/github](https://github.com/semantic-release/github) from 7.2.3 to 8.0.5.
- [Release notes](https://github.com/semantic-release/github/releases)
- [Commits](https://github.com/semantic-release/github/compare/v7.2.3...v8.0.5)

---
updated-dependencies:
- dependency-name: &#34;@semantic-release/github&#34;
  dependency-type: direct:production
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt; ([`0b0dc8c`](https://github.com/slauger/check_netscaler/commit/0b0dc8c2dbaa3978f94eac0581e67899dda9baa6))

* Merge pull request #105 from slauger/renovate/configure

Configure Renovate ([`fcb90a3`](https://github.com/slauger/check_netscaler/commit/fcb90a3eea3662100523030b0f18f832b503d8c7))

## v1.6.2 (2021-09-27)

### Chore

* chore(release): 1.6.2 [skip ci]

## [1.6.2](https://github.com/slauger/check_netscaler/compare/v1.6.1...v1.6.2) (2021-09-27)

### Bug Fixes

* measurement should be undef for hapktrxrate and hapkttxrate ([#47](https://github.com/slauger/check_netscaler/issues/47)) ([1c721dd](https://github.com/slauger/check_netscaler/commit/1c721dd4e6f940a409b1b0c8c20af5a3d5a13bb4)) ([`ae71599`](https://github.com/slauger/check_netscaler/commit/ae7159998ac146d860e8fd82123fb15b488dfe69))

* chore(deps): add renovate.json ([`70cec44`](https://github.com/slauger/check_netscaler/commit/70cec441cbab76d3b072edcd46b1590b91d7bfad))

* chore: add GitHub Sponsors funding and fix linting issues ([`50f3791`](https://github.com/slauger/check_netscaler/commit/50f37913529af5ab9f444826527c7de8ac8fb408))

* chore: add CLAUDE.md and AGENT.md to .gitignore ([`7271517`](https://github.com/slauger/check_netscaler/commit/727151782e81112532dd77177b55ce2d2a08f1be))

* chore(docs): remove string &#39;current branch only&#39; (#58) ([`3948c2c`](https://github.com/slauger/check_netscaler/commit/3948c2cbc584cecfe999c41ecf0588000a3f4732))

* chore: add additional icinga2 example (icinga2_command_advanced.conf) (#59) ([`8759a02`](https://github.com/slauger/check_netscaler/commit/8759a021d52c7fcb467d772635731ebea1560ae4))

### Ci

* ci: add complete release pipeline with PyPI deployment ([`8cc3a8d`](https://github.com/slauger/check_netscaler/commit/8cc3a8d465edbc8373b113f012bca0caa0a3f0e2))

* ci: add GitHub Actions CI/CD pipeline and fix code quality issues ([`26ab7fe`](https://github.com/slauger/check_netscaler/commit/26ab7feddb6f3580bcd1de2c738ac0aeec0d4533))

* ci: upgrade to node-version 14 ([`c9d41d6`](https://github.com/slauger/check_netscaler/commit/c9d41d615c6152f0d2020872a3279fe01208a044))

### Documentation

* docs: use static MIT license badge ([`cd7caef`](https://github.com/slauger/check_netscaler/commit/cd7caef5181a7a27ac07b0a252f42db55607e728))

* docs: add status badges to README.md ([`95a3d44`](https://github.com/slauger/check_netscaler/commit/95a3d44e72ae935efb47c24014eee36684077542))

* docs: replace CHANGELOG.md with MIGRATION.md ([`17de308`](https://github.com/slauger/check_netscaler/commit/17de308840325e0ac446b466670b9135aa5c2da3))

* docs: update documentation to reflect 100% completion ([`06dc4a8`](https://github.com/slauger/check_netscaler/commit/06dc4a8f6dd3f7f37280e4c401018faf39842c63))

* docs: add integration examples and contributing guidelines ([`a879771`](https://github.com/slauger/check_netscaler/commit/a8797715a04fb1b8c949710cc062f2d0e15ba36b))

* docs: add remaining command examples ([`d82a0d6`](https://github.com/slauger/check_netscaler/commit/d82a0d62ac936660d1446e4a594a111f4bf01382))

* docs: add comprehensive command examples and streamline README ([`1f293b7`](https://github.com/slauger/check_netscaler/commit/1f293b79e921e63dc71893d022f7e44842191f99))

* docs: update TODO.md with Phase 4 completion status ([`390ae3e`](https://github.com/slauger/check_netscaler/commit/390ae3e2ba1bf6105689db35c801d23399188db8))

* docs: update README.md with current implementation status ([`c1af583`](https://github.com/slauger/check_netscaler/commit/c1af58389fa6c47297e99595a1688f6b6b4482ff))

* docs: mark Phase 3 (Advanced Features) as complete ([`18c9a50`](https://github.com/slauger/check_netscaler/commit/18c9a5060f3d05791d3054930ae2b189dd4d1aae))

* docs: update TODO.md with threshold command completion ([`441c0cd`](https://github.com/slauger/check_netscaler/commit/441c0cd5b6c6848007e6bdec73e78071a32dd996))

* docs: add TODO and architecture documentation ([`09d2faf`](https://github.com/slauger/check_netscaler/commit/09d2faffacd1cc77a2da1909d6ba6d1c76f52e4b))

* docs(README.md): fix cmdPolicy for the license check (fixes #83) ([`c0628ef`](https://github.com/slauger/check_netscaler/commit/c0628efea78e1bfdff4f014e13ef9770f51a6f05))

### Feature

* feat: add environment variable support and make HTTPS default ([`7fd8227`](https://github.com/slauger/check_netscaler/commit/7fd8227987bdcddd9a4d6f067257a3146852b24f))

* feat: add ntp command for NTP synchronization status checking ([`5050e74`](https://github.com/slauger/check_netscaler/commit/5050e74ef21b62029b732f8d2a8e24ec2b064358))

* feat: add perfdata command for generic performance data collection ([`6e43586`](https://github.com/slauger/check_netscaler/commit/6e435868a804202e696f7429799b7b27f5abe42b))

* feat: add interfaces command for network interface monitoring ([`fade2f2`](https://github.com/slauger/check_netscaler/commit/fade2f2af15f01fe8f3e9b428f20b1e0a54f63fb))

* feat: add license command for license expiration monitoring ([`7e5a938`](https://github.com/slauger/check_netscaler/commit/7e5a938814e5785d4c8111a895a5d796247492f7))

* feat: add hastatus command for High Availability monitoring ([`4dc6496`](https://github.com/slauger/check_netscaler/commit/4dc649629075b743bfbba5892cfa7ab4d63ce32b))

* feat: implement staserver command ([`7efd837`](https://github.com/slauger/check_netscaler/commit/7efd837427fb98ad91e41c766081c6016958d4e2))

* feat: implement matches/matches_not commands ([`d7ebec8`](https://github.com/slauger/check_netscaler/commit/d7ebec8be5f21214e7b8a381ef05cad38f9abe57))

* feat: implement servicegroup command ([`8c662a7`](https://github.com/slauger/check_netscaler/commit/8c662a7ec3d27463e1a6469c6eea618bacbd4ed3))

* feat: implement debug command ([`558e6ce`](https://github.com/slauger/check_netscaler/commit/558e6cedf0a97a85259dc8f1264d1c2d954a7861))

* feat: implement sslcert command ([`8f96148`](https://github.com/slauger/check_netscaler/commit/8f961480623a23f68a43298c061ca9b8eabbe3ad))

* feat: implement hwinfo command ([`eeb10e2`](https://github.com/slauger/check_netscaler/commit/eeb10e25b458ccf6d1a33be658b085c6e30f4b1e))

* feat: implement nsconfig command ([`16f6c8a`](https://github.com/slauger/check_netscaler/commit/16f6c8a50c5c60b419b5f841eeb56e1760455347))

* feat: implement above/below threshold commands

Add threshold monitoring for system resources:
- Above command: alerts when values exceed thresholds
- Below command: alerts when values fall below thresholds
- Support for multiple fields (comma-separated)
- Individual field evaluation with aggregated status
- Performance data for all checked metrics

Common use cases:
- CPU monitoring: cpuusagepcnt, mgmtcpuusagepcnt
- Memory monitoring: memusagepcnt
- Disk monitoring: disk0perusage, disk1perusage
- ServiceGroup quorum: activemembers

Features:
- Single or multiple field checks
- Proper CRITICAL &gt; WARNING precedence
- Long output for multi-field checks
- Thresholds displayed in output

Tests: 21 new tests (73 total passing)

Example usage:
  check_netscaler -H ns -s -C above -o system -n cpuusagepcnt -w 75 -c 90
  check_netscaler -H ns -s -C above -o system -n cpuusagepcnt,memusagepcnt -w 75 -c 90
  check_netscaler -H ns -s -C below -o servicegroup -n activemembers -w 5 -c 2 ([`0953104`](https://github.com/slauger/check_netscaler/commit/0953104449277f1a02bdf79a7812eedadf858025))

* feat: implement state command with Nagios output

Add complete state monitoring implementation:
- Base command class for all checks
- Nagios/Icinga output formatter with perfdata
- State command for vServer/service/servicegroup/server
- Support for filter and limit regex patterns
- Aggregated status reporting with long output
- Performance data for all state checks

Features:
- Checks UP/DOWN/OUT OF SERVICE states
- Returns OK/WARNING/CRITICAL/UNKNOWN appropriately
- Shows problematic objects in message (up to 5)
- Long output with all object states
- Filter/limit support for selective monitoring

Tests: 13 new tests for state command (52 total passing)

Example output:
  OK - All 3 lbvserver are UP | &#39;total&#39;=3;; &#39;ok&#39;=3;;
  CRITICAL - 1/5 service CRITICAL (svc_db) | &#39;total&#39;=5;; ([`c6a0908`](https://github.com/slauger/check_netscaler/commit/c6a09081a52c5a303543dc48c748e6ad19c2e530))

* feat: implement NITRO API client

Add complete NITRO REST API client implementation:
- Session management with login/logout
- HTTP/HTTPS support with custom ports
- GET requests for stat and config endpoints
- Comprehensive error handling and custom exceptions
- Context manager support for automatic cleanup
- SSL certificate validation (configurable)
- Request timeout handling

Tests: 17 new tests for client (40 total passing) ([`ba025ee`](https://github.com/slauger/check_netscaler/commit/ba025ee2b6dbe8163ee1c2ad3d890155f18d4fed))

* feat: add Python package structure and core modules

Add the complete Python package with CLI implementation:
- CLI entry point and argument parser
- Nagios/Icinga exit codes and constants
- Package structure (client, commands, output, utils)
- Update .gitignore to include Python package

All 23 CLI tests passing. ([`5d3c149`](https://github.com/slauger/check_netscaler/commit/5d3c149ee6df820730f31d7b4c25fc9302447823))

* feat: initial Python rewrite (v2.0)

Complete rewrite from Perl to Python 3.8+ with modern architecture.

Changes:
- Replace Perl implementation with Python package structure
- Add CLI argument parser with all v1.x options
- Implement Nagios/Icinga exit codes and constants
- Add pytest test suite (23 tests passing)
- Switch to MIT license for clean rewrite
- Add pyproject.toml for modern Python packaging
- Configure Renovate for Python dependencies
- Remove old Perl build tools and test infrastructure

This is the foundation for v2.0 with mock-based testing. ([`90803ec`](https://github.com/slauger/check_netscaler/commit/90803ec5d0c206cd790a3b9f33c61c9712d12744))

### Fix

* fix: correct interface resource type casing for NITRO API ([`49b8efd`](https://github.com/slauger/check_netscaler/commit/49b8efdb6c91b90b1e3c79e5bbaabc2c97555105))

* fix: measurement should be undef for hapktrxrate and hapkttxrate (#47) ([`1c721dd`](https://github.com/slauger/check_netscaler/commit/1c721dd4e6f940a409b1b0c8c20af5a3d5a13bb4))

### Unknown

* Merge pull request #93 from slauger/dependabot/npm_and_yarn/semantic-release-18.0.0

Bump semantic-release from 17.4.7 to 18.0.0 ([`d770ba7`](https://github.com/slauger/check_netscaler/commit/d770ba75a2cb90af12f3e907b34768e9764f6057))

* Bump semantic-release from 17.4.7 to 18.0.0

Bumps [semantic-release](https://github.com/semantic-release/semantic-release) from 17.4.7 to 18.0.0.
- [Release notes](https://github.com/semantic-release/semantic-release/releases)
- [Commits](https://github.com/semantic-release/semantic-release/compare/v17.4.7...v18.0.0)

---
updated-dependencies:
- dependency-name: semantic-release
  dependency-type: direct:production
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt; ([`0a74c59`](https://github.com/slauger/check_netscaler/commit/0a74c5944c512237babdbe072639e58d6c8e6508))

* Merge pull request #90 from slauger/dependabot/npm_and_yarn/semantic-release-17.4.7

Bump semantic-release from 17.2.3 to 17.4.7 ([`673bc7b`](https://github.com/slauger/check_netscaler/commit/673bc7b8acf7bc88d411965c15918fc072d8708f))

* Bump semantic-release from 17.2.3 to 17.4.7

Bumps [semantic-release](https://github.com/semantic-release/semantic-release) from 17.2.3 to 17.4.7.
- [Release notes](https://github.com/semantic-release/semantic-release/releases)
- [Commits](https://github.com/semantic-release/semantic-release/compare/v17.2.3...v17.4.7)

---
updated-dependencies:
- dependency-name: semantic-release
  dependency-type: direct:production
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt; ([`6f31903`](https://github.com/slauger/check_netscaler/commit/6f319039d804c2915017513dfc263b303da93dfd))

* Merge pull request #91 from slauger/dependabot/npm_and_yarn/semantic-release/git-9.0.1

Bump @semantic-release/git from 9.0.0 to 9.0.1 ([`65721ed`](https://github.com/slauger/check_netscaler/commit/65721edd2e074d9e5c83ddc4dc70e38c3640c0c3))

* Bump @semantic-release/git from 9.0.0 to 9.0.1

Bumps [@semantic-release/git](https://github.com/semantic-release/git) from 9.0.0 to 9.0.1.
- [Release notes](https://github.com/semantic-release/git/releases)
- [Commits](https://github.com/semantic-release/git/compare/v9.0.0...v9.0.1)

---
updated-dependencies:
- dependency-name: &#34;@semantic-release/git&#34;
  dependency-type: direct:production
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt; ([`e76a171`](https://github.com/slauger/check_netscaler/commit/e76a171267d595edd9aa02ead9424a2766b36461))

* Merge pull request #66 from slauger/dependabot/npm_and_yarn/semantic-release-17.2.3

Bump semantic-release from 17.1.1 to 17.2.3 ([`12ca410`](https://github.com/slauger/check_netscaler/commit/12ca4109dada41b5ff673401832078f03092f419))

* Bump semantic-release from 17.1.1 to 17.2.3

Bumps [semantic-release](https://github.com/semantic-release/semantic-release) from 17.1.1 to 17.2.3.
- [Release notes](https://github.com/semantic-release/semantic-release/releases)
- [Commits](https://github.com/semantic-release/semantic-release/compare/v17.1.1...v17.2.3)

Signed-off-by: dependabot[bot] &lt;support@github.com&gt; ([`f871704`](https://github.com/slauger/check_netscaler/commit/f871704444b744cc4ec08709f524ee2bc279e247))

* Create Dependabot config file ([`a1ba6bc`](https://github.com/slauger/check_netscaler/commit/a1ba6bcea0385e428ededcce13d2b6d9cec72a75))

* Add perltidy to CI pipeline (#60)

* chore: add perltidy in ci tests (fixes #46)
* install Perl::Tidy from CPAN ([`96a76c9`](https://github.com/slauger/check_netscaler/commit/96a76c9b9097ece4cc187b89c7a79859aeccfbba))

## v1.6.1 (2020-09-18)

### Chore

* chore(release): 1.6.1 [skip ci]

## [1.6.1](https://github.com/slauger/check_netscaler/compare/v1.6.0...v1.6.1) (2020-09-18)

### Bug Fixes

* add --seperator to allow to configure a custom perfdata seperator ([#47](https://github.com/slauger/check_netscaler/issues/47)) ([9a9a1b1](https://github.com/slauger/check_netscaler/commit/9a9a1b1d29c3da784cd6b05cce1b162797f8a3cb))
* add limit switch (&#39;--limit&#39;, &#39;-l&#39;) and change spec for label switch from &#39;-l&#39; to &#39;-L&#39; ([f396fbe](https://github.com/slauger/check_netscaler/commit/f396fbe052f658e1d0f3df56519f44ca9f5a721f))
* add release automation via semantic-release-bot ([19bb5d1](https://github.com/slauger/check_netscaler/commit/19bb5d12c390b48e6705da80ecfe1ccc64d5035e))
* add support for limit in more subs ([90b7995](https://github.com/slauger/check_netscaler/commit/90b799526885b7ff663821552f5c21b7d4c2fa22))
* add the ability to set a custom perfdata label for sub check_keyword and check_threshold_and_get_perfdata ([#56](https://github.com/slauger/check_netscaler/issues/56)) ([5c0ef0a](https://github.com/slauger/check_netscaler/commit/5c0ef0a218a56402742329a082d3c754131c3401))
* get host, user and password from environment variables (NETSCALER_HOST, NETSCALER_USERNAME, NETSCALER_PASSWORD) ([4cec658](https://github.com/slauger/check_netscaler/commit/4cec658b89d833d38c318c146f151ba993e62197))
* replace hardcoded id with $plugin-&gt;opts-&gt;label ([2c623d3](https://github.com/slauger/check_netscaler/commit/2c623d3b48da4c47a0a9599fe4c7b86ced22c5cf)) ([`b1fccfd`](https://github.com/slauger/check_netscaler/commit/b1fccfd09c8ba60e331daac1ea63b48932eea839))

* chore: add more advanced tests ([`e65baeb`](https://github.com/slauger/check_netscaler/commit/e65baebeeca379ba0ab81e121940832128f2af17))

* chore: additional tests for advanced switches ([`29a3460`](https://github.com/slauger/check_netscaler/commit/29a3460b4c2fb6b2e0955a4f1585852a66a80640))

* chore: replace NETSCALER_IP with NETSCALER_HOST in our tests ([`3a39b9d`](https://github.com/slauger/check_netscaler/commit/3a39b9db6a2feb9c8f3c17cb367a4db4b7a9fb58))

* chore: run perltidy ([`b183f67`](https://github.com/slauger/check_netscaler/commit/b183f675b29d5dfafd9169ff9767456b34df21d5))

* chore: run perltidy ([`ebf3a49`](https://github.com/slauger/check_netscaler/commit/ebf3a497cbd7a2bb6bd3bbb3873123bd73e50754))

* chore: add docs for advanced switches ([`dc15ddf`](https://github.com/slauger/check_netscaler/commit/dc15ddf20e25f8025e0492dd82ba2e09b583f536))

### Fix

* fix: get host, user and password from environment variables (NETSCALER_HOST, NETSCALER_USERNAME, NETSCALER_PASSWORD) ([`4cec658`](https://github.com/slauger/check_netscaler/commit/4cec658b89d833d38c318c146f151ba993e62197))

* fix: add release automation via semantic-release-bot ([`19bb5d1`](https://github.com/slauger/check_netscaler/commit/19bb5d12c390b48e6705da80ecfe1ccc64d5035e))

* fix: add support for limit in more subs ([`90b7995`](https://github.com/slauger/check_netscaler/commit/90b799526885b7ff663821552f5c21b7d4c2fa22))

* fix: add --seperator to allow to configure a custom perfdata seperator (#47) ([`9a9a1b1`](https://github.com/slauger/check_netscaler/commit/9a9a1b1d29c3da784cd6b05cce1b162797f8a3cb))

* fix: add limit switch (&#39;--limit&#39;, &#39;-l&#39;) and change spec for label switch from &#39;-l&#39; to &#39;-L&#39; ([`f396fbe`](https://github.com/slauger/check_netscaler/commit/f396fbe052f658e1d0f3df56519f44ca9f5a721f))

* fix: replace hardcoded id with $plugin-&gt;opts-&gt;label ([`2c623d3`](https://github.com/slauger/check_netscaler/commit/2c623d3b48da4c47a0a9599fe4c7b86ced22c5cf))

* fix: add the ability to set a custom perfdata label for sub check_keyword and check_threshold_and_get_perfdata (#56) ([`5c0ef0a`](https://github.com/slauger/check_netscaler/commit/5c0ef0a218a56402742329a082d3c754131c3401))

### Unknown

* Merge pull request #57 from slauger/custom-perfdata-label

feat: add limit and label switches ([`8760396`](https://github.com/slauger/check_netscaler/commit/87603967ca4b7b8cefc8bd12ddb79a8c3412d9a3))

* remove release date (to peprare for sematic-release-bot) ([`e68e08c`](https://github.com/slauger/check_netscaler/commit/e68e08c5f63c707896e0cd1d9180f0ad52a19758))

* reset permissions for check_netscaler.pl ([`6494a57`](https://github.com/slauger/check_netscaler/commit/6494a570fc0c6c524d556b5e306f33d2f8d50bb8))

* changed the check_license function (#54)

if no lic-files were given with `-n` option then it will fetch all lic-files which ends with `.lic` and check for these licenses.

Co-authored-by: Simon Lauger &lt;simon@lauger.de&gt; ([`e873ded`](https://github.com/slauger/check_netscaler/commit/e873ded4a5eb1d7c20e1930fe94b06f27979e4b9))

* Merge pull request #53 from juergenz/fix_examples

fix examples icinga2 service templates ([`003f234`](https://github.com/slauger/check_netscaler/commit/003f2346cec193e85cc34e3a06e2d42601fa5322))

* fix examples icinga2 service templates ([`fdd167e`](https://github.com/slauger/check_netscaler/commit/fdd167e95f5abd47f9364cea0c5a56344453f8a7))

## v1.6.0 (2019-10-04)

### Fix

* fix: perltidy broke the file permissions for check_netscaler.pl ([`3891b2c`](https://github.com/slauger/check_netscaler/commit/3891b2c4c99396aad0f53288f43d826c4a4c4acf))

### Unknown

* prepare for release v1.6.0 (#50) ([`05b1f8c`](https://github.com/slauger/check_netscaler/commit/05b1f8c77886f075774285b16bca19c44ffc9f97))

* Merge pull request #45 from slauger/develop

Recent changes from develop ([`584bc3a`](https://github.com/slauger/check_netscaler/commit/584bc3ab75f08fcd1c69b7ce461c658144dda0be))

* Enhance CI Tests (#48)

* run perltidy on check_netscaler.pl

* enhance ci tests - first shot

* fix docker startup

* fix docker startup

* fix sed command

* fix svc_http_web2

* fix svc_http_web2

* add dummy services

* ci test fixes

* ci test fixes

* fix duplicate ips

* fix duplicate ips

* cosmetic changes

* tests for nspartition with multiple objectnames ([`22961b0`](https://github.com/slauger/check_netscaler/commit/22961b020fb69df0951efb73355aae4606bed9ca))

* run perltidy on check_netscaler.pl ([`8bf0754`](https://github.com/slauger/check_netscaler/commit/8bf07546ac0c952f0687ce8928677ec10917d6e5))

* enhanced support for array responses in check_keyword (#43) ([`37e9279`](https://github.com/slauger/check_netscaler/commit/37e92796608bb08626558c3306b715667dfcbae9))

* harmonize the call of the split function (cosmetic) ([`09d0c27`](https://github.com/slauger/check_netscaler/commit/09d0c277709d0e5d51bdaa0fd34b33be1da0b2b2))

* fix syntax error ([`b02359f`](https://github.com/slauger/check_netscaler/commit/b02359fb975bdac0424571d8fd50adbc8fc6ae28))

* fix permissions of check_netscaler.pl one again (thank you perltidy...) ([`54bd9a0`](https://github.com/slauger/check_netscaler/commit/54bd9a0dd2a6dc9f4bc4de5df0ccbe3712e135e6))

* enhanced support for array responses in check_threshold_and_get_perfdata (#43) ([`e2efbd8`](https://github.com/slauger/check_netscaler/commit/e2efbd8f3ce57885b8a8455e2bf22ee0fec04ce7))

* update CHANGELOG.md ([`9dbb205`](https://github.com/slauger/check_netscaler/commit/9dbb205d937eed4755b6b97bbcd6063f1aaf386f))

* reset permissions of check_netscaler.pl ([`b6cf3a8`](https://github.com/slauger/check_netscaler/commit/b6cf3a8a8944557464dc0aa57dac67e6a63a1932))

* run perltidy and cleanup some code ([`105cfb9`](https://github.com/slauger/check_netscaler/commit/105cfb9167a553e2f0c292b55af22f6dff2086fd))

* support for nspartition in check_threshold_and_get_perfdata and check_keyword (#43)

- special handling for objecttypes with a slash inside (e.g. nspartition/mypartition) ([`fec043f`](https://github.com/slauger/check_netscaler/commit/fec043fa5d89be5c34f926ee7d51332ad8b88243))

* updated CHANGELOG.md ([`7c3d298`](https://github.com/slauger/check_netscaler/commit/7c3d29851ae59b65845eaa372ac6404385089ca6))

* switch to plugin_die (as nagios_die is depreacted) ([`05f1b9a`](https://github.com/slauger/check_netscaler/commit/05f1b9afd0fcf9be4a36ae90e3092f9c8460b3bf))

* switch to plugin_exit (as nagios_exit is depreacted) ([`c7314eb`](https://github.com/slauger/check_netscaler/commit/c7314ebf85461cf78c7b57815347c43426251a93))

* only return OK if objectname is not set (#44) ([`d4b1049`](https://github.com/slauger/check_netscaler/commit/d4b1049b118fa7544b776b4ac92883455f03eea3))

* return OK in check state if no vservers are configured/present (#44) ([`8d1654b`](https://github.com/slauger/check_netscaler/commit/8d1654b0f53bc0bc7bcd9741b5e07a93218d3428))

* updated README (tested with version 13.0) ([`52821be`](https://github.com/slauger/check_netscaler/commit/52821be12356c777c01071d98a83fc9f97d536e8))

* updated README (tested with version 13.0) ([`b7d6cf7`](https://github.com/slauger/check_netscaler/commit/b7d6cf74d8eabf142308c132877197afcedd9948))

* simplified .travis.yml ([`ae2d921`](https://github.com/slauger/check_netscaler/commit/ae2d92160e97ebb97fa9154cc64249003f2f8448))

* simplified .travis.yml ([`acb714f`](https://github.com/slauger/check_netscaler/commit/acb714f16eed8fb14f468acae28a0a8354b4803d))

* documentation for building static binary with PAR ([`7ec6675`](https://github.com/slauger/check_netscaler/commit/7ec6675b50907a4d460e688cff23e3d5c8082eda))

* added .gitignore ([`84a9a3c`](https://github.com/slauger/check_netscaler/commit/84a9a3c53e133aaaa208b6cd3343eaefc6bd09ec))

* cosmetic changes - cuddle else and other blocks ([`5108025`](https://github.com/slauger/check_netscaler/commit/51080259113a9c3771f9416043bfd71909f08347))

* removed multiple whitespaces ([`f579cff`](https://github.com/slauger/check_netscaler/commit/f579cff40d421668bf32e3b159dfc24200fd5205))

* fixed permissions of check_netscaler.pl ([`8b6d7c0`](https://github.com/slauger/check_netscaler/commit/8b6d7c01ceff343a25fe4fe771dae7a673ed6832))

* cosmetic changes ([`abb91af`](https://github.com/slauger/check_netscaler/commit/abb91af7951fc5a36f9b381cc20d9333ff6e65a9))

* Merge branch &#39;master&#39; into development ([`7a7d37b`](https://github.com/slauger/check_netscaler/commit/7a7d37b773095c30079fd678bd4dfa89f406e64e))

* added .perltidyrc file ([`098b18c`](https://github.com/slauger/check_netscaler/commit/098b18c6a61b461a38b5fae80774d12758fd6a63))

* Rewrite of Travis CI tests with bats (closed #41) ([`7903a6d`](https://github.com/slauger/check_netscaler/commit/7903a6d959b911d0cb8548fd8716c9353a2ba88e))

* vs_cs_http_web1 should be UP ([`17d51d6`](https://github.com/slauger/check_netscaler/commit/17d51d67f08d470ed3ac73dc206b74cd0ceae376))

* fix ci tests ([`3c92fa7`](https://github.com/slauger/check_netscaler/commit/3c92fa7e057455252ca86444fa154ba730611e49))

* fix ci tests ([`313e16b`](https://github.com/slauger/check_netscaler/commit/313e16b308d8249d6cda47e8ca04a6df3ff22ab3))

* we do not need the complete json response in our travis log ([`c79001d`](https://github.com/slauger/check_netscaler/commit/c79001de0ecb32661ba7705a0c1210570ebea00a))

* finally found a solution to print out stdout ([`979421b`](https://github.com/slauger/check_netscaler/commit/979421be8a9eeb7e9d99617daa499f8c0724a21a))

* set CONTAINER_VERSION as env in .travis.yml ([`1676925`](https://github.com/slauger/check_netscaler/commit/1676925ebf1e9e46d91f21af262c9351801cd660))

* rename var to NETSCALER_IP ([`ae6f19e`](https://github.com/slauger/check_netscaler/commit/ae6f19e9d45a4b673e683f85e6756a75564082dd))

* renamed to travis_test.sh ([`2ea0cf3`](https://github.com/slauger/check_netscaler/commit/2ea0cf34d05b82c5699fbab970cec82a53b1383e))

* renamed to travis_test.sh ([`7d41a14`](https://github.com/slauger/check_netscaler/commit/7d41a14994df89672c7741a27679261161f47ebc))

* prepare netscaler ([`c9befb2`](https://github.com/slauger/check_netscaler/commit/c9befb2c7b9b26a1d93b157728001380f375c7a8))

* use run helper ([`5807852`](https://github.com/slauger/check_netscaler/commit/58078522d400b51734e7b7c438a0678531263b74))

* updated unit tests ([`c5abf5f`](https://github.com/slauger/check_netscaler/commit/c5abf5f9bfa0bc4e028a9d2b053e54220c4eef66))

* updated unit tests ([`1446176`](https://github.com/slauger/check_netscaler/commit/1446176c94193b6929f7fdd0b08d22d45c650577))

* updated unit tests ([`acb1a1d`](https://github.com/slauger/check_netscaler/commit/acb1a1d2abeab124061eb2c09e130fcaded134de))

* updated unit tests ([`b9d0bd4`](https://github.com/slauger/check_netscaler/commit/b9d0bd40b10a15b3807ceb43a1abf34faaffd108))

* install bats-core via git ([`c6a0c6c`](https://github.com/slauger/check_netscaler/commit/c6a0c6ca7d15d48c7c20a0db27c3edf3c96b1d37))

* updated ci tests and switched to bats ([`a7d2926`](https://github.com/slauger/check_netscaler/commit/a7d29261930a1ebbaeeceb47afd4b4d3193b1013))

* Makefile (Perl PP) ([`75da0d7`](https://github.com/slauger/check_netscaler/commit/75da0d77e074eddd5bfcbc58acf8642441aa53a2))

* set lines to 2 (hardcoded) ([`5e8de3f`](https://github.com/slauger/check_netscaler/commit/5e8de3f315a4056a6b2292243f4980a49ac864ef))

* set lines to 0 (hardcoded) ([`58a65b8`](https://github.com/slauger/check_netscaler/commit/58a65b868d99ec4607970e0189f0c4b59e50740f))

* configure netscaler ([`df408d6`](https://github.com/slauger/check_netscaler/commit/df408d6bdf5fd3aa52001617291bd51205f2c32e))

* debug ([`57141dd`](https://github.com/slauger/check_netscaler/commit/57141ddf19e68b8467e699d1188cbb4d842f9440))

* enable debugging ([`bd81595`](https://github.com/slauger/check_netscaler/commit/bd815957c458b2a6c59d3e9606244e287e6d96e5))

* add assert_success to all functions ([`93d8bc4`](https://github.com/slauger/check_netscaler/commit/93d8bc420721b618afd7da0984666d7bf2ba5bef))

* unit testing ([`53c35ff`](https://github.com/slauger/check_netscaler/commit/53c35ff9c4bde43a616a9746a7fdaf04d3d98afb))

* unit testing ([`d4c2eca`](https://github.com/slauger/check_netscaler/commit/d4c2eca92175f9d48da792de510f57185d81fe9c))

* start testrunner ([`34a7f03`](https://github.com/slauger/check_netscaler/commit/34a7f038a49a15cf6230713956799716b28edcec))

* travis ci tests with testing framework ([`d4103a4`](https://github.com/slauger/check_netscaler/commit/d4103a4025a257051982d424a7a5bd2ec40b85ed))

* Merge branch &#39;master&#39; of github.com:slauger/check_netscaler into development ([`f37b907`](https://github.com/slauger/check_netscaler/commit/f37b907c2de9d5c43f4e00d003064de910d65df3))

* Allow dynamic host address variable in Icinga2 command definition ([`e6a412a`](https://github.com/slauger/check_netscaler/commit/e6a412aa3f8333cb7b1f36175749a224f952a3b6))

* added changelog for v1.5.1; set version to v1.5.1 in check_netscaler.pl ([`edc2157`](https://github.com/slauger/check_netscaler/commit/edc215783e76ed61cbe893b71386120007d4485b))

* add missing template perf_enabled #36

Fixes: #36 ([`0f1f2dd`](https://github.com/slauger/check_netscaler/commit/0f1f2dd8d739714d9ffc6103f12d94907ce58724))

* Add netscaler prefix to variable names for critical and warning

Standard practice in the Icinga Template Library is to prefix
the names of the variables with the name of the check. ([`63e5481`](https://github.com/slauger/check_netscaler/commit/63e5481576c5072f5ec4a38d99fea2e68454f80b))

## v1.5.1 (2018-06-10)

### Unknown

* updated docs and plugin tests

- plugin successful tested with 12.1
- using 12.0 build 56.20 for traivs ci ([`870cfb8`](https://github.com/slauger/check_netscaler/commit/870cfb848e890fa58e3a68622ea69fd2607b34a3))

* updated README.md and CHANGELOG.md ([`00711e9`](https://github.com/slauger/check_netscaler/commit/00711e9bbac74510428267e03e2be81ed3706de6))

* Output for array matches more comprehensible ([`3d37978`](https://github.com/slauger/check_netscaler/commit/3d37978b25ea427061f5b517123525a11888801f))

* fixed minor typo, made matches/matches_not support matching in arrays ([`9d9407a`](https://github.com/slauger/check_netscaler/commit/9d9407aaf4f21beda59d337fe8a7ae09f0930558))

## v1.5.0 (2018-03-10)

### Unknown

* prepare for release v1.5.0 ([`f75ee5b`](https://github.com/slauger/check_netscaler/commit/f75ee5bb837ac3ad1ed6269d3223b1f98637b834))

* added filter option for subcommands sslcert, interface and staserver (#31) ([`f83bfb9`](https://github.com/slauger/check_netscaler/commit/f83bfb988befda047b3714040c06a07725f7c001))

* added parameter -f|--filter to docs (#31) ([`931c64f`](https://github.com/slauger/check_netscaler/commit/931c64f20dbc00db9082309a27ea4bbabd0a88f6))

* new parameter -f|--filter to filter out objects in check_state sub (#31) ([`ce95ad3`](https://github.com/slauger/check_netscaler/commit/ce95ad3fc1afbab9cfc1feb9a2495f8ed192ae41))

* added example command policy for monitoring the local license files (thanks to Martin) ([`bd865d5`](https://github.com/slauger/check_netscaler/commit/bd865d5c6cfb8b027cc28d5cdab2b64d25a44a0d))

* added example command policy for monitoring the local license files (thanks to Martin) ([`f4b8d1a`](https://github.com/slauger/check_netscaler/commit/f4b8d1a0ad46d6eb3d967701e538c8a817eb341c))

* removed perfdata for state/service for now
the api documentation from citrix seems to be wrong. Docs say the fields totalrequests, requestsrate, ... should be also available for /v1/service ([`fad7569`](https://github.com/slauger/check_netscaler/commit/fad756973e56452c2c4f878f59d729565bbad202))

* enabled verbose output in travis_test.sh ([`4eb8d2d`](https://github.com/slauger/check_netscaler/commit/4eb8d2df6d2fddd4d40cb587dbd8e6d2c31c2553))

* added example command policy for monitoring the local license files (thanks to Martin) ([`fc5410f`](https://github.com/slauger/check_netscaler/commit/fc5410f516f4da27276328c2336fa63b9f2696ef))

* added example command policy for monitoring the local license files (thanks to Martin) ([`0b43aac`](https://github.com/slauger/check_netscaler/commit/0b43aac8919cb555cdb1d568242c47d0bdc3a536))

* removed perfdata for state/service for now
the api documentation from citrix seems to be wrong. Docs say the fields totalrequests, requestsrate, ... should be also available for /v1/service ([`d84ddd1`](https://github.com/slauger/check_netscaler/commit/d84ddd17460c2ed8443a159bc0972cb6b7ab0e0d))

* enabled verbose output in travis_test.sh ([`5430a9c`](https://github.com/slauger/check_netscaler/commit/5430a9cbfddbbf59811396b5baf2ddb216125e53))

* some cosmetic changes (#26)

some minor cosmetic changes and adding a contributor section ([`d7f90e5`](https://github.com/slauger/check_netscaler/commit/d7f90e565581178dce66df112cf3ff6f92ccb020))

* added automated tests against a NetScaler CPX instance with Travis CI ([`a8c3357`](https://github.com/slauger/check_netscaler/commit/a8c3357d50600841a2afe28d6b96e946e434276c))

* travis build status ([`0e6c276`](https://github.com/slauger/check_netscaler/commit/0e6c2764a38406730e5ac051bca6bc2c4002a188))

* removed dependency installation trough apt ([`e96bc43`](https://github.com/slauger/check_netscaler/commit/e96bc435e0ea81e736bb6f4c7ee254aac314c1a2))

* Makefile, cpanfile ([`a3a8381`](https://github.com/slauger/check_netscaler/commit/a3a83817a0b51a297e0df003b049b2ec314509e6))

* testing with travis ([`5eeef76`](https://github.com/slauger/check_netscaler/commit/5eeef7612b97a845738fb2627b3b79703cad10b8))

* Ubuntu sucks, libmonitoring-plugin-perl is not available as dpkg package; trying installation trough cpanm ([`f50d444`](https://github.com/slauger/check_netscaler/commit/f50d4449801c95a30421f3a4fabb4c57a9ae2423))

* added .travis.yml ([`5e6bdce`](https://github.com/slauger/check_netscaler/commit/5e6bdce378e0944bed256db622ddb9cfcc826e03))

## v1.4.0 (2017-08-20)

### Unknown

* prepare for release v1.4.0 ([`4c20884`](https://github.com/slauger/check_netscaler/commit/4c2088441d306b7b2a7a836d0705d3485702d624))

* defaults values for warning and critical for check_sslcert ([`3227ba3`](https://github.com/slauger/check_netscaler/commit/3227ba3ccaa7be49689c7b2fddd259589931b624))

* switched from Nagios::Plugin to Monitoring::Plugin (libary was renamed in 2014)
added installation instructions for Mac OS X ([`edcdae2`](https://github.com/slauger/check_netscaler/commit/edcdae2dae5b19e6878b78ca9e82b6d11b4674da))

* check for haerrproptimeout in check_hastatus ([`6d99663`](https://github.com/slauger/check_netscaler/commit/6d99663683561118061ef626e2ca357638e1e097))

* added performance data to service and vserver checks (totalrequests, totalresponses, ...); dropped counter when testing a single object ([`26fe2f0`](https://github.com/slauger/check_netscaler/commit/26fe2f064a4133fefa846a428fb74202265be92c))

* added command &#39;hastatus&#39; for testing the current high availability status of a NetScaler appliance ([`2fe18f7`](https://github.com/slauger/check_netscaler/commit/2fe18f786e9fcb60a205b785ea32debd86c7d1e9))

* Merge pull request #24 from bb-Ricardo/master

 	merged check_threshold and get_perfdata into one function: check_threshold_and_get_perfdata ([`3bfe81b`](https://github.com/slauger/check_netscaler/commit/3bfe81b697b8f6119a0a4aba5feeaa8d9901cfc1))

* fix OK output for last commit ([`0591117`](https://github.com/slauger/check_netscaler/commit/0591117a82a28c452aacee1a339a6a015d92b111))

* merged check_threshold and get_perfdata into one function: check_threshold_and_get_perfdata ([`c52216e`](https://github.com/slauger/check_netscaler/commit/c52216ec35408c03ad482cbbdeed104ae883b0ee))

* Merge pull request #22 from bb-Ricardo/master

added new command check_ntp #18 ([`05e0e96`](https://github.com/slauger/check_netscaler/commit/05e0e96e456d4b14b201604049658663227559a3))

* added NTP check #18

Added a new command to check NTP synchronisation with configured peers.
This is pretty much a reimplementation of check_ntp_peer. Output format and
performance data should match to 99%. Also the behaviour of the warning and
critical threshold checking got matched to to check_ntp_peer.

To avoid adding a couple of extra command line options the thresholds can be
set with following options. They have to be comma separated.
* o -&gt; offset
* s -&gt; stratum
* j -&gt; jitter
* t -&gt; truechimers

example:
 -C ntp -w o=0.03,s=1,t=3,j=100 -c o=0.05,s=2,j=200,t=2

Fixes: #18 ([`b8da669`](https://github.com/slauger/check_netscaler/commit/b8da669cf6c04a8bbc26687cbc320a0ace54a77e))

* fixed license check for permanent licenses ([`548b67d`](https://github.com/slauger/check_netscaler/commit/548b67d1e538b618487fb3fb43a9faedb1d0dcb4))

* remove command option &#34;performancedata&#34;

This was only valid for roughly two days. Should be fine to just keep &#34;perfdata&#34;. ([`8c6ef53`](https://github.com/slauger/check_netscaler/commit/8c6ef53a711874829dd04e05ce152cf5e3551409))

* Merge pull request #1 from slauger/master

get current master status ([`ffbc46e`](https://github.com/slauger/check_netscaler/commit/ffbc46e9a0b1c7ef53713d86224bd5c3e45669a6))

## v1.3.0 (2017-08-13)

### Unknown

* Merge pull request #21 from slauger/development

Merge branch development for release v1.3.0 ([`ec6fa2a`](https://github.com/slauger/check_netscaler/commit/ec6fa2ac2b8a62347e01f1863efb0abd83ee0265))

* updated CHANGELOG.md for release v1.3.0 ([`9f0aa8e`](https://github.com/slauger/check_netscaler/commit/9f0aa8e9b1c83533fe22f8e13f68ba552f177ecb))

* removed command server from the plugin (replaced by state in v1.3.0) ([`492e4d0`](https://github.com/slauger/check_netscaler/commit/492e4d04ae3ecceeeab6d72ff1ff49ad4f9f68fb))

* refactoring of check_state

cleanup and simplified code (counter etc.)
added support for testing servers (makes check_server obsolet)
added warning level for DISABLED and PARTIAL-UP ([`cd60efa`](https://github.com/slauger/check_netscaler/commit/cd60efa309fa0eb0a154342202786c7658abf61d))

* harmonize output of threshold and keyword check ([`da21774`](https://github.com/slauger/check_netscaler/commit/da217741ceaf9c74917f6e8002d6eeac39f74398))

* harmonize plugin output for all commands
fixed documentation bug (nsglobalcntr)
check_license does now support testing of multiple license files in a single check
plugin_test.sh does now use --extra-opts to be more flexible ([`905cb90`](https://github.com/slauger/check_netscaler/commit/905cb90ee0bac1060914ac6ca0478eb017a6e358))

* smalld documentation fixes ([`12181b5`](https://github.com/slauger/check_netscaler/commit/12181b500b66763fa9cf0b41cdd3a094ea94d52a))

* plugin_test.sh now uses --extra-opts ([`8cf4f6f`](https://github.com/slauger/check_netscaler/commit/8cf4f6f2f4fd568464580c572093990ab0ccce23))

* added Time-Piece and Data-Dumper in the installation instructions ([`d5d534a`](https://github.com/slauger/check_netscaler/commit/d5d534abeaf30b7b74380aeda8ab9ec9922502fa))

* renamed check performancedata to perfdata (backwards compatible); small documentation changes ([`41764df`](https://github.com/slauger/check_netscaler/commit/41764df67f342774656d9094ee0c9a475edcb075))

* added usage examples to README.md ([`37fbe3d`](https://github.com/slauger/check_netscaler/commit/37fbe3d98649317c398a9d13d410a8ed7fc1d289))

* Disk1 -&gt; Disk ([`794dc8a`](https://github.com/slauger/check_netscaler/commit/794dc8aa404450310b7f7177c75f98eae7759ca8))

* updated examples for threshold and string checks (#7); updated CHANGELOG.md with recent changes ([`8af2e0d`](https://github.com/slauger/check_netscaler/commit/8af2e0dc0a19990e2c08f615ff6d7fcaaf1a63b3))

* renamed checks &#39;string&#39; and &#39;string_not&#39; to &#39;matches&#39; and &#39;matches_not&#39; (with backwards compatibility) ([`73eabdf`](https://github.com/slauger/check_netscaler/commit/73eabdf1844d64e59d76a03f5f382fc17d9a8a60))

* accept multiple values for threshold checks (#7) ([`1db4413`](https://github.com/slauger/check_netscaler/commit/1db4413b37444acead8b607554bd4914a3974c98))

* added perl-Data-Dumper to the dependencies ([`41299d4`](https://github.com/slauger/check_netscaler/commit/41299d41d83bcaf20a750e7c60f43ab94806ab1c))

* updated CHANGELOG.md with the recent changes ([`5677fdf`](https://github.com/slauger/check_netscaler/commit/5677fdf5eddbd70872c8bb5d1892ae34e570f3ec))

* added switch --api to select a different version of the NITRO API (#16) ([`dfc8c2d`](https://github.com/slauger/check_netscaler/commit/dfc8c2d407c2a1dd2c94f8fe5f2a18a67b956f31))

* added example for requesting performance data from global counters (#13) ([`b1d3c2d`](https://github.com/slauger/check_netscaler/commit/b1d3c2d310c2b9293876086964b9ad37690e9964))

* allow usage of urlopts everywhere (also fixes #13) ([`60761c5`](https://github.com/slauger/check_netscaler/commit/60761c5e1c3098670851c2d6ddd0d087f2447634))

* added sub check_license to check the expiry date of a license file (#17) ([`97ff84b`](https://github.com/slauger/check_netscaler/commit/97ff84b06be92539ff7ac17fdde64ac408de6057))

* removed whitespace from sub check_server ([`f6d7a21`](https://github.com/slauger/check_netscaler/commit/f6d7a21e9a1cfd63ec10fdc7e25cccc2abfbac98))

## v1.2.0 (2017-08-12)

### Unknown

* Merge pull request #20 from slauger/development

Release 1.2.0 ([`78ea53b`](https://github.com/slauger/check_netscaler/commit/78ea53b282d7a23d1dd2128be2ca2d0e49a1ce6e))

* added links to contributors in Markdown syntax (GitHub does not recognize the syntax with ‘@user&#39;) ([`0b5c317`](https://github.com/slauger/check_netscaler/commit/0b5c317b2eb087fdacd309ed7fad92037ac4cb3a))

* fixed typo (exmaples) ([`1ebde07`](https://github.com/slauger/check_netscaler/commit/1ebde0756ba372ee1e08d9f8f0fb43fb7693b3c9))

* release v1.2.0 ([`b02e560`](https://github.com/slauger/check_netscaler/commit/b02e56085bc827d5c79e9010366eca7ffe64aedb))

* prepare for v1.2.0, harmonize string quoting ([`168026c`](https://github.com/slauger/check_netscaler/commit/168026cb26cf28b76b5c09b9467d340b04abf7eb))

* added new commands to plugin_test.sh ([`f497d77`](https://github.com/slauger/check_netscaler/commit/f497d77427efa0754e083b298365b0680ec87d05))

* changed description for service group check ([`0290e0c`](https://github.com/slauger/check_netscaler/commit/0290e0c4671c3d234b3f70999359f99683653499))

* refactored the documentation ([`de728ed`](https://github.com/slauger/check_netscaler/commit/de728edd395c6755d64bc143e880d2177e7df3f4))

* Merge pull request #19 from bb-Ricardo/master

enhancing plugin, adding Icinga2 examples ([`0fbf038`](https://github.com/slauger/check_netscaler/commit/0fbf0389fbf4d5ec095e8e75ed0395519b92434f))

* fixed typo in icinga2 templates file ([`c6801d5`](https://github.com/slauger/check_netscaler/commit/c6801d566f75de0de40d8a5179e1d5173482ac1b))

* Added Icinga2 service examples ([`66025c7`](https://github.com/slauger/check_netscaler/commit/66025c74010eae8ab2601b3f0e539c71078d6b5b))

* added new commands to Icinga2 templates ([`d5c7a3e`](https://github.com/slauger/check_netscaler/commit/d5c7a3e3918f910f0388e968b826a874b32337dd))

* adding cli option -x (urlopts)

Adding command line option -x / --urlopts to set NITRO URL options for further filtering in debug mode ([`49b50d5`](https://github.com/slauger/check_netscaler/commit/49b50d515b026440bea6d0918298ad04909c54bb))

* added ICA User session example to README ([`5ddac46`](https://github.com/slauger/check_netscaler/commit/5ddac46030d38881a2a563cfe107610911a275ce))

* make use of nagios_die

I like the name of the function ([`2d286c1`](https://github.com/slauger/check_netscaler/commit/2d286c141e7735e87c0b6ff928d97e7b58b823b7))

* merged check_string and check_string_not into one function ([`28949d4`](https://github.com/slauger/check_netscaler/commit/28949d4694ab3e23359be0e61dc73cbe7d6d48f5))

* Updated README with latest changes ([`dcaaf93`](https://github.com/slauger/check_netscaler/commit/dcaaf93a20a08f03c15e515d56dd7b6ade559c0f))

* updated CHANGELOG for servicegroup command ([`1f72196`](https://github.com/slauger/check_netscaler/commit/1f721963c260601edf5dbf3396fe9165da3327f8))

* added member quorum check to servicegroup command

now you can define (in percent) how many servicegroup members can go DOWN until you get a WARNING or CRITICAL output ([`1c4c25d`](https://github.com/slauger/check_netscaler/commit/1c4c25d1558fe5294dec9cd28ffe774cb431d47d))

* enhanced performance data output for &#34;perfromancedata&#34; ([`2817c47`](https://github.com/slauger/check_netscaler/commit/2817c472f6fe86b53b8e59fab1d0991575f0238d))

* unified threshold functions to check_threshold ([`61ef37c`](https://github.com/slauger/check_netscaler/commit/61ef37c84b87c43f5bbd1bd0c954060dcaef2d8e))

* added command servicegroup to README ([`f556478`](https://github.com/slauger/check_netscaler/commit/f55647856cb057fdabe1d5779d088a36a09e5aff))

* Update CHANGELOG.md ([`8bc0dd2`](https://github.com/slauger/check_netscaler/commit/8bc0dd246eb60b1072cb967dade2213deb106a0c))

* Added new command servicegroup

check the state of a servicegroup and its members ([`4f58ef6`](https://github.com/slauger/check_netscaler/commit/4f58ef6900374fd94be46a0f070331b282061a55))

* fixed issue with interfaces perf data output ([`9c6b9fe`](https://github.com/slauger/check_netscaler/commit/9c6b9fe546898af4e48a6ca200a090bd85f71150))

* performancedata command van now parse arrays

Now it is possible to get performance data from arrays like Interface.
* identifier and field name need to be separated by &#39;.&#39;
* example Interface endpoint:
 -C performancedata -o Interface -n id.tottxbytes,id.totrxbytes ([`7fce71e`](https://github.com/slauger/check_netscaler/commit/7fce71ecbffeb31d11d961cb08fbe43dff68ec73))

* added a contributers section to README ([`fb32f29`](https://github.com/slauger/check_netscaler/commit/fb32f29c2306402888a0517097a50b2acd8ec4b9))

* added &#34;performancedata&#34; command to README ([`c368613`](https://github.com/slauger/check_netscaler/commit/c368613851022a3d245ea29e4a8e1ad2a56773ca))

* added command performancedata to Changelog ([`a842b41`](https://github.com/slauger/check_netscaler/commit/a842b41e3a64dc49b5d8dd995d085fc27c28e1a3))

* added new option to gather performancedata

added option &#34;performancedata&#34; to query stats and counters to forward them to a performance tool of your choice
* examples:
 * cache
    -C performancedata -o ns -n cachetothits,cachetotmisses
 * tcp connections
    -C performancedata -o ns -n tcpcurclientconn,tcpcurclientconnestablished,tcpcurserverconn,tcpcurserverconnestablished
 * http requests
    -C performancedata -o ns -n httprxrequestbytesrate,httprxresponsebytesrate,httptotrequests,httptotresponses,httptotrxrequestbytes,httptotrxresponsebytes ([`2d71db1`](https://github.com/slauger/check_netscaler/commit/2d71db13a55529a12fc91cc433d56b666dea6756))

* add IP adresses to server out in check_netscaler ([`ec365b0`](https://github.com/slauger/check_netscaler/commit/ec365b097db29cc8cc9b331de9d3baa340b7f56a))

* Update README.md ([`f56b807`](https://github.com/slauger/check_netscaler/commit/f56b807f2abbb31e9b88d2fbc915044f487e323f))

* Added new commands to README ([`0fc6093`](https://github.com/slauger/check_netscaler/commit/0fc60939d7943df22019bd5c768aa70726a90780))

* Changelog Update ([`45f36c2`](https://github.com/slauger/check_netscaler/commit/45f36c2387946663afb24ffcc8167b8f22f7935e))

* Add version information to main script ([`33a4c1d`](https://github.com/slauger/check_netscaler/commit/33a4c1d9a084444a01034e445ba662ddf6e98e6e))

* added three new commands to check_netscaler.pl

Added following commands:
* server -&gt; check status of Load Balancing Servers
* hwinfo -&gt; just print information about the Netscaler itself
* interfaces -&gt; check state of all interfaces and add performance data for each interface ([`c6c85a4`](https://github.com/slauger/check_netscaler/commit/c6c85a4bdb4ae20c8a5e3145b6bdf6cf510b543f))

* removing trailing white spaces ([`f4c3bf3`](https://github.com/slauger/check_netscaler/commit/f4c3bf31aafdc9793689bc311d548c67a40bea21))

* fixed templates description ([`a1eddd7`](https://github.com/slauger/check_netscaler/commit/a1eddd7dfa1bde2ff114c07df56683722878c983))

* added icinga2 service templates ([`ae234f8`](https://github.com/slauger/check_netscaler/commit/ae234f8e24191d84d0a4f9dcee0a941cdabf79df))

* Create icinga2_command.conf

Added Icinga2 command definition ([`470a953`](https://github.com/slauger/check_netscaler/commit/470a953fed57145ebb330a868354754054e9a16d))

## v1.1.1 (2017-06-11)

### Unknown

* removed debugging statement ([`c33a50f`](https://github.com/slauger/check_netscaler/commit/c33a50f8a9996ee82e8f314b2d42dbd33ec9a2cc))

* updated documentation ([`9158243`](https://github.com/slauger/check_netscaler/commit/91582438a50c0773c521d118bf368de744196b2c))

* forgot to remove echo statement ([`ef158c7`](https://github.com/slauger/check_netscaler/commit/ef158c7fa60a162436c029e0e44720b0c22908c8))

* bump version to v1.1.1, updated plugin_test.sh ([`d7eb0d8`](https://github.com/slauger/check_netscaler/commit/d7eb0d85051e09bf52ede9ecf336b4282f6de2ba))

* Merge pull request #15 from slauger/development

Merge development branch into master ([`8cbae03`](https://github.com/slauger/check_netscaler/commit/8cbae03b66f3e82a970fc38608e2a39d89bf9fdd))

* support for alternative http ports (to support NetScaler CPX) ([`68108b4`](https://github.com/slauger/check_netscaler/commit/68108b4bbd767b6e4e8d9ed65c55e2b13e2da59e))

* Fix for the svrstate bug in 12.x. As in early 11.0/11.1 builds svrstate always returns DOWN ([`08e84bd`](https://github.com/slauger/check_netscaler/commit/08e84bd99b2ee49a62242a5a5a3b16bf7e8a4781))

## v1.1.0 (2017-05-13)

### Unknown

* bump version to v1.1.0 ([`47b4268`](https://github.com/slauger/check_netscaler/commit/47b4268a990026498a8ade72233c5284ad9ce01d))

* bump version to v1.0.1 ([`ca2f581`](https://github.com/slauger/check_netscaler/commit/ca2f5816981076195d57b691a4c4a793b134db35))

* fixed documentation for staserver (was: &#39;staservers&#39;) ([`83956d3`](https://github.com/slauger/check_netscaler/commit/83956d3a46f3ef5b09dba02dc7ee971e1abc641d))

* removed colon from documentation ([`73776a6`](https://github.com/slauger/check_netscaler/commit/73776a685aea08bd657d8897462ec200e450c6dc))

* Merge pull request #12 from slauger/development

New check &#34;staserver&#34; (#11) ([`3b77909`](https://github.com/slauger/check_netscaler/commit/3b7790907a28e45fd2f81847cb239728664b6fd4))

* #11 checks for secure ticket authority ([`f97faba`](https://github.com/slauger/check_netscaler/commit/f97faba50f09773aeb2a284bf73c0df2ca8ec18d))

* #11 checks for secure ticket authority ([`821c28f`](https://github.com/slauger/check_netscaler/commit/821c28f4dae5acacd38edc79b04d7b2f0b3b83ad))

* added example configuration for nagios ([`c6588d4`](https://github.com/slauger/check_netscaler/commit/c6588d48016dbc4ab8770eb1aec7821bb5e2ed03))

* added missing description for nsconfig check ([`0278192`](https://github.com/slauger/check_netscaler/commit/0278192a6e42d2d0f0eb43035f1f5f266dfabb37))

## v1.0.0 (2017-02-02)

### Unknown

* Merge pull request #10 from slauger/development

Rewrite and released v1.0.0 ([`9d92160`](https://github.com/slauger/check_netscaler/commit/9d921605c25d4a99985b67b6f0221758278fc190))

* Merge branch &#39;master&#39; into development ([`e641511`](https://github.com/slauger/check_netscaler/commit/e641511f214084a167622aaa5416e808ed767e44))

* set version to 0.2.0 ([`f6d489b`](https://github.com/slauger/check_netscaler/commit/f6d489bc7c59ab705d9f40ea6efe7f6586ce2b39))

* renamed check sslcerts to sslcert ([`bc8d8c1`](https://github.com/slauger/check_netscaler/commit/bc8d8c189ff35d66db898f6c9f7c75510c3a9dc3))

* updated documentation ([`d795a6c`](https://github.com/slauger/check_netscaler/commit/d795a6c87983a5c554100b371fe11c7f7a034b33))

* updated documentation ([`9152517`](https://github.com/slauger/check_netscaler/commit/91525176aae2f20bc3f4760d02b9830dab40bab2))

* fixed a typo in sub check_nsconfig ([`66fc921`](https://github.com/slauger/check_netscaler/commit/66fc9212c2509a31187314181ecc7f04baaae284))

* added sub check_nsconfig, beautify some code ([`386521b`](https://github.com/slauger/check_netscaler/commit/386521bae9e2a8b0576e154afab2088f2ce37a68))

* added sub check_nsconfig, beautify some code ([`ad0547d`](https://github.com/slauger/check_netscaler/commit/ad0547da28915777af40298ca88663661fb2714f))

* updated documentation ([`1a712ae`](https://github.com/slauger/check_netscaler/commit/1a712aeb9fbc1724815491f56d48d2967cdeed7a))

* updated documentation ([`8b77012`](https://github.com/slauger/check_netscaler/commit/8b77012fb1f5c067b5c5054f1ce8bb085ec1ead1))

* updated documentation ([`84e08a0`](https://github.com/slauger/check_netscaler/commit/84e08a0789ba9ca2239f56d6b2fe7627fb842f2d))

* updated documentation ([`539253a`](https://github.com/slauger/check_netscaler/commit/539253a9f1a61e46b74453af8e3ac04b0025b3c3))

* updated documentation ([`58e9595`](https://github.com/slauger/check_netscaler/commit/58e95954cc83956b5d561f778879b419533e7852))

* Finished rewrite without Nitro.pm; set version to 1.0.0; ([`72bf434`](https://github.com/slauger/check_netscaler/commit/72bf43499b020c12a73232c0c3583452e11b80a6))

* changed parameters ([`68354bb`](https://github.com/slauger/check_netscaler/commit/68354bb1a4725cd3d315579ec48aeaa0e14c64fb))

* changed argument syntax, added override for endpoint, updated usage and license ([`56db071`](https://github.com/slauger/check_netscaler/commit/56db071a58770aa526515b50704f9126f03c2708))

* changed argument syntax, added override for endpoint, updated usage and license ([`59ec626`](https://github.com/slauger/check_netscaler/commit/59ec626989eabab9d95b743d111e6f652fcf5543))

* updated documentation ([`af1aee9`](https://github.com/slauger/check_netscaler/commit/af1aee941c5207ec4e778bea722450bb900acb19))

* dropped dependency to Nitro.pm; still a lot todo, but first working version ([`2de23c4`](https://github.com/slauger/check_netscaler/commit/2de23c436ab61b67f94ba06197c009627c308b56))

* dropped dependency to Nitro.pm; still a lot todo, but first working version ([`47dc56e`](https://github.com/slauger/check_netscaler/commit/47dc56e49a4062bd12e7d36830cd7ea28545eccc))

* dropped dependency to Nitro.pm; still a lot todo, but first working version ([`bdd69bb`](https://github.com/slauger/check_netscaler/commit/bdd69bb4bf4434331e6073dba4f59e09ae380e81))

* started development for #8 ([`2fce0c8`](https://github.com/slauger/check_netscaler/commit/2fce0c862ddbf8012199dba7302c6c6e4a78a7ec))

* started development for #8 ([`be0acb8`](https://github.com/slauger/check_netscaler/commit/be0acb8e97bf959a9f3c04c1b4f7c288ba1b2f71))

* updated documentation ([`0d53d13`](https://github.com/slauger/check_netscaler/commit/0d53d13ccb492dd74d8d8f224a1ef5b9563e9623))

* Bugfix for #9,SSL parameter didn&#39;t work as expected ([`76d5a22`](https://github.com/slauger/check_netscaler/commit/76d5a22b987997a7121b0c6b66274a724caf7ccd))

* updated documentation; checks were already renamed and no longer available ([`bd7c397`](https://github.com/slauger/check_netscaler/commit/bd7c397807198d86a9b3e4fcb82382a222d4a415))

* changed naming convention, added examples.sh for testing ([`8012919`](https://github.com/slauger/check_netscaler/commit/801291933f1f691e48bb82b47ba19280259d3785))

* updated documentation ([`33a0eae`](https://github.com/slauger/check_netscaler/commit/33a0eae65b55808b59773a725dd72e4fe3980df3))

* updated documentation ([`186c025`](https://github.com/slauger/check_netscaler/commit/186c025bb627eebf26a2452ea9a73b6fbabb5ec3))

* updated documentation ([`ad2d393`](https://github.com/slauger/check_netscaler/commit/ad2d393816b2c820b1d1f53f2b1cb7821c60fafd))

* Issue #1: Patch for Nitro.pm to support SSL ([`48e4205`](https://github.com/slauger/check_netscaler/commit/48e420555aaebea42cc54d27bb8c13590ff66621))

* inital patch for ssl support ([`d238968`](https://github.com/slauger/check_netscaler/commit/d238968924e745956b820299036b3cfcbb9c8d6d))

* removed documentation from script, set identifier for check_vserver as required paramter ([`7a4a10c`](https://github.com/slauger/check_netscaler/commit/7a4a10cd6724ee4f72dbdb14d868836b263f29e4))

* #6: always require -w and -c for check_sslcert ([`e5dddab`](https://github.com/slauger/check_netscaler/commit/e5dddabc99fbb37e6051b5fd2172dfd36c50d0a6))

* added sub check_sslcert for certificate expiry checks ([`610f3e3`](https://github.com/slauger/check_netscaler/commit/610f3e3407caf6c8bed62c6fdc8997397a8dc705))

* added sub dump_conf ([`93ddd7d`](https://github.com/slauger/check_netscaler/commit/93ddd7d53e3e047d8f1bf5d82d0107357e9a108a))

* Bugfix for sub add_arg: missed parameters for &#39;default&#39; and &#39;required&#39; ([`d278999`](https://github.com/slauger/check_netscaler/commit/d278999ea113ce00b5d818ee8f3b0bb29b422a37))

* performance data is now available ([`dfcfbeb`](https://github.com/slauger/check_netscaler/commit/dfcfbebc71105279c5c2930bd1e37e1a3393969a))

* added performance data for check_threshold_* ([`ad3534b`](https://github.com/slauger/check_netscaler/commit/ad3534b9c04e302873eaef574eddd96856f5ba66))

* added performance data for check_vserver ([`b8d39d0`](https://github.com/slauger/check_netscaler/commit/b8d39d0a923ec6b14a51cfb826de348f3fb2f3f2))

* Merge pull request #5 from macampo/master

Update check_netscaler.pl ([`26fc9c3`](https://github.com/slauger/check_netscaler/commit/26fc9c30653efa4c2dd3f964954df5faf8948559))

* Update check_netscaler.pl

Noticed that for the vserver sub it reports the status of only the first vserver and then exits. This adjustment makes sure that it loops through all vservers, then reports and exits. ([`8e65a46`](https://github.com/slauger/check_netscaler/commit/8e65a46e83c1408ca80ba21308e01f3ba4c0dfd1))

* Merge pull request #4 from Velociraptor85/patch-1

Typo changes ([`0fc64fc`](https://github.com/slauger/check_netscaler/commit/0fc64fc8c0127a768130dbfd02bfba3af6396d07))

* Typo changes

Typo changes in Help and Version UP ([`5e1df3d`](https://github.com/slauger/check_netscaler/commit/5e1df3d43424c37509d84ca3139ae839fe44446a))

* updated documentation (Nitro API URL) ([`f3d7316`](https://github.com/slauger/check_netscaler/commit/f3d73163cd0d06ba5705bfaa99ae6aad4c2484de))

* updated README.md (usage examples) ([`26bdaee`](https://github.com/slauger/check_netscaler/commit/26bdaeeb4dbca30c797ae69c361fc053a86a5014))

* updated README.md (usage examples) ([`8092e40`](https://github.com/slauger/check_netscaler/commit/8092e40f43c8d5740f588116be9164ef76a544f0))

* updated README.md (usage examples) ([`f961755`](https://github.com/slauger/check_netscaler/commit/f961755c9ff9dd86931af1cce9c0d326f32d1e5c))

* updated README.md (usage examples) ([`c6a8ee0`](https://github.com/slauger/check_netscaler/commit/c6a8ee018e41a70012074f1bceeb970263a88366))

* updated README.md (usage examples) ([`b777a59`](https://github.com/slauger/check_netscaler/commit/b777a597397e255e4148feac5bf3658ab49b8ef5))

* updated README.md (usage examples) ([`05dc0cf`](https://github.com/slauger/check_netscaler/commit/05dc0cf385376168b8d8de5388daa29c23b1d63d))

* updated README.md (usage examples) ([`c95437c`](https://github.com/slauger/check_netscaler/commit/c95437c6a413fa511e2df374d0611c0267de29fd))

* updated README.md (usage examples) ([`18d10a0`](https://github.com/slauger/check_netscaler/commit/18d10a06d2c31f37de9c835877f4bb9eff1dbba4))

* added check_netscaler.pl ([`e8805db`](https://github.com/slauger/check_netscaler/commit/e8805dbd4def4c0b116f40ead33c742b9d88cd8c))

* added check_netscaler.pl ([`60e36fb`](https://github.com/slauger/check_netscaler/commit/60e36fb5c003787aff93dd7c158faba0fae167af))

* Initial commit ([`041d078`](https://github.com/slauger/check_netscaler/commit/041d07807432b406d1a18067c234f2a403439eaa))
