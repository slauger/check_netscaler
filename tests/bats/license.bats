#!/usr/bin/env bats

@test "check_netscaler with command license" {
  run ./check_netscaler.pl -H ${NETSCALER_IP} -C license
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 0 ]
}
@test "check_netscaler with command interfaces" {
  run ./check_netscaler.pl -H ${NETSCALER_IP} -C license -n FID_ab9cab9c_ab9c_ab9c_ab9c_ab9cab9cab9c.lic
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 0 ]
}
