#!/bin/bash
# Travis CI Test for check_netscaler.pl
# https://github.com/slauger/check_netscaler

set -xeo pipefail

function deploy_nsconfig
{
  # auto accept ssh host key
  sshpass -p nsroot ssh -o SendEnv=None -o StrictHostKeyChecking=no nsroot@${NETSCALER_HOST} echo

  # configure netscaler cpx
  sshpass -p nsroot ssh -o SendEnv=None nsroot@${NETSCALER_HOST} "mkdir -p /nsconfig/license"
  sshpass -p nsroot scp -o SendEnv=None tests/license/*.lic nsroot@${NETSCALER_HOST}:/nsconfig/license/
  sshpass -p nsroot scp -o SendEnv=None tests/ns.conf nsroot@${NETSCALER_HOST}:/home/nsroot/ns.conf
  sshpass -p nsroot ssh -o SendEnv=None nsroot@${NETSCALER_HOST} "/var/netscaler/bins/cli_script.sh /home/nsroot/ns.conf"
}

if [ -z "${NETSCALER_HOST}" ]; then
  echo "ERROR: NETSCALER_HOST not set"
  exit 1
fi

deploy_nsconfig
