#!/usr/bin/env perl
##############################################################################
# check_netscaler.pl
# Nagios Plugin for Citrix NetScaler
# Simon Lauger <simon@lauger.name>
#
# https://github.com/slauger/check_netscaler
#
# Version: v1.6.0 (2019-10-04)
#
# Copyright 2015-2019 Simon Lauger
#
# Contributor:
# bb-ricardo (github.com/bb-ricardo)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##############################################################################

use strict;
use warnings;

use LWP;
use JSON;
use URI::Escape;
use MIME::Base64;
use Data::Dumper;
use Monitoring::Plugin;
use Time::Piece;

my $plugin = Monitoring::Plugin->new(
  plugin    => 'check_netscaler',
  shortname => 'NetScaler',
  version   => 'v1.6.0',
  url       => 'https://github.com/slauger/check_netscaler',
  blurb     => 'Nagios Plugin for Citrix NetScaler Appliance (VPX/MPX/SDX/CPX)',
  usage     => 'Usage: %s
-H|--hostname=<hostname> -C|--command=<command>
[ -o|--objecttype=<objecttype> ] [ -n|--objectname=<objectname> ]
[ -u|--username=<username> ] [ -p|--password=<password> ]
[ -s|--ssl ] [ -a|--api=<version> ] [ -P|--port=<port> ]
[ -e|--endpoint=<endpoint> ] [ -w|--warning=<warning> ] [ -c|--critical=<critical> ]
[ -v|--verbose ] [ -t|--timeout=<timeout> ] [ -x|--urlopts=<urlopts> ]',
  license => 'http://www.apache.org/licenses/LICENSE-2.0',
  extra   => '
This is a Nagios monitoring plugin for the Citrix NetScaler. The plugin works with
the Citrix NetScaler NITRO API. The goal of this plugin is to have a single plugin
for every important metric on the Citrix NetSaler.

This plugin works for NetScaler VPX, MPX, SDX and CPX appliances.

See https://github.com/slauger/check_netscaler for details.'
);

my @args = (
  {
    spec     => 'hostname|H=s',
    usage    => '-H, --hostname=STRING',
    desc     => 'Hostname of the NetScaler appliance to connect to',
    required => 1,
  },
  {
    spec     => 'username|u=s',
    usage    => '-u, --username=STRING',
    desc     => 'Username to log into box as (default: nsroot)',
    default  => 'nsroot',
    required => 0,
  },
  {
    spec     => 'password|p=s',
    usage    => '-p, --password=STRING',
    desc     => 'Password for login username (default: nsroot)',
    default  => 'nsroot',
    required => 0,
  },
  {
    spec     => 'ssl|s!',
    usage    => '-s, --ssl',
    desc     => 'Establish connection to NetScaler using SSL',
    default  => 0,
    required => 0,
  },
  {
    spec     => 'port|P=i',
    usage    => '-P, --port=INTEGER',
    desc     => 'Establish connection to a alternate TCP Port',
    default  => 0,
    required => 0,
  },
  {
    spec     => 'command|C=s',
    usage    => '-C, --command=STRING',
    desc     => 'Check to be executed on the appliance.',
    required => 1,
  },
  {
    spec     => 'objecttype|o=s',
    usage    => '-o, --objecttype=STRING',
    desc     => 'Objecttype (target) to for the check command',
    required => 0,
  },
  {
    spec     => 'objectname|n=s',
    usage    => '-n, --objectname=STRING',
    desc     => 'Filter request to a specific objectname',
    required => 0,
  },
  {
    spec     => 'endpoint|e=s',
    usage    => '-e, --endpoint=STRING',
    desc     => 'Override option for the API endpoint (stat or config)',
    required => 0,
  },
  {
    spec     => 'warning|w=s',
    usage    => '-w, --warning=STRING',
    desc     => 'Value for warning',
    required => 0,
  },
  {
    spec     => 'critical|c=s',
    usage    => '-c, --critical=STRING',
    desc     => 'Value for critical',
    required => 0,
  },
  {
    spec     => 'urlopts|x=s',
    usage    => '-x, --urlopts=STRING',
    desc     => 'add additional url options',
    required => 0,
  },
  {
    spec     => 'api|a=s',
    usage    => '-a, --api=STRING',
    desc     => 'version of the NITRO API to use (default: v1)',
    required => 0,
    default  => 'v1',
  },
  {
    spec     => 'filter|f=s',
    usage    => '-f, --filter=STRING',
    desc     => 'filter out objects from the API response (regular expression syntax)',
    required => 0,
  },
  {
    spec     => 'limit|l=s',
    usage    => '-l, --limit=STRING',
    desc     => 'limit check to objects matching this pattern (regular expression syntax)',
    required => 0,
  },
  {
    spec     => 'label|L=s',
    usage    => '-L, --label=STRING',
    desc     => 'optional name of the field, which will be used as identifier when the response contians multiple items (default is to use the array index instead)',
    required => 0,
  }
);

foreach my $arg (@args) {
  add_arg( $plugin, $arg );
}

$plugin->getopts;

if ( $plugin->opts->command eq 'state' ) {

  # check for up/down state of vservers, service, servicegroup
  check_state($plugin);
} elsif ( $plugin->opts->command eq 'above' ) {

  # check if a response is above a threshold
  check_threshold_and_get_perfdata( $plugin, $plugin->opts->command );
} elsif ( $plugin->opts->command eq 'below' ) {

  # check if a response is below  a threshold
  check_threshold_and_get_perfdata( $plugin, $plugin->opts->command );
}

# be backwards compatible; also accept command 'string'
elsif ( $plugin->opts->command eq 'matches' || $plugin->opts->command eq 'string' ) {

  # check if a response does contains a specific string
  check_keyword( $plugin, 'matches' );
}

# be backwards compatible; also accept command 'string_not'
elsif ( $plugin->opts->command eq 'matches_not' || $plugin->opts->command eq 'string_not' ) {

  # check if a response does not contains a specific string
  check_keyword( $plugin, 'matches not' );
} elsif ( $plugin->opts->command eq 'sslcert' ) {

  # check for the lifetime of installed certificates
  check_sslcert($plugin);
} elsif ( $plugin->opts->command eq 'nsconfig' ) {

  # check for unsaved configuration changes
  check_nsconfig($plugin);
} elsif ( $plugin->opts->command eq 'staserver' ) {

  # check the state of the staservers
  check_staserver($plugin);
} elsif ( $plugin->opts->command eq 'hwinfo' ) {

  # print infos about hardware and build version
  get_hardware_info($plugin);
} elsif ( $plugin->opts->command eq 'perfdata' ) {

  # print performance data of protocol stats
  check_threshold_and_get_perfdata( $plugin, 'above' );
} elsif ( $plugin->opts->command eq 'interfaces' ) {

  # check the state of all interfaces
  check_interfaces($plugin);
} elsif ( $plugin->opts->command eq 'servicegroup' ) {

  # check the state of a servicegroup and its members
  check_servicegroup($plugin);
} elsif ( $plugin->opts->command eq 'license' ) {

  # check a installed license file
  check_license($plugin);
} elsif ( $plugin->opts->command eq 'hastatus' ) {

  # check the HA status of a node
  check_hastatus($plugin);
} elsif ( $plugin->opts->command eq 'ntp' ) {

  # check NTP status
  check_ntp($plugin);
} elsif ( $plugin->opts->command eq 'debug' ) {

  # dump the full response of the nitro api
  check_debug($plugin);
} else {

  # error, unkown command given
  $plugin->plugin_die( 'unkown command ' . $plugin->opts->command . ' given' );
}

