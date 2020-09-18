#!/usr/bin/env bats

@test "check interfaces with additional label" {
  run ./check_netscaler.pl -s -C perfdata -o Interface -n rxbytesrate -L id
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 0 ]
  [[ ${output} = *"Interface.rxbytesrate[0/1]"* ]]
  [[ ${output} = *"Interface.rxbytesrate[LO/1]"* ]]
}
