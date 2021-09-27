## [1.6.2](https://github.com/slauger/check_netscaler/compare/v1.6.1...v1.6.2) (2021-09-27)


### Bug Fixes

* measurement should be undef for hapktrxrate and hapkttxrate ([#47](https://github.com/slauger/check_netscaler/issues/47)) ([1c721dd](https://github.com/slauger/check_netscaler/commit/1c721dd4e6f940a409b1b0c8c20af5a3d5a13bb4))

## [1.6.1](https://github.com/slauger/check_netscaler/compare/v1.6.0...v1.6.1) (2020-09-18)


### Bug Fixes

* add --seperator to allow to configure a custom perfdata seperator ([#47](https://github.com/slauger/check_netscaler/issues/47)) ([9a9a1b1](https://github.com/slauger/check_netscaler/commit/9a9a1b1d29c3da784cd6b05cce1b162797f8a3cb))
* add limit switch ('--limit', '-l') and change spec for label switch from '-l' to '-L' ([f396fbe](https://github.com/slauger/check_netscaler/commit/f396fbe052f658e1d0f3df56519f44ca9f5a721f))
* add release automation via semantic-release-bot ([19bb5d1](https://github.com/slauger/check_netscaler/commit/19bb5d12c390b48e6705da80ecfe1ccc64d5035e))
* add support for limit in more subs ([90b7995](https://github.com/slauger/check_netscaler/commit/90b799526885b7ff663821552f5c21b7d4c2fa22))
* add the ability to set a custom perfdata label for sub check_keyword and check_threshold_and_get_perfdata ([#56](https://github.com/slauger/check_netscaler/issues/56)) ([5c0ef0a](https://github.com/slauger/check_netscaler/commit/5c0ef0a218a56402742329a082d3c754131c3401))
* get host, user and password from environment variables (NETSCALER_HOST, NETSCALER_USERNAME, NETSCALER_PASSWORD) ([4cec658](https://github.com/slauger/check_netscaler/commit/4cec658b89d833d38c318c146f151ba993e62197))
* replace hardcoded id with $plugin->opts->label ([2c623d3](https://github.com/slauger/check_netscaler/commit/2c623d3b48da4c47a0a9599fe4c7b86ced22c5cf))

## v1.6.0 (2019-10-04)
- return OK in state check if no vservers are configured (#44)
- replaced depreacted calls from Perl-Nagios-Plugin with new names from Perl-Monitoring-Plugin
- experimental support for objecttypes with a slash inside, e.g. for nspartition/foo (#43)
- enhanced support for array responses in check_threshold_and_get_perfdata (#43)

## v1.5.1 (2018-06-10)
- fixed minor typo, made matches/matches_not support matching in arrays
- output for array matches more comprehensible (#33)
- updated README.md and CHANGELOG.md (#33)
- updated README.md (plugin successful tested with 12.1)
- using 12.0 build 56.20 for traivs ci tests

## v1.5.0 (2018-03-10)
- added automated tests against a NetScaler CPX with TravisCI
- using /usr/bin/env instead of hardcoding the perl binary path
- added filter parameter for filtering out objects from the API response (used in state, sslcert, staserver and interface) (#31)
- disabled performance data in sub state for services

## v1.4.0 (2017-08-20)
- added command ntp to check NTP status (#18)
- merged check_threshold and get_perfdata into one function: check_threshold_and_get_perfdata
- added command hastatus to check the status of an high availability pair (#25)
- command state: more performance data when testing single vserver and service objects (not servicegroups)
- switched from Nagios::Plugin to Monitoring::Plugin (Nagios::Plugin was renamed to Monitoring::Plugin in 2014)

## v1.3.0 (2017-08-13)
- added command license to check the status of a local license file (#17)
- added perl-Time-Piece as new dependency (Time::Piece for license check)
- added perl-Data-Dumper to the install instructions in the README.md
- added switch for selecting a different version of the NITRO API (fixes #16)
- allow the usage of urlopts everywhere (fixes #13)
- check_threshold and check_string accept arrays (seperated by colon) (fixes #7)
- renamed checks 'string' and 'string_not' to 'matches' and 'matches_not' (backwards compatibility given)
- renamed check 'performancedata' to 'perfdata' (backwards compatibility given);
- backwards compatibility will be removed in a future release, please update your nagios configuration
- harmonized plugin output for all subcommands
- refactored sub check_state (cleanup and simplified code)
  - added support for testing the status of server objects
  - added a new warning level for DISABLED and PARTIAL-UP objects
- removed command server (as it might be confusing for users to have two checks with the same function)

## v1.2.0 (2017-08-12)
- merged pull request from @bb-Ricardo
  - added command server to check status of Load Balancing Servers
  - added command hwinfo to just print information about the Netscaler itself
  - added command interfaces to check state of all interfaces and add performance data for each interface
  - added command to request performance data
  - added command to check the state of a servicegroup and its members (set warning and critical values for member quorum)
  - added Icinga2 config templates
- updated documentation and plugin_test.sh

## v1.1.1 (2017-06-10)
- bugfix for servicegroups in 12.0 (#12)
- new option to connect to an alternate port (for CPX instances)

## v1.1.0 (2017-05-13)
 - new check command for STA services
 - small documentation fixes

## v1.0.0 (2017-02-01)
 - huge rewrite of the Plugin, changed nearly every parameters 
 - upgrading from versions prior to 1.0.0 require to change your monitoring configuration
 - added own nitro implementation and dropped the dependency to Nitro.pm by Citrix
 - added check for unsaved configuration changes (changes in nsconfig not written to disk)
 - improved check for ssl certificates to only check for a specific certificate
 - fixed a bug in check_state to support services and servicegroups again

## v0.2.0 2017-01-04
 - patch for Nitro.pm to support ssl connections
 - added check to test the validity and expiry of installed certificates 

## v0.1.2 2016-12-02
 - added performance data feature 
 - updated sub add_arg and added default values for parameters
 - Bugfix in vserver checks loop by @macampo 

## v0.1.1 2016-11-10
 - documentation fixes by @Velociraptor85

## v0.1.0 (2015-12-17)
 - First release based on Nitro.pm
