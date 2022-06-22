#! /usr/bin/env bash

BYPORT=/etc/authbind/byport

for PORT in 80 443
do
  sudo touch ${BYPORT}/${PORT}
  sudo chown "${USER}" ${BYPORT}/${PORT}
  sudo chmod 755 ${BYPORT}/${PORT}
done
