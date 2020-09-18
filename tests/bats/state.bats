#!/usr/bin/env bats

# test state all objects at once
@test "check_netscaler with command state against all lbvservers" {
  run ./check_netscaler.pl -C state -o lbvserver
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 2 ]
  [[ ${output} = *"vs_lb_http_web_down DOWN"* ]]
}
@test "check_netscaler with command state against all csvservers" {
  run ./check_netscaler.pl -C state -o csvserver
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 2 ]
  [[ ${output} = *"vs_cs_ssl_web_down DOWN"* ]]
}
@test "check_netscaler with command state against all services" {
  run ./check_netscaler.pl -C state -o service
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 2 ]
  [[ ${output} = *"svc_http_dummy1 OUT OF SERVICE"* ]]
  [[ ${output} = *"svc_http_dummy2 OUT OF SERVICE"* ]]
}
@test "check_netscaler with command state against all servicegroups" {
  run ./check_netscaler.pl -C state -o servicegroup
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 2 ]
  [[ ${output} = *"sg_http_dummy OUT OF SERVICE"* ]]
}
@test "check_netscaler with command state against all servers" {
  run ./check_netscaler.pl -C state -o server
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 1 ]
  [[ ${output} = *"srv_dummy1 DISABLED"* ]]
  [[ ${output} = *"srv_dummy2 DISABLED"* ]]
}
