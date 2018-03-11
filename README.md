[![Build Status](https://travis-ci.org/slauger/check_netscaler.svg?branch=master)](https://travis-ci.org/slauger/check_netscaler)

# check_netscaler Nagios Plugin

A Nagios Plugin written for the Citrix NetScaler Application Delivery Controller. It's based on Perl (Monitoring::Plugin) and using the the NITRO REST API. No need for SNMP.

Currently the plugin has the following subcommands:

| command                | description |
---                      | --- | 
**state**                | check the current service state of vservers (e.g. lb, vpn, gslb), services and service groups and servers
**matches, matches_not** | check if a string matches the the api response or not
**above, below**         | check if a value is above/below a threshold (e.g. traffic limits, concurrent connections)
**sslcert**              | check the lifetime for installed ssl certificates
**nsconfig**             | check for configuration changes which are not saved to disk
**license**              | check the expiry date of a local installed license file
**hastatus**             | check the high availability status of a appliance
**staserver**            | check if configured STA (secure ticket authority) servers are available
**servicegroup**         | check the state of a servicegroup and its members
**hwinfo**               | just print information about the Netscaler itself
**interfaces**           | check state of all interfaces and add performance data for each interface
**perfdata**             | gather performancedata from all sorts of API endpoints
**ntp**                  | check the ntp synchronization status
**debug**                | debug command, print all data for a endpoint

This plugin works with VPX, MPX, SDX and CPX NetScaler Appliances. The api responses may differ by build, appliance type and your installed license.

The plugin supports performance data for the commands state and the above or below threshold checks. Also there is a perfdata command to gather information from your NetScaler.

Example configurations for Nagios and Icinga 2 can be found in the examples directory of this repository.

Feedback and feature requests are appreciated. Just create an issue on GitHub or send me a pull request.

If you looking for a plugin to test your NetScaler Gateway vServer and Storefront see also [check_netscaler_gateway](https://github.com/slauger/check_netscaler_gateway).

## Installation

Run the following commands to install all Perl dependencies (Monitoring::Plugin, LWP, JSON, Time::Piece, Data::Dumper).

### Enterprise Linux (CentOS, RedHat)

```
yum install perl-libwww-perl perl-JSON perl-Monitoring-Plugin perl-Time-Piece perl-Data-Dumper
```

If you want to connect to your NetScaler with SSL/HTTPS you should also install the LWP HTTPS package.

```
yum install perl-LWP-Protocol-https
```

### Debian and Ubuntu Linux

```
apt-get install libwww-perl liblwp-protocol-https-perl libjson-perl libmonitoring-plugin-perl
```

### Mac OS X

The preinstalled Perl distribution is missing the JSON and Monitoring::Plugin libaries. The best way is to install them is trough the cpanminus tool. The cpanminus tool can be installed trough [brew](https://github.com/Homebrew/brew).

```
brew install cpanminus
```

Use the following commands to install the missing perl libaries.

```
sudo cpanm JSON
sudo cpanm Monitoring::Plugin
```

## Usage
```
Usage: check_netscaler
-H|--hostname=<hostname> -C|--command=<command>
[ -o|--objecttype=<objecttype> ] [ -n|--objectname=<objectname> ]
[ -u|--username=<username> ] [ -p|--password=<password> ]
[ -s|--ssl ] [ -a|--api=<version> ] [ -P|--port=<port> ]
[ -e|--endpoint=<endpoint> ] [ -w|--warning=<warning> ] [ -c|--critical=<critical> ]
[ -v|--verbose ] [ -t|--timeout=<timeout> ] [ -x|--urlopts=<urlopts> ]

 -?, --usage
   Print usage information
 -h, --help
   Print detailed help screen
 -V, --version
   Print version information
 --extra-opts=[section][@file]
   Read options from an ini file. See http://nagiosplugins.org/extra-opts
   for usage and examples.
 -H, --hostname=STRING
   Hostname of the NetScaler appliance to connect to
 -u, --username=STRING
   Username to log into box as (default: nsroot)
 -p, --password=STRING
   Password for login username (default: nsroot)
 -s, --ssl
   Establish connection to NetScaler using SSL
 -P, --port=INTEGER
   Establish connection to a alternate TCP Port
 -C, --command=STRING
   Check to be executed on the appliance
 -o, --objecttype=STRING
   Objecttype (target) to for the check command
 -n, --objectname=STRING
   Filter request to a specific objectname
 -e, --endpoint=STRING
   Override option for the API endpoint (stat or config)
 -w, --warning=STRING
   Value for warning
 -c, --critical=STRING
   Value for critical
 -x, --urlopts=STRING
   add additional url options
 -a, --api=STRING
   version of the NITRO API to use (default: v1)
 -f, --filter=STRING
   filter out objects from the API response (regular expression syntax)
 -t, --timeout=INTEGER
   Seconds before plugin times out (default: 15)
 -v, --verbose
   Show details for command-line debugging (can repeat up to 3 times)
```

## Usage Examples

### Check status of vServers

```
# NetScaler::LBvServer
./check_netscaler.pl -H ${IPADDR} -s -C state -o lbvserver

# NetScaler::LBvServer::Website
./check_netscaler.pl -H ${IPADDR} -s -C state -o lbvserver -n vs_lb_http_webserver

# NetScaler::VPNvServer
./check_netscaler.pl -H ${IPADDR} -s -C state -o vpnvserver

# NetScaler::GSLBvServer
./check_netscaler.pl -H ${IPADDR} -s -C state -o gslbvserver

# NetScaler::AAAvServer
./check_netscaler.pl -H ${IPADDR} -s -C state -o authenticationvserver

# NetScaler::CSvServer
./check_netscaler.pl -H ${IPADDR} -s -C state -o csvserver

# NetScaler::SSLvServer (obsolet and replaced by lbvserver for newer builds)
./check_netscaler.pl -H ${IPADDR} -s -C state -o sslvserver
```

### Check status of services

```
# NetScaler::Services
./check_netscaler.pl -H ${IPADDR} -s -C state -o service

# NetScaler::Services::Webserver
./check_netscaler.pl -H ${IPADDR} -s -C state -o service -n svc_webserver
```

### Check status of service groups

```
# NetScaler::Servicegroups
./check_netscaler.pl -H ${IPADDR} -s -C state -o servicegroup

# NetScaler::Servicegroups::Webservers
./check_netscaler.pl -H ${IPADDR} -s -C state -o servicegroup -n sg_webservers
```

### Check status and quorum of a service group

Define member quorum (in percent) with warning and critical values.

```
# NetScaler::Servicegroup::Webservers
./check_netscaler.pl -H ${IPADDR} -s -C servicegroup -n sg_webservers -w 75 -c 50
```

### Check status of server objects

```
# NetScaler::Servers
./check_netscaler.pl -H ${IPADDR} -s -C state -o server

# NetScaler::Servers::web01.example.com
./check_netscaler.pl -H ${IPADDR} -s -C state -o server -n web01.example.com
```

### Check for thresholds or matching strings

Multiple fields need to be seperated by a colon.

```
# NetScaler::Memory
./check_netscaler.pl -H ${IPADDR} -s -C above -o system -n memusagepcnt -w 75 -c 80

# NetScaler::CPU
./check_netscaler.pl -H ${IPADDR} -s -C above -o system -n cpuusagepcnt,mgmtcpuusagepcnt -w 75 -c 80

# NetScaler::Disk
./check_netscaler.pl -H ${IPADDR} -s -C above -o system -n disk0perusage,disk1perusage -w 75 -c 80

# NetScaler::HA::Status
./check_netscaler.pl -H ${IPADDR} -s -C matches_not -o hanode -n hacurstatus -w YES -c YES

# NetScaler::HA::State
./check_netscaler.pl -H ${IPADDR} -s -C matches_not -o hanode -n hacurstate -w UP -c UP
```

### Check expiration of installed ssl certificates

```
# NetScaler::Certs
./check_netscaler.pl -H ${IPADDR} -s -C sslcert -w 30 -c 10

# NetScaler::Certs::Wildcard
./check_netscaler.pl -H ${IPADDR} -s -C sslcert -n wildcard.example.com -w 30 -c 10
```

### Check for unsaved configuration changes

```
# NetScaler::Config
./check_netscaler.pl -H ${IPADDR} -s -C nsconfig
```

### Check the expiry date of a local license file

The license file must be placed in `/nsconfig/license` and the filename must be given as objectname.
Also the NITRO user needs permissions to access the filesystem directly (NITRO command systemfile). This could be achieved with the following command policy.
```
add system cmdPolicy nagios ALLOW "(^man.*)|(^show\\s+(?!system)(?!configstatus)(?!ns ns\\.conf)(?!ns savedconfig)(?!ns runningConfig)(?!gslb runningConfig)(?!audit messages)(?!techsupport).*)|(^stat.*)|(^show\\s+(system)\\s+(file))"
```

Multiple license files can be passed, separated with a colon.

```
# NetScaler::License
./check_netscaler.pl -H ${IPADDR} -s -C license -n FID_4c9a2c7e_14292ea2df2_2a97.lic,FID_2b9a2c7e_14212ef2d27_4b87.lic -w 30 -c 10
```

### Check the current high availability status

```
# NetScaler::HA
./check_netscaler.pl -H ${IPADDR} -s -C hastatus
```

### Check if STA servers are working

```
# NetScaler::STA
./check_netscaler.pl -H ${IPADDR} -s -C staserver

# NetScaler::STA::vs_vpn_gateway
./check_netscaler.pl -H ${IPADDR} -s -C staserver -n vs_vpn_gateway
```

### Get information about the netscaler

```
# NetScaler::HWInfo
./check_netscaler.pl -H ${IPADDR} -s -C hwinfo
```

### Check status of all network interfaces

```
# NetScaler::Interfaces
./check_netscaler.pl -H ${IPADDR} -s -C interfaces
```

### Request performance data

All fields must be defined via "-n" option and be seperated with a comma.

```
# NetScaler::Performancedata on Cache hit/misses
./check_netscaler.pl -H ${IPADDR} -s -C perfdata -o ns -n cachetothits,cachetotmisses

# NetScaler::Performancedata on tcp connections
./check_netscaler.pl -H ${IPADDR} -s -C perfdata -o ns -n tcpcurclientconn,tcpcurclientconnestablished,tcpcurserverconn,tcpcurserverconnestablished

# NetScaler::Performancedata on network interfaces
./check_netscaler.pl -H ${IPADDR} -s -C perfdata -o Interface -n id.totrxbytes

# NetScaler::Current user sessions
./check_netscaler.pl -H ${IPADDR} -s -C perfdata -o aaa -n aaacuricasessions,aaacuricaonlyconn

# find more object names to check out for object type "ns"
/check_netscaler.pl -H ${IPADDR} -s -C debug -o ns
```

[Global counters](https://docs.citrix.com/en-us/netscaler/12/nitro-api/nitro-rest/nitro-rest-usage-scenarios/view-individual-counter-info.html) can be accessed as follows (NetScaler 12.0 and newer).

```
./check_netscaler.pl -H ${IPADDR} -s -C perfdata -o nsglobalcntr -n http_tot_Requests,http_tot_Responses -x 'args=counters:http_tot_Requests;http_tot_Responses'
```

For more interesting performance data object types see the following API methods.

- ns
- cache
- protocolhttp
- protocolip
- protocoltcp

### check NTP status
This is pretty much a reimplementation of [check_ntp_peer](https://github.com/monitoring-plugins/monitoring-plugins/blob/master/plugins/check_ntp_peer.c). Output format and performance data should match to 99%.
Also the behaviour of the warning and critical threshold checking got matched to check_ntp_peer.
To avoid adding a couple of extra command line options the thresholds can be set with following options. Format: "option=value". They have to be comma separated.
* o -> offset
* s -> stratum
* j -> jitter
* t -> truechimers

```
# check NTP status
./check_netscaler.pl -H ${IPADDR} -s -C ntp -w o=0.03,j=100,s=1,t=3 -c o=0.05,j=200,s=2,t=2
```
This means:
* offset WARNING if peer offset is >= 30 ms or <= - 30 ms
* jitter WARNING if jitter is >= 100 ms
* stratum WARNING if peer stratum > 1
* truechimers WARNING if number of truechimers (possible sync sources) is <= 3
* offset CRITICAL if peer offset is >= 50 ms or <= - 50 ms
* jitter CRITICAL if jitter is >= 200 ms
* stratum CRITICAL if peer stratum > 2
* truechimers CRITICAL if number of truechimers (possible sync sources) is <= 2

## Debug command

```
# Print all LB vServers (stat endpoint)
./check_netscaler.pl -H ${IPADDR} -s -C debug -o lbvserver

# Print all LB vServers (config endpoint)
./check_netscaler.pl -H ${IPADDR} -s -C debug -o lbvserver -e config
```

## Configuration File

The plugin uses the Monitoring::Plugin Libary, so you can use --extra-opts and seperate the login crendetials from your nagios configuration.

```
define command {
  command_name check_netscaler_vserver
  command_line $USER5$/3rdparty/check_netscaler/check_netscaler.pl -H $HOSTADDRESS$ -s --extra-opts=netscaler@$USER11$/plugins.ini -C state -n '$ARG1$'
}
```

```
[netscaler]
hostname=netscaler01
username=nagios
password=password
ssl=true
```

## Authors
- [slauger](https://github.com/slauger)

## Contributors
- [macampo](https://github.com/macampo)
- [Velociraptor85](https://github.com/Velociraptor85)
- [bb-ricardo](https://github.com/bb-ricardo)

## NITRO API Documentation

You will find a full documentation about the NITRO API on your NetScaler Appliance in the "Download" area.

http://NSIP/nitro-rest.tgz (where NSIP is the IP address of your NetScaler appliance).

## Tested Firmware

Tested with NetScaler 10.5, 11.0, 11.1 and 12.0. The plugin should work with all available firmware builds.

## Automated Tests

Every commit and pull request in this repository will trigger a continuous integration test with [Travis CI](https://travis-ci.org/slauger/check_netscaler). The test starts a NetScaler CPX instance (currently build 11.1-53.11) and runs `tests/travis_test.sh` against the container.

Please add tests if you add new commands to this plugin. Be aware that a NetScaler CPX is very limited in it's features and not all checks of this plugin will work against a CPX instance (e.g. `hwinfo`, `ntp`, ...).

## Changelog

See [CHANGELOG](CHANGELOG.md)