sub add_arg {
  my $plugin = shift;
  my $arg    = shift;

  my $spec     = $arg->{'spec'};
  my $help     = $arg->{'usage'};
  my $default  = $arg->{'default'};
  my $required = $arg->{'required'};

  if ( defined $arg->{'desc'} ) {
    my @desc;

    if ( ref( $arg->{'desc'} ) ) {
      @desc = @{ $arg->{'desc'} };
    } else {
      @desc = ( $arg->{'desc'} );
    }

    foreach my $d (@desc) {
      $help .= "\n   $d";
    }
  }

  $plugin->add_arg(
    spec     => $spec,
    help     => $help,
    default  => $default,
    required => $required,
  );
}

sub nitro_client {

  my $plugin = shift;
  my $params = shift;

  my $lwp = LWP::UserAgent->new(
    env_proxy  => 1,
    keep_alive => 1,
    timeout    => $plugin->opts->timeout,
    ssl_opts   => {
      verify_hostname => 0,
      SSL_verify_mode => 0
    },
  );

  my $protocol = 'http://';

  if ( $plugin->opts->ssl ) {
    $protocol = 'https://';
  }

  my $port = '';

  if ( $plugin->opts->port ) {
    $port = ':' . $plugin->opts->port;
  }

  my $url = $protocol . $plugin->opts->hostname . $port . '/nitro/' . $plugin->opts->api . '/' . $params->{'endpoint'} . '/' . $params->{'objecttype'};

  if ( $params->{'objectname'} && $params->{'objectname'} ne '' ) {
    $url = $url . '/' . uri_escape( uri_escape( $params->{'objectname'} ) );
  }

  if ( $params->{'options'} && $params->{'options'} ne '' ) {
    $url = $url . '?' . $params->{'options'};
  }

  if ( $plugin->opts->verbose ) {
    print "debug: target url is $url\n";
  }

  my $request = HTTP::Request->new( GET => $url );

  $request->header( 'X-NITRO-USER', $plugin->opts->username );
  $request->header( 'X-NITRO-PASS', $plugin->opts->password );
  $request->header( 'Content-Type', 'application/vnd.com.citrix.netscaler.' . $params->{'objecttype'} . '+json' );

  my $response = $lwp->request($request);

  if ( $plugin->opts->verbose > 1 ) {
    print "debug: response of request is:\n";
    print Dumper( $response->content );
  }

  if ( HTTP::Status::is_error( $response->code ) ) {
    $plugin->plugin_die( $response->content );
  } else {
    $response = JSON->new->allow_blessed->convert_blessed->decode( $response->content );
  }

  if ( $plugin->opts->verbose > 2 ) {
    print "debug: json decoded response of request is:\n";
    print Dumper($response);
  }

  return $response;
}

sub check_state {
  my $plugin = shift;

  if ( !defined $plugin->opts->objecttype ) {
    $plugin->plugin_die( $plugin->opts->command . ': command requires objecttype parameter' );
  }

  my %counter;

  # special handling for objecttype server
  if ( $plugin->opts->objecttype eq 'server' ) {
    $counter{'ENABLED'}  = 0;
    $counter{'DISABLED'} = 0;
  } else {
    $counter{'UP'}             = 0;
    $counter{'DOWN'}           = 0;
    $counter{'OUT OF SERVICE'} = 0;
    $counter{'UNKOWN'}         = 0;

    # for servicegroups: PARTIAL-UP (non critical event)
    if ( $plugin->opts->objecttype eq 'servicegroup' ) {
      $counter{'PARTIAL-UP'} = 0;
    }
  }

  # performance data for service and vservers
  # if you want some performance data for your service groups please use the check_servicegroup command
  # see https://www.icinga.com/docs/icinga1/latest/de/perfdata.html
  my %perfdata;
  $perfdata{'totalrequests'}      = 'c';
  $perfdata{'requestsrate'}       = undef;
  $perfdata{'totalresponses'}     = 'c';
  $perfdata{'responsesrate'}      = undef;
  $perfdata{'totalrequestbytes'}  = 'B';
  $perfdata{'requestbytesrate'}   = undef;
  $perfdata{'totalresponsebytes'} = 'B';
  $perfdata{'responsebytesrate'}  = undef;

  my %params;

  my $field_name      = 'name';
  my $field_state     = 'state';
  my $enable_perfdata = 1;

  # well, i guess the citrix api developers were drunk
  if ( $plugin->opts->objecttype eq 'service' ) {
    $params{'endpoint'} = $plugin->opts->endpoint || 'config';
    $field_name         = 'name';
    $field_state        = 'svrstate';
    $enable_perfdata    = 0;
  } elsif ( $plugin->opts->objecttype eq 'servicegroup' ) {
    $params{'endpoint'} = $plugin->opts->endpoint || 'config';
    $field_name         = 'servicegroupname';
    $field_state        = 'servicegroupeffectivestate';
    $enable_perfdata    = 0;
  } elsif ( $plugin->opts->objecttype eq 'server' ) {
    $params{'endpoint'} = $plugin->opts->endpoint || 'config';
    $field_name         = 'name';
    $field_state        = 'state';
    $enable_perfdata    = 0;
  } else {
    $params{'endpoint'} = $plugin->opts->endpoint || 'stat';
  }

  $params{'objecttype'} = $plugin->opts->objecttype;
  $params{'objectname'} = $plugin->opts->objectname;
  $params{'options'}    = $plugin->opts->urlopts;

  my $response = nitro_client( $plugin, \%params );
  $response = $response->{ $plugin->opts->objecttype };

  # handle an empty response
  if ( !scalar($response) ) {
    if ( $params{'objectname'} && $params{'objectname'} ne '' ) {
      $plugin->plugin_exit( CRITICAL, $plugin->opts->command . ': no ' . $plugin->opts->objecttype . ' found in configuration' );
    } else {
      $plugin->plugin_exit( OK, $plugin->opts->command . ': no ' . $plugin->opts->objecttype . ' found in configuration' );
    }
  }

  # loop around, check states and increment the counters
  foreach my $response ( @{$response} ) {
    if ( defined( $plugin->opts->filter ) && $response->{$field_name} =~ $plugin->opts->filter ) {
      next;
    }

    if ( defined( $counter{ $response->{$field_state} } ) ) {
      $counter{ $response->{$field_state} }++;
    }
    if ( $response->{$field_state} eq 'UP' || $response->{$field_state} eq 'ENABLED' ) {
      $plugin->add_message( OK, $response->{$field_name} . ' ' . $response->{$field_state} . ';' );
    } elsif ( $response->{$field_state} eq 'PARTIAL-UP' || $response->{$field_state} eq 'DISABLED' ) {
      $plugin->add_message( WARNING, $response->{$field_name} . ' ' . $response->{$field_state} . ';' );
    } else {
      $plugin->add_message( CRITICAL, $response->{$field_name} . ' ' . $response->{$field_state} . ';' );
    }

    # add performance data only if we are dealing with a single object
    if ( defined( $plugin->opts->objectname ) && $enable_perfdata ) {
      foreach my $perfdata_field ( keys %perfdata ) {
        $plugin->add_perfdata(
          label => $response->{$field_name} . ' ' . $perfdata_field,
          value => $response->{$perfdata_field},
          uom   => $perfdata{$perfdata_field},
          min   => 0,
          max   => undef,
        );
      }
    }
  }

  # a global counter is pretty useless for a single object
  if ( !defined( $plugin->opts->objectname ) ) {
    foreach my $key ( keys %counter ) {
      $plugin->add_message( OK, $counter{$key} . ' ' . $key . ';' );
      $plugin->add_perfdata(
        label => $key,
        value => $counter{$key},
        uom   => undef,
        min   => 0,
        max   => undef,
      );
    }
  }

  my ( $code, $message ) = $plugin->check_messages;

  $plugin->plugin_exit( $code, $plugin->opts->command . ' ' . $plugin->opts->objecttype . ': ' . $message );
}

