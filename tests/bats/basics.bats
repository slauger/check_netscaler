#!/usr/bin/env bats
# Travis CI Test for check_netscaler.pl
# https://github.com/slauger/check_netscaler

# do some basic plugin tests
@test "check_netscaler with command sslcert" {
  run ./check_netscaler.pl -C sslcert
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 0 ]
}
@test "check_netscaler with command interfaces" {
  run ./check_netscaler.pl -C interfaces
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 0 ]
}
@test "check_netscaler with command nsconfig" {
  run ./check_netscaler.pl -C nsconfig
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 0 ]
}
@test "check_netscaler with command hastatus" {
  run ./check_netscaler.pl -C hastatus
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 2 ]
  [[ ${output} = *"appliance is not configured for high availability"* ]]
}
