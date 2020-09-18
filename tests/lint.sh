#!/bin/bash

LINT_FILE=$(mktemp)

perltidy check_netscaler.pl > ${LINT_FILE}
diff check_netscaler.pl ${LINT_FILE}

echo

if [ "${?}" -eq 0 ]; then
  echo "OK: perltidy lint ok"
  exit 0
else
  echo "ERROR: please run perltidy, changes found"
  exit 1
fi
