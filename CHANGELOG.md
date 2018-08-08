## v1.6.0 (YYYY-MM-DD)
- better support for SDX appliances in subs matches/matches_not (#33)

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