sub check_keyword {
  my $plugin                    = shift;
  my $type_of_string_comparison = shift;

  if ( !defined $plugin->opts->objecttype ) {
    $plugin->plugin_die( $plugin->opts->command . ': command requires parameter for objecttype' );
  }

  if ( !defined $plugin->opts->objectname ) {
    $plugin->plugin_die( $plugin->opts->command . ': command requires parameter for objectname' );
  }

  if ( !defined $plugin->opts->warning || !defined $plugin->opts->critical ) {
    $plugin->plugin_die( $plugin->opts->command . ': command requires parameter for warning and critical' );
  }

  if ( $type_of_string_comparison ne 'matches' && $type_of_string_comparison ne 'matches not' ) {
    $plugin->plugin_die( $plugin->opts->command . ': string can only be checked for "matches" and "matches not"' );
  }

  my %params;
  $params{'endpoint'}   = $plugin->opts->endpoint || 'stat';
  $params{'objecttype'} = $plugin->opts->objecttype;
  $params{'objectname'} = undef;
  $params{'options'}    = $plugin->opts->urlopts;

  my $response = nitro_client( $plugin, \%params );

  # handle and objecttype with an slash inside (e.g. nspartition/mypartition)
  if ( $params{'objecttype'} =~ /\// ) {
    my @objecttype_parts = split( '/', $params{'objecttype'}, 2 );
    $response = $response->{ $objecttype_parts[0] }[0];
  } else {
    $response = $response->{ $params{'objecttype'} };
  }

  if ( ref $response eq 'ARRAY' ) {
    my $response_id = 0;
    foreach $response ( @{$response} ) {
      foreach my $origin_objectname ( split( ',', $plugin->opts->objectname ) ) {

        my $objectname;
        my $objectname_id;
        my $description;
        my $label;

        # handling of the dot notation for sdx appliances (see #33)
        if ( $plugin->opts->objectname =~ /\./ ) {
          ( $objectname_id, $objectname ) = split( '.', $origin_objectname );

          if ( not defined( $response->{$objectname_id} ) ) {
            $plugin->nagios_die( $plugin->opts->command . ': object id "' . $objectname_id . '" not found in output.' );
          }

          $description = $params{'objecttype'} . '.' . $response->{$objectname_id} . '.' . $objectname;
        } else {
          $objectname = $origin_objectname;

          # use a custom label from a field in the response as perfdata label (see #56)
          if ( $plugin->opts->label ) {
            $label = $response->{ $plugin->opts->label };
          } else {
            $label = $response_id;
          }
          $description = $params{'objecttype'} . '.' . $origin_objectname . '[' . $label . ']';
        }

        if ( not defined( $response->{$objectname} ) ) {
          $plugin->plugin_die( $plugin->opts->command . ': object name "' . $objectname . '" not found in output.' );
        }

        # should we skip this label (see #56)?
        if ( defined( $plugin->opts->filter ) && $label =~ $plugin->opts->filter ) {
          next;
        }

        # limit parameter set (see #56)?
        if ( defined( $plugin->opts->limit ) && $label !~ $plugin->opts->limit ) {
          next;
        }

        if ( ( $type_of_string_comparison eq 'matches' && $response->{$objectname} eq $plugin->opts->critical )
          || ( $type_of_string_comparison eq 'matches not' && $response->{$objectname} ne $plugin->opts->critical ) )
        {
          $plugin->add_message( CRITICAL, $description . ': "' . $response->{$objectname} . '" ' . $type_of_string_comparison . ' keyword "' . $plugin->opts->critical . '"' );
        } elsif ( ( $type_of_string_comparison eq 'matches' && $response->{$objectname} eq $plugin->opts->warning )
          || ( $type_of_string_comparison eq 'matches not' && $response->{$objectname} ne $plugin->opts->warning ) )
        {
          $plugin->add_message( WARNING, $description . ': "' . $response->{$objectname} . '" ' . $type_of_string_comparison . ' keyword "' . $plugin->opts->warning . '"' );
        } else {
          $plugin->add_message( OK, $description . ': "' . $response->{$objectname} . '"' );
        }
        $response_id++;
      }
    }
  } elsif ( ref $response eq 'HASH' ) {
    foreach ( split( ',', $plugin->opts->objectname ) ) {
      if ( ( $type_of_string_comparison eq 'matches' && $response->{$_} eq $plugin->opts->critical ) || ( $type_of_string_comparison eq 'matches not' && $response->{$_} ne $plugin->opts->critical ) )
      {
        $plugin->add_message( CRITICAL, $plugin->opts->objecttype . '.' . $_ . ': "' . $response->{$_} . '" ' . $type_of_string_comparison . ' keyword "' . $plugin->opts->critical . '";' );
      } elsif ( ( $type_of_string_comparison eq 'matches' && $response->{$_} eq $plugin->opts->warning )
        || ( $type_of_string_comparison eq 'matches not' && $response->{$_} ne $plugin->opts->warning ) )
      {
        $plugin->add_message( WARNING, $plugin->opts->objecttype . '.' . $_ . ': "' . $response->{$_} . '" ' . $type_of_string_comparison . ' keyword "' . $plugin->opts->warning . '";' );
      } else {
        $plugin->add_message( OK, $plugin->opts->objecttype . '.' . $_ . ': ' . $response->{$_} . ';' );
      }
    }
  } else {
    $plugin->plugin_die( $plugin->opts->command . ': unable to parse data. Returned data is not a HASH or ARRAY!' );
  }

  my ( $code, $message ) = $plugin->check_messages( join => "; ", join_all => "; " );
  $plugin->plugin_exit( $code, 'keyword ' . $type_of_string_comparison . ': ' . $message );
}

