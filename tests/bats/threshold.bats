#!/usr/bin/env bats

@test "check_netscaler with command system_memusagepcnt" {
  run ./check_netscaler.pl -s -C above -o system -n memusagepcnt -w 75 -c 80
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 0 ]
}
@test "check_netscaler with command system_cpuusagepcnt" {
  run ./check_netscaler.pl -s -C above -o system -n cpuusagepcnt,mgmtcpuusagepcnt -w 75 -c 80
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 0 ]
}
@test "check_netscaler with command system_diskperusage" {
  run ./check_netscaler.pl -s -C above -o system -n disk0perusage,disk1perusage -w 75 -c 80
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 0 ]
}
