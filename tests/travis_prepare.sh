#!/bin/bash
# Travis CI Test for check_netscaler.pl
# https://github.com/slauger/check_netscaler

function deploy_nsconfig
{
  # auto accept ssh host key
  sshpass -p nsroot ssh -o StrictHostKeyChecking=no nsroot@${NETSCALER_IP} hostname

  # configure netscaler cpx
  sshpass -p nsroot scp tests/ns.conf nsroot@${NETSCALER_IP}:/home/nsroot/ns.conf
  sshpass -p nsroot ssh nsroot@${NETSCALER_IP} "/var/netscaler/bins/cli_script.sh /home/nsroot/ns.conf"
  sshpass -p nsroot scp tests/license/*.lic /nsconfig/license/
}

deploy_nsconfig
