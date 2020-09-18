#!/usr/bin/env bats

@test "check_netscaler with command license" {
  run ./check_netscaler.pl -C license -w 30 -c 10
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 0 ]
}
@test "check_netscaler with command license and explicit file" {
  run ./check_netscaler.pl -C license -n FID_ab9cab9c_ab9c_ab9c_ab9c_ab9cab9cab9c.lic -w 30 -c 10
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 0 ]
}
