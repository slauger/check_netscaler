#!/usr/bin/env bats

@test "check_netscaler with command perfdata against all admin partitions" {
  run ./check_netscaler.pl -s -C perfdata -o nspartition -n memoryusagepcnt
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 0 ]
}
@test "check_netscaler with command perfdata snf multiple objectnames against all admin partitions" {
  run ./check_netscaler.pl -s -C perfdata -o nspartition -n memoryusagepcnt,maxbandwidth,maxmemory,dropsrate
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 0 ]
}
@test "check_netscaler with command perfdata against specific admin partitions" {
  run ./check_netscaler.pl -s -C perfdata -o nspartition/partition1 -n memoryusagepcnt 
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 0 ]
}
@test "check_netscaler with command perfdata and multiple objectnames against specific admin partitions" {
  run ./check_netscaler.pl -s -C perfdata -o nspartition/partition1 -n memoryusagepcnt,maxbandwidth,maxmemory,dropsrate
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 0 ]
}
@test "check_netscaler with command matches against all admin partitions" {
  run ./check_netscaler.pl -s -C matches -o nspartition -n partitionname -w partition1 -c partition1
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 2 ]
}
@test "check_netscaler with command matches against specific admin partitions" {
  run ./check_netscaler.pl -s -C matches -o nspartition/partition1 -n partitionname -w partition1 -c partition1
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 2 ]
}