sub check_sslcert {
  my $plugin = shift;

  # defaults for warning and critical
  my $warning  = $plugin->opts->warning  || 30;
  my $critical = $plugin->opts->critical || 10;

  my %params;
  $params{'endpoint'}   = $plugin->opts->endpoint   || 'config';
  $params{'objecttype'} = $plugin->opts->objecttype || 'sslcertkey';
  $params{'objectname'} = $plugin->opts->objectname;
  $params{'options'}    = $plugin->opts->urlopts;

  my $response = nitro_client( $plugin, \%params );
  $response = $response->{ $params{'objecttype'} };

  foreach $response ( @{$response} ) {
    if ( defined( $plugin->opts->filter ) && $response->{certkey} =~ $plugin->opts->filter ) {
      next;
    }

    if ( $response->{daystoexpiration} <= 0 ) {
      $plugin->add_message( CRITICAL, $response->{certkey} . ' expired;' );
    } elsif ( $response->{daystoexpiration} <= $critical ) {
      $plugin->add_message( CRITICAL, $response->{certkey} . ' expires in ' . $response->{daystoexpiration} . ' days;' );
    } elsif ( $response->{daystoexpiration} <= $warning ) {
      $plugin->add_message( WARNING, $response->{certkey} . ' expires in ' . $response->{daystoexpiration} . ' days;' );
    }
  }

  my ( $code, $message ) = $plugin->check_messages;

  if ( $code == OK ) {
    $plugin->plugin_exit( $code, $plugin->opts->command . ': certificate lifetime OK' );
  } else {
    $plugin->plugin_exit( $code, $plugin->opts->command . ': ' . $message );
  }
}

sub check_staserver {
  my $plugin = shift;

  my %params;
  $params{'endpoint'}   = $plugin->opts->endpoint   || 'config';
  $params{'objectname'} = $plugin->opts->objectname || '';
  $params{'options'}    = $plugin->opts->urlopts;

  if ( $params{'objectname'} eq '' ) {
    $params{'objecttype'} = $plugin->opts->objecttype || 'vpnglobal_staserver_binding';
  } else {
    $params{'objecttype'} = $plugin->opts->objecttype || 'vpnvserver_staserver_binding';
  }

  my $response = nitro_client( $plugin, \%params );
  $response = $response->{ $params{'objecttype'} };

  if ( !scalar($response) ) {
    $plugin->plugin_exit( CRITICAL, $plugin->opts->command . ': no staserver found in configuration' );
  }

  # return critical if all staservers are down at once
  my $critical = 1;

  # check if any stas are in down state
  foreach $response ( @{$response} ) {
    if ( defined( $plugin->opts->filter ) && $response->{'staserver'} =~ $plugin->opts->filter ) {
      next;
    }

    if ( $response->{'staauthid'} eq '' ) {
      $plugin->add_message( WARNING, $response->{'staserver'} . ' unavailable;' );
    } else {
      $plugin->add_message( OK, $response->{'staserver'} . ' OK (' . $response->{'staauthid'} . ');' );
      $critical = 0;
    }
  }

  my ( $code, $message ) = $plugin->check_messages;

  if ( $critical == 1 ) { $code = CRITICAL; }

  $plugin->plugin_exit( $code, $plugin->opts->command . ': ' . $message );
}

sub check_nsconfig {
  my $plugin = shift;

  my %params;
  $params{'endpoint'}   = $plugin->opts->endpoint   || 'config';
  $params{'objecttype'} = $plugin->opts->objecttype || 'nsconfig';
  $params{'objectname'} = undef;
  $params{'options'}    = $plugin->opts->urlopts;

  my $response = nitro_client( $plugin, \%params );
  $response = $response->{ $params{'objecttype'} };

  if ( !defined $response->{'configchanged'} || $response->{'configchanged'} ) {
    $plugin->plugin_exit( WARNING, $plugin->opts->command . ': unsaved configuration changes' );
  } else {
    $plugin->plugin_exit( OK, $plugin->opts->command . ': no unsaved configuration changes' );
  }
}

sub get_hardware_info {
  my $plugin = shift;

  my %params;
  $params{'endpoint'}   = 'config';
  $params{'objecttype'} = 'nshardware';
  $params{'objectname'} = undef;
  $params{'options'}    = $plugin->opts->urlopts;

  my $response = nitro_client( $plugin, \%params );
  $response = $response->{ $params{'objecttype'} };

  $plugin->add_message( OK, 'Platform: ' . $response->{'hwdescription'} . ' ' . $response->{'sysid'} . ';' );
  $plugin->add_message( OK, 'Manufactured on: ' . $response->{'manufactureyear'} . '/' . $response->{'manufacturemonth'} . '/' . $response->{'manufactureday'} . ';' );
  $plugin->add_message( OK, 'CPU: ' . $response->{'cpufrequncy'} . 'MHz;' );
  $plugin->add_message( OK, 'Serial no: ' . $response->{'serialno'} . ';' );

  $params{'objecttype'} = 'nsversion';

  $response = nitro_client( $plugin, \%params );
  $response = $response->{ $params{'objecttype'} };

  $plugin->add_message( OK, 'Build Version: ' . $response->{'version'} . ';' );

  my ( $code, $message ) = $plugin->check_messages;
  $plugin->plugin_exit( $code, $plugin->opts->command . ': ' . $message );
}

