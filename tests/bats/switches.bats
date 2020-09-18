#!/usr/bin/env bats

@test "check interfaces with additional label" {
  run ./check_netscaler.pl -s -C perfdata -o Interface -n rxbytesrate -L id
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 0 ]
  [[ ${output} = *"Interface.rxbytesrate[0/1]"* ]]
  [[ ${output} = *"Interface.rxbytesrate[0/2]"* ]]
}
@test "check interfaces with additional label and filter" {
  run ./check_netscaler.pl -s -C perfdata -o Interface -n rxbytesrate -L id -f '0.2'
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 0 ]
  [[ ${output} = *"Interface.rxbytesrate[0/1]"* ]]
  [[ ${output} != *"Interface.rxbytesrate[0/2]"* ]]
}
@test "check interfaces with additional label and limit" {
  run ./check_netscaler.pl -s -C perfdata -o Interface -n rxbytesrate -L id -l '0.1'
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 0 ]
  [[ ${output} = *"Interface.rxbytesrate[0/1]"* ]]
  [[ ${output} != *"Interface.rxbytesrate[0/2]"* ]]
}
@test "check interfaces with additional label, filter and limit" {
  run ./check_netscaler.pl -s -C perfdata -o Interface -n rxbytesrate -L id -l '0.1' -f '0.1'
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 0 ]
  [[ ${output} != *"Interface.rxbytesrate[0/1]"* ]]
  [[ ${output} != *"Interface.rxbytesrate[0/2]"* ]]
}
@test "check interfaces with additional label and custom perfdata seperator" {
  run ./check_netscaler.pl -s -C perfdata -o Interface -n rxbytesrate -L id --seperator=_
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 0 ]
  [[ ${output} = *"Interface_rxbytesrate[0/1]"* ]]
  [[ ${output} = *"Interface_rxbytesrate[0/2]"* ]]
}
