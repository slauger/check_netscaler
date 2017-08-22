#!/bin/bash
# Travis CI Test Script for check_netscaler.pl
# https://github.com/slauger/check_netscaler

# enable output for all commands
set -x

# get ipaddress from container id
CID=$(docker ps | grep netscalercpx | awk '{print $1}')
CIP=$(docker inspect ${CID} | grep IPAddress | cut -d '"' -f 4 | tail -n1)

# auto accept ssh host key
sshpass -p nsroot ssh -o StrictHostKeyChecking=no nsroot@${CIP} hostname

# configure netscaler cpx
sshpass -p nsroot scp tests/ns.conf nsroot@${CIP}:/home/nsroot/ns.conf
sshpass -p nsroot ssh nsroot@${CIP} "/var/netscaler/bins/cli_script.sh /home/nsroot/ns.conf"

# do some basic plugin tests
./check_netscaler.pl -H ${CIP} -C sslcert
./check_netscaler.pl -H ${CIP} -C interfaces
./check_netscaler.pl -H ${CIP} -C nsconfig
./check_netscaler.pl -H ${CIP} -C hastatus

# fails on vpx instances
#./check_netscaler.pl -H ${CIP} -C hwinfo

./check_netscaler.pl -H ${CIP} -s -C above -o system -n memusagepcnt -w 75 -c 80
./check_netscaler.pl -H ${CIP} -s -C above -o system -n cpuusagepcnt,mgmtcpuusagepcnt -w 75 -c 80
./check_netscaler.pl -H ${CIP} -s -C above -o system -n disk0perusage,disk1perusage -w 75 -c 80

# test state all objects at once
./check_netscaler.pl -H ${CIP} -C state -o lbvserver
./check_netscaler.pl -H ${CIP} -C state -o csvserver
./check_netscaler.pl -H ${CIP} -C state -o service
./check_netscaler.pl -H ${CIP} -C state -o servicegroup
./check_netscaler.pl -H ${CIP} -C state -o server

# test state of single objects
./check_netscaler.pl -H ${CIP} -C state -o lbvserver -n vs_lb_http_web1
./check_netscaler.pl -H ${CIP} -C state -o csvserver -n vs_cs_http_web1
./check_netscaler.pl -H ${CIP} -C state -o service -n svc_http_web1
./check_netscaler.pl -H ${CIP} -C state -o servicegroup -n sg_http_web1
./check_netscaler.pl -H ${CIP} -C state -o server -n srv_web1

# Everything OK
exit 0