sub check_threshold_and_get_perfdata {
  my $plugin    = shift;
  my $direction = shift;

  my %params;
  $params{'endpoint'}   = $plugin->opts->endpoint || 'stat';
  $params{'objecttype'} = $plugin->opts->objecttype;
  $params{'objectname'} = undef;
  $params{'options'}    = $plugin->opts->urlopts;

  if ( !defined $plugin->opts->objecttype ) {
    $plugin->plugin_die( $plugin->opts->command . ': command requires parameter for objecttype' );
  }

  if ( !defined $plugin->opts->objectname ) {
    $plugin->plugin_die( $plugin->opts->command . ': command requires parameter for objectname' );
  }

  if ( $direction ne 'above' && $direction ne 'below' ) {
    $plugin->plugin_die( $plugin->opts->command . ': threshold can only be checked for "above" and "below"' );
  }

  my $response = nitro_client( $plugin, \%params );

  # handle and objecttype with an slash inside (e.g. nspartition/mypartition)
  if ( $params{'objecttype'} =~ /\// ) {
    my @objecttype_parts = split( '/', $params{'objecttype'}, 2 );
    $response = $response->{ $objecttype_parts[0] }[0];
  } else {
    $response = $response->{ $params{'objecttype'} };
  }

  if ( ref $response eq 'ARRAY' ) {
    my $response_id = 0;
    foreach $response ( @{$response} ) {
      foreach my $origin_objectname ( split( ',', $plugin->opts->objectname ) ) {

        my $objectname;
        my $objectname_id;
        my $description;
        my $label;

        # handling of the dot notation for sdx appliances (see #33)
        if ( $plugin->opts->objectname =~ /\./ ) {
          ( $objectname_id, $objectname ) = split( '.', $origin_objectname );

          if ( not defined( $response->{$objectname_id} ) ) {
            $plugin->nagios_die( $plugin->opts->command . ': object id "' . $objectname_id . '" not found in output.' );
          }

          $description = $params{'objecttype'} . '.' . $response->{$objectname_id} . '.' . $objectname;
        } else {
          $objectname = $origin_objectname;

          # use a custom label from a field in the response as perfdata label (see #56)
          if ( $plugin->opts->label ) {
            $label = $response->{ $plugin->opts->label };
          } else {
            $label = $response_id;
          }
          $description = $params{'objecttype'} . '.' . $origin_objectname . '[' . $label . ']';
        }

        # should we skip this label (see #56)?
        if ( defined( $plugin->opts->filter ) && $label =~ $plugin->opts->filter ) {
          next;
        }

        # limit parameter set (see #56)?
        if ( defined( $plugin->opts->limit ) && $label !~ $plugin->opts->limit ) {
          next;
        }

        if ( not defined( $response->{$objectname} ) ) {
          $plugin->plugin_die( $plugin->opts->command . ': object name "' . $objectname . '" not found in output.' );
        }

        # check thresholds
        if ( defined $plugin->opts->critical && ( $direction eq 'above' && $response->{$objectname} >= $plugin->opts->critical )
          || ( $direction eq 'below' && $response->{$objectname} <= $plugin->opts->critical ) )
        {
          $plugin->add_message( CRITICAL, $description . ' is ' . $direction . ' threshold (current: ' . $response->{$objectname} . ', critical: ' . $plugin->opts->critical . ')' );
        } elsif ( defined $plugin->opts->warning && ( $direction eq 'above' && $response->{$objectname} >= $plugin->opts->warning )
          || ( $direction eq 'below' && $response->{$objectname} <= $plugin->opts->warning ) )
        {
          $plugin->add_message( WARNING, $description . ' is ' . $direction . ' threshold (current: ' . $response->{$objectname} . ', warning: ' . $plugin->opts->warning . ')' );
        } else {
          $plugin->add_message( OK, $description . ': ' . $response->{$objectname} );
        }

        $plugin->add_perfdata(
          label    => "'" . $description . "'",
          value    => $response->{$objectname},
          min      => undef,
          max      => undef,
          warning  => $plugin->opts->warning,
          critical => $plugin->opts->critical,
        );
      }
      $response_id++;
    }
  } elsif ( ref $response eq 'HASH' ) {
    foreach my $objectname ( split( ',', $plugin->opts->objectname ) ) {
      if ( not defined( $response->{$objectname} ) ) {
        $plugin->plugin_die( $plugin->opts->command . ': object name "' . $objectname . '" not found in output.' );
      }

      # check thresholds
      if ( defined $plugin->opts->critical && ( $direction eq 'above' && $response->{$objectname} >= $plugin->opts->critical )
        || ( $direction eq 'below' && $response->{$objectname} <= $plugin->opts->critical ) )
      {
        $plugin->add_message( CRITICAL,
          $params{'objecttype'} . '.' . $objectname . ' is ' . $direction . ' threshold (current: ' . $response->{$objectname} . ', critical: ' . $plugin->opts->critical . ')' );
      } elsif ( defined $plugin->opts->warning && ( $direction eq 'above' && $response->{$objectname} >= $plugin->opts->warning )
        || ( $direction eq 'below' && $response->{$objectname} <= $plugin->opts->warning ) )
      {
        $plugin->add_message( WARNING,
          $params{'objecttype'} . '.' . $objectname . ' is ' . $direction . ' threshold (current: ' . $response->{$objectname} . ', warning: ' . $plugin->opts->warning . ')' );
      } else {
        $plugin->add_message( OK, $params{'objecttype'} . '.' . $objectname . ': ' . $response->{$objectname} );
      }

      $plugin->add_perfdata(
        label    => "'" . $params{'objecttype'} . '.' . $objectname . "'",
        value    => $response->{$objectname},
        min      => undef,
        max      => undef,
        warning  => $plugin->opts->warning,
        critical => $plugin->opts->critical,
      );
    }
  } else {
    $plugin->plugin_die( $plugin->opts->command . ': unable to parse data. Returned data is not a HASH or ARRAY!' );
  }

  my ( $code, $message ) = $plugin->check_messages( join => "; ", join_all => "; " );
  $plugin->plugin_exit( $code, $plugin->opts->command . ': ' . $message );
}

sub check_interfaces {
  my $plugin = shift;
  my @interface_errors;

  my %params;
  $params{'endpoint'}   = 'config';
  $params{'objecttype'} = 'interface';
  $params{'objectname'} = undef;
  $params{'options'}    = $plugin->opts->urlopts;

  my $response = nitro_client( $plugin, \%params );

  foreach my $interface ( @{ $response->{'Interface'} } ) {
    if ( defined( $plugin->opts->filter ) && $interface->{'devicename'} =~ $plugin->opts->filter ) {
      next;
    }

    my $interface_state = OK;

    my $interface_speed = 'N/A';
    if ( $interface->{'actspeed'} ) { $interface_speed = $interface->{'actspeed'}; }

    if ( $interface->{'linkstate'} != 1 ) {
      push( @interface_errors, 'interface ' . $interface->{'devicename'} . " has linkstate \"DOWN\"" );
      $interface_state = CRITICAL;
    }
    if ( $interface->{'intfstate'} != 1 ) {
      push( @interface_errors, 'interface ' . $interface->{'devicename'} . " has intstate \"DOWN\"" );
      $interface_state = CRITICAL;
    }
    if ( $interface->{'state'} ne 'ENABLED' ) {
      push( @interface_errors, 'interface ' . $interface->{'devicename'} . " has state \"" . $interface->{'state'} . "\"" );
      $interface_state = CRITICAL;
    }

    $plugin->add_message( $interface_state,
          'device: '
        . $interface->{'devicename'}
        . ' (speed: '
        . $interface_speed
        . ', MTU: '
        . $interface->{'actualmtu'}
        . ', VLAN: '
        . $interface->{'vlan'}
        . ', type: '
        . $interface->{'intftype'} . ') '
        . $interface->{'state'}
        . ';' );

    $plugin->add_perfdata(
      label => "\'" . $interface->{'devicename'} . ".rxbytes'",
      value => $interface->{'rxbytes'} . 'B'
    );
    $plugin->add_perfdata(
      label => "\'" . $interface->{'devicename'} . ".txbytes'",
      value => $interface->{'txbytes'} . 'B'
    );
    $plugin->add_perfdata(
      label => "\'" . $interface->{'devicename'} . ".rxerrors'",
      value => $interface->{'rxerrors'} . 'c'
    );
    $plugin->add_perfdata(
      label => "\'" . $interface->{'devicename'} . ".txerrors'",
      value => $interface->{'txerrors'} . 'c'
    );
  }

  my ( $code, $message ) = $plugin->check_messages;
  if ( scalar @interface_errors != 0 ) {
    $message = join( ', ', @interface_errors ) . ' - ' . $message;
  }
  $plugin->plugin_exit( $code, $plugin->opts->command . ': ' . $message );
}

