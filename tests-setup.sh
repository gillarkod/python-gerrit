#!/bin/bash

if [[ -n $(sudo docker ps -f status=running -f name=gerrit -q) ]]; then
  sudo docker kill gerrit
  sudo docker rm gerrit
fi
if [[ -n $(sudo docker ps -f status=running -f name=openldap -q) ]]; then
  sudo docker kill openldap
  sudo docker rm openldap
fi

sudo docker run \
  --detach \
  --publish 389:389 \
  --env LDAP_ORGANISATION="DOMAIN" \
  --env LDAP_DOMAIN="DOMAIN.COM" \
  --env LDAP_ADMIN_PASSWORD="randompassword" \
  --name openldap \
  osixia/openldap

until sudo docker logs openldap 2>&1 | grep -q "slapd starting"
  do sleep 1
done

sudo docker run \
  --detach \
  --publish 8080:8080 \
  --publish 29418:29418 \
  --env WEBURL=http://localhost:8080 \
  --link openldap:ldap \
  --env AUTH_TYPE=LDAP \
  --env LDAP_SERVER="ldap" \
  --env LDAP_ACCOUNTBASE="ou=people,dc=domain,dc=com" \
  --env LDAP_GROUPBASE="ou=groups,dc=domain,dc=com" \
  --env LDAP_USERNAME="cn=admin,dc=domain,dc=com" \
  --env LDAP_PASSWORD="randompassword" \
  --env LDAP_ACCOUNTFULLNAME='givenName' \
  --name gerrit \
  openfrontier/gerrit

until sudo docker logs gerrit 2>&1 | grep -q "Gerrit Code Review .* ready"
  do sleep 1
done

ldapadd -f tests/directory.ldif -D "cn=admin,dc=domain,dc=com" -w "randompassword" -x
