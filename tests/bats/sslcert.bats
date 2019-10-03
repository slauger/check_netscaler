#!/usr/bin/env bats

# do some basic plugin tests
@test "check_netscaler with command sslcert" {
  run ./check_netscaler.pl -H ${NETSCALER_IP} -C sslcert
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 0 ]
}
