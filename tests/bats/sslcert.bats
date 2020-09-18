#!/usr/bin/env bats

# do some basic plugin tests
@test "run with command sslcert" {
  run ./check_netscaler.pl -C sslcert
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 0 ]
}
