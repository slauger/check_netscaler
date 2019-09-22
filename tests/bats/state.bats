#!/usr/bin/env bats

# test state all objects at once
@test "check_netscaler with command state against all lbvservers" {
  run ./check_netscaler.pl -H ${NETSCALER_IP} -C state -o lbvserver
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 2 ]
  [[ ${output} = *"vs_lb_http_web_down DOWN"* ]]
}
@test "check_netscaler with command state against all csvservers" {
  run ./check_netscaler.pl -H ${NETSCALER_IP} -C state -o csvserver
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 2 ]
  [[ ${output} = *"vs_cs_ssl_web_down DOWN"* ]]
}
@test "check_netscaler with command state against all services" {
  run ./check_netscaler.pl -H ${NETSCALER_IP} -C state -o service
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 2 ]
  [[ ${output} = *"svc_http_web1 DOWN"* ]]
  [[ ${output} = *"svc_http_web2 DOWN"* ]]
  [[ ${output} = *"svc_http_web DOWN"* ]]
}
@test "check_netscaler with command state against all servicegroups" {
  run ./check_netscaler.pl -H ${NETSCALER_IP} -C state -o servicegroup
  echo "status = ${status}"
  echo "output = ${output}"
  [ ${status} -eq 2 ]
  [[ ${output} = *"sg_http_web1 DOWN"* ]]
  [[ ${output} = *"sg_http_web2 DOWN"* ]]
  [[ ${output} = *"sg_http_web3 DOWN"* ]]
}