sub check_servicegroup {
  my $plugin = shift;
  my @servicegroup_errors;

  # define quorum (in percent) of working servicegroup members
  my $member_quorum_warning  = $plugin->opts->warning  || '90';
  my $member_quorum_critical = $plugin->opts->critical || '50';

  my %member_state;

  my %params;
  $params{'endpoint'}   = 'config';
  $params{'objecttype'} = 'servicegroup';
  $params{'objectname'} = $plugin->opts->objectname;
  $params{'options'}    = $plugin->opts->urlopts;

  if ( not defined( $plugin->opts->objectname ) ) {
    $plugin->plugin_die( $plugin->opts->command . ': no object name "-n" set' );
  }

  my %healthy_servicegroup_states;
  $healthy_servicegroup_states{'state'}                      = 'ENABLED';
  $healthy_servicegroup_states{'servicegroupeffectivestate'} = 'UP';
  $healthy_servicegroup_states{'monstate'}                   = 'ENABLED';
  $healthy_servicegroup_states{'healthmonitor'}              = 'YES';

  my %healthy_servicegroup_member_states;
  $healthy_servicegroup_member_states{'state'}    = 'ENABLED';
  $healthy_servicegroup_member_states{'svrstate'} = 'UP';

  my $response              = nitro_client( $plugin, \%params );
  my $servicegroup_response = $response->{ $params{'objecttype'} };
  my $servicegroup_state    = OK;

  # check servicegroup health status
  foreach my $servicegroup_response ( @{$servicegroup_response} ) {

    foreach my $servicegroup_check_key ( keys %healthy_servicegroup_states ) {

      if ( $servicegroup_response->{$servicegroup_check_key} ne $healthy_servicegroup_states{$servicegroup_check_key} ) {
        push( @servicegroup_errors,
          'servicegroup ' . $servicegroup_response->{'servicegroupname'} . ' "' . $servicegroup_check_key . '" is: ' . $healthy_servicegroup_states{$servicegroup_check_key} );
      }
    }
    $plugin->add_message( OK,
      $servicegroup_response->{'servicegroupname'} . ' (' . $servicegroup_response->{'servicetype'} . ') - state: ' . $servicegroup_response->{'servicegroupeffectivestate'} . ' -' );
  }

  # get servicegroup members status
  $params{'objecttype'} = 'servicegroup_servicegroupmember_binding';

  $response = nitro_client( $plugin, \%params );
  my $servicegroup_members_response = $response->{ $params{'objecttype'} };

  # check servicegroup members health status
  foreach my $servicegroup_members_response ( @{$servicegroup_members_response} ) {

    foreach my $servicegroup_members_check_key ( keys %healthy_servicegroup_member_states ) {

      if ( $servicegroup_members_response->{$servicegroup_members_check_key} ne $healthy_servicegroup_member_states{$servicegroup_members_check_key} ) {
        push( @servicegroup_errors,
              'servicegroup member '
            . $servicegroup_members_response->{'servername'} . ' "'
            . $servicegroup_members_check_key . '" is '
            . $healthy_servicegroup_member_states{$servicegroup_members_check_key} );
        $member_state{ $servicegroup_members_response->{'servername'} } = 'DOWN';
      }
    }
    if ( not defined $member_state{ $servicegroup_members_response->{'servername'} } ) {
      $member_state{ $servicegroup_members_response->{'servername'} } = "UP";
    }
    $plugin->add_message( OK,
          $servicegroup_members_response->{'servername'} . ' ('
        . $servicegroup_members_response->{'ip'} . ':'
        . $servicegroup_members_response->{'port'} . ') is '
        . $servicegroup_members_response->{'svrstate'}
        . ',' );
  }

  # count states
  my $members_up   = 0;
  my $members_down = 0;
  foreach my $member_state_key ( keys %member_state ) {
    if ( $member_state{$member_state_key} eq 'DOWN' ) {
      $members_down++;
    } else {
      $members_up++;
    }
  }

  # check quorum
  my $member_quorum = sprintf( '%1.2f', 100 / ( $members_up + $members_down ) * $members_up );

  if ( $member_quorum <= $member_quorum_critical ) {
    $servicegroup_state = CRITICAL;
  } elsif ( $member_quorum <= $member_quorum_warning ) {
    $servicegroup_state = WARNING;
  }

  $plugin->add_message( OK, 'member quorum: ' . $member_quorum . '% (UP/DOWN): ' . $members_up . '/' . $members_down );

  $plugin->add_perfdata(
    label    => "'" . $plugin->opts->objectname . ".member_quorum'",
    value    => $member_quorum . '%',
    min      => 0,
    max      => 100,
    warning  => $member_quorum_warning,
    critical => $member_quorum_critical,
  );

  my ( $code, $message ) = $plugin->check_messages;
  if ( scalar @servicegroup_errors != 0 ) {
    $message = join( ', ', @servicegroup_errors ) . ' - ' . $message;
  }
  $plugin->plugin_exit( $servicegroup_state, $plugin->opts->command . ': ' . $message );
}

sub check_license {
  my $plugin = shift;

  my %params;
  $params{'endpoint'}   = $plugin->opts->endpoint || 'config';
  $params{'objecttype'} = 'systemfile';
  $params{'options'}    = $plugin->opts->urlopts;

  if ( !defined $plugin->opts->warning || !$plugin->opts->critical ) {
    $plugin->plugin_die( $plugin->opts->command . ': command requires parameter for warning and critical' );
  }

  my $response;
  my @stripped;
  my $timepiece;
  my $licfiles;

  if ( !defined $plugin->opts->objectname ) {
    $params{'options'} = 'args=filelocation:' . uri_escape('/nsconfig/license');
    $response          = nitro_client( $plugin, \%params );
    $licfiles          = join( ",", map { $_->{'filename'} } grep { $_->{'filename'} =~ m/\.lic$/ } @{ $response->{'systemfile'} } );
  } else {
    $licfiles = $plugin->opts->objectname;
  }

  foreach ( split( ',', $licfiles ) ) {
    $params{'options'} = 'args=filelocation:' . uri_escape('/nsconfig/license') . ',filename:' . uri_escape($_);

    $response = nitro_client( $plugin, \%params );

    foreach ( split( "\n", decode_base64( $response->{'systemfile'}[0]->{'filecontent'} ) ) ) {
      if ( $_ =~ /^INCREMENT .*/ ) {
        @stripped = split( ' ', $_ );

        # date format in license file, e.g. 18-jan-2018
        if ( $stripped[4] ne "permanent" ) {

          $timepiece = Time::Piece->strptime( ( $stripped[4], '%d-%b-%Y' ) );

          if ( $timepiece->epoch - time < ( 60 * 60 * 24 * $plugin->opts->critical ) ) {
            $plugin->add_message( CRITICAL, $stripped[1] . ' expires on ' . $stripped[4] . ';' );
          } elsif ( $timepiece->epoch - time < ( 60 * 60 * 24 * $plugin->opts->warning ) ) {
            $plugin->add_message( WARNING, $stripped[1] . ' expires on ' . $stripped[4] . ';' );
          } else {
            $plugin->add_message( OK, $stripped[1] . ' expires on ' . $stripped[4] . ';' );
          }
        } else {
          $plugin->add_message( OK, $stripped[1] . ' never expires;' );
        }
      }
    }
  }

  my ( $code, $message ) = $plugin->check_messages;
  $plugin->plugin_exit( $code, $plugin->opts->command . ': ' . $message );
}

sub check_hastatus {
  my $plugin = shift;

  my %params;
  $params{'endpoint'}   = $plugin->opts->endpoint   || 'stat';
  $params{'objecttype'} = $plugin->opts->objecttype || 'hanode';
  $params{'objectname'} = $plugin->opts->objecttype;
  $params{'options'}    = $plugin->opts->urlopts;

  my $response = nitro_client( $plugin, \%params );
  $response = $response->{ $params{'objecttype'} };

  if ( $response->{'hacurstatus'} ne 'YES' ) {
    $plugin->plugin_exit( CRITICAL, $plugin->opts->command . ': appliance is not configured for high availability' );
  }

  my %hastatus;

  # current ha master state
  $hastatus{'PRIMARY'}       = OK;
  $hastatus{'SECONDARY'}     = OK;
  $hastatus{'STAYSECONDARY'} = WARNING;
  $hastatus{'CLAIMING'}      = WARNING;
  $hastatus{'FORCE CHANGE'}  = WARNING;

  # current ha status
  $hastatus{'UP'}               = OK;
  $hastatus{'DISABLED'}         = WARNING;
  $hastatus{'INIT'}             = WARNING;
  $hastatus{'DUMB'}             = WARNING;
  $hastatus{'PARTIALFAIL'}      = CRITICAL;
  $hastatus{'COMPLETEFAIL'}     = CRITICAL;
  $hastatus{'PARTIALFAILSSL'}   = CRITICAL;
  $hastatus{'ROUTEMONITORFAIL'} = CRITICAL;

  my $index = undef;

  foreach ( 'hacurmasterstate', 'hacurstate' ) {
    $index = uc( $response->{$_} );
    if ( defined( $hastatus{$index} ) ) {
      $plugin->add_message( $hastatus{$index}, $_ . ' ' . $response->{$_} . ';' );
    } else {
      $plugin->add_message( CRITICAL, $_ . ' ' . $response->{$_} . ';' );
    }
  }

  # make use of warning and critical parameters?
  if ( $response->{'haerrsyncfailure'} > 0 ) {
    $plugin->add_message( WARNING, 'ha sync failed ' . $response->{'haerrsyncfailure'} . ' times;' );
  }

  # make use of warning and critical parameters?
  if ( $response->{'haerrproptimeout'} > 0 ) {
    $plugin->add_message( WARNING, 'ha propagation timed out ' . $response->{'haerrproptimeout'} . ' times;' );
  }

  my $measurement = undef;

  foreach ( 'hatotpktrx', 'hatotpkttx', 'hapktrxrate', 'hapkttxrate' ) {
    if ( $_ eq 'hatotpktrx' || $_ eq 'hatotpkttx' ) {
      $measurement = 'c';
    } elsif ( $_ eq 'hapktrxrate' || $_ eq 'hapkttxrate' ) {
      $measurement = 'a';
    } else {
      $measurement = undef;
    }

    $plugin->add_perfdata(
      label    => $_,
      value    => $response->{$_},
      uom      => $measurement,
      min      => 0,
      max      => undef,
      warning  => undef,
      critical => undef,
    );
  }

  my ( $code, $message ) = $plugin->check_messages;
  $plugin->plugin_exit( $code, $plugin->opts->command . ': ' . $message );
}

sub check_ntp {
  my $plugin = shift;

  my %params;
  $params{'endpoint'}   = 'config';
  $params{'objecttype'} = 'ntpsync';
  $params{'objectname'} = undef;
  $params{'options'}    = $plugin->opts->urlopts;

  my $response = nitro_client( $plugin, \%params );
  $response = $response->{ $params{'objecttype'} };

  # check if syncing is even enabled
  if ( $response->{'state'} ne "ENABLED" ) {
    $plugin->plugin_exit( CRITICAL, $plugin->opts->command . ': Sync ' . $response->{'state'} );
  }

  my @stripped;
  my $ntp_check_status = OK;
  my %ntp_info;
  $ntp_info{'synced_source'}  = undef;
  $ntp_info{'synced_stratum'} = -1;
  $ntp_info{'synced_offset'}  = 'unknown';
  $ntp_info{'synced_jitter'}  = -1.000000;
  $ntp_info{'truechimers'}    = 0;

  $ntp_info{'threshold_offset_warning'}  = undef;
  $ntp_info{'threshold_offset_critical'} = undef;

  $ntp_info{'threshold_stratum_warning'}  = undef;
  $ntp_info{'threshold_stratum_critical'} = undef;

  $ntp_info{'threshold_jitter_warning'}  = undef;
  $ntp_info{'threshold_jitter_critical'} = undef;

  $ntp_info{'threshold_truechimers_warning'}  = undef;
  $ntp_info{'threshold_truechimers_critical'} = undef;

  # check ntp status
  $params{'objecttype'} = 'ntpstatus';

  $response = nitro_client( $plugin, \%params );
  $response = $response->{ $params{'objecttype'} }->{'response'};

  foreach ( split( "\n", $response ) ) {
    my $sync_status = substr( $_, 0, 1 );

    if ( $sync_status eq "=" ) {
      $ntp_info{'peer_list_started'} = 1;
      next;
    }
    if ( not defined $ntp_info{'peer_list_started'} ) { next; }

    @stripped = split( ' ', substr( $_, 1, length($_) ) );

    my $ntp_source       = $stripped[0];
    my $ntp_peer_stratum = $stripped[2];
    my $ntp_peer_offset  = $stripped[8];
    my $ntp_peer_jitter  = $stripped[9];

    if ( $sync_status eq "*" ) {
      $ntp_info{'synced_source'}  = $ntp_source;
      $ntp_info{'synced_stratum'} = $ntp_peer_stratum;
      $ntp_info{'synced_offset'}  = sprintf( "%1.6f", $ntp_peer_offset / 1000 );
      $ntp_info{'synced_jitter'}  = $ntp_peer_jitter;
    }

    if ( $sync_status eq "*" || $sync_status eq "+" || $sync_status eq "-" ) {
      $ntp_info{'truechimers'}++;
    }
  }

  if ( not defined $ntp_info{'synced_source'} ) {
    $ntp_check_status = CRITICAL;
    $plugin->add_message( OK,
          'Server not synchronized, Offset '
        . $ntp_info{'synced_offset'}
        . ', jitter='
        . $ntp_info{'synced_jitter'}
        . ', stratum='
        . $ntp_info{'synced_stratum'}
        . ', truechimers='
        . $ntp_info{'truechimers'} );
  } else {

    # get values for WARNING and CRITICAL
    foreach ( split( ',', $plugin->opts->warning ) ) {
      my ( $warning_option, $warning_value ) = split( '=', $_ );

      if ( $warning_option eq "o" ) { $ntp_info{'threshold_offset_warning'}      = sprintf( "%1.6f", $warning_value ); }
      if ( $warning_option eq "j" ) { $ntp_info{'threshold_jitter_warning'}      = sprintf( "%1.3f", $warning_value ); }
      if ( $warning_option eq "s" ) { $ntp_info{'threshold_stratum_warning'}     = $warning_value; }
      if ( $warning_option eq "t" ) { $ntp_info{'threshold_truechimers_warning'} = $warning_value; }
    }

    foreach ( split( ',', $plugin->opts->critical ) ) {
      my ( $critical_option, $critical_value ) = split( '=', $_ );

      if ( $critical_option eq "o" ) { $ntp_info{'threshold_offset_critical'}      = sprintf( "%1.6f", $critical_value ); }
      if ( $critical_option eq "j" ) { $ntp_info{'threshold_jitter_critical'}      = sprintf( "%1.3f", $critical_value ); }
      if ( $critical_option eq "s" ) { $ntp_info{'threshold_stratum_critical'}     = $critical_value; }
      if ( $critical_option eq "t" ) { $ntp_info{'threshold_truechimers_critical'} = $critical_value; }
    }

    # now check thresholds
    my $output_text;

    # offset
    $output_text = 'Offset ' . $ntp_info{'synced_offset'} . ' secs';
    if ( defined $ntp_info{'threshold_offset_critical'}
      && ( $ntp_info{'synced_offset'} >= $ntp_info{'threshold_offset_critical'} || $ntp_info{'synced_offset'} <= 0 - $ntp_info{'threshold_offset_critical'} ) )
    {
      $ntp_check_status = CRITICAL;
      $output_text .= ' (CRITCAL)';
    } elsif ( defined $ntp_info{'threshold_offset_warning'}
      && ( $ntp_info{'synced_offset'} >= $ntp_info{'threshold_offset_warning'} || $ntp_info{'synced_offset'} <= 0 - $ntp_info{'threshold_offset_warning'} ) )
    {
      if ( $ntp_check_status ne CRITICAL ) { $ntp_check_status = WARNING }
      $output_text .= ' (WARNING)';
    }
    $plugin->add_message( OK, $output_text );

    # jitter
    $output_text = 'jitter=' . $ntp_info{'synced_jitter'};
    if ( defined $ntp_info{'threshold_jitter_critical'} && $ntp_info{'synced_jitter'} >= $ntp_info{'threshold_jitter_critical'} ) {
      $ntp_check_status = CRITICAL;
      $output_text .= ' (CRITCAL)';
    } elsif ( defined $ntp_info{'threshold_jitter_warning'} && $ntp_info{'synced_jitter'} >= $ntp_info{'threshold_jitter_warning'} ) {
      if ( $ntp_check_status ne CRITICAL ) { $ntp_check_status = WARNING }
      $output_text .= ' (WARNING)';
    }
    $plugin->add_message( OK, $output_text );

    # stratum
    $output_text = 'stratum=' . $ntp_info{'synced_stratum'};
    if ( defined $ntp_info{'threshold_stratum_critical'} && $ntp_info{'synced_stratum'} > $ntp_info{'threshold_stratum_critical'} ) {
      $ntp_check_status = CRITICAL;
      $output_text .= ' (CRITCAL)';
    } elsif ( defined $ntp_info{'threshold_stratum_warning'} && $ntp_info{'synced_stratum'} > $ntp_info{'threshold_stratum_warning'} ) {
      if ( $ntp_check_status ne CRITICAL ) { $ntp_check_status = WARNING }
      $output_text .= ' (WARNING)';
    }
    $plugin->add_message( OK, $output_text );

    # truechimers
    $output_text = 'truechimers=' . $ntp_info{'truechimers'};
    if ( defined $ntp_info{'threshold_truechimers_critical'} && $ntp_info{'truechimers'} <= $ntp_info{'threshold_truechimers_critical'} ) {
      $ntp_check_status = CRITICAL;
      $output_text .= ' (CRITCAL)';
    } elsif ( defined $ntp_info{'threshold_truechimers_warning'} && $ntp_info{'truechimers'} <= $ntp_info{'threshold_truechimers_warning'} ) {
      if ( $ntp_check_status ne CRITICAL ) { $ntp_check_status = WARNING }
      $output_text .= ' (WARNING)';
    }
    $plugin->add_message( OK, $output_text );

    # add perfdata
    $plugin->add_perfdata(
      label    => "offset",
      value    => $ntp_info{'synced_offset'} . 's',
      min      => undef,
      max      => undef,
      warning  => $ntp_info{'threshold_offset_warning'},
      critical => $ntp_info{'threshold_offset_critical'},
    );
    $plugin->add_perfdata(
      label    => "jitter",
      value    => $ntp_info{'synced_jitter'},
      min      => 0,
      max      => undef,
      warning  => $ntp_info{'threshold_jitter_warning'},
      critical => $ntp_info{'threshold_jitter_critical'},
    );
    $plugin->add_perfdata(
      label    => "stratum",
      value    => $ntp_info{'synced_stratum'},
      min      => 0,
      max      => 16,
      warning  => $ntp_info{'threshold_stratum_warning'},
      critical => $ntp_info{'threshold_stratum_critical'},
    );
    $plugin->add_perfdata(
      label    => "truechimers",
      value    => $ntp_info{'truechimers'},
      min      => 0,
      max      => undef,
      warning  => $ntp_info{'threshold_truechimers_warning'},
      critical => $ntp_info{'threshold_truechimers_critical'},
    );
  }

  my ( $code, $message ) = $plugin->check_messages( join => ", ", join_all => ", " );
  $plugin->plugin_exit( $ntp_check_status, $plugin->opts->command . ': ' . $message );
}

sub check_debug {
  my $plugin = shift;

  my %params;
  $params{'endpoint'}   = $plugin->opts->endpoint || 'stat';
  $params{'objecttype'} = $plugin->opts->objecttype;
  $params{'objectname'} = $plugin->opts->objectname;
  $params{'options'}    = $plugin->opts->urlopts;

  my $response = nitro_client( $plugin, \%params );

  print Dumper($response);
}
