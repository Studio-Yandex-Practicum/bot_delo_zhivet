#!/bin/bash

# Проверяем, запущен ли контейнер nginx в Docker Compose
if docker-compose ps | grep -q "nginx"; then
    echo "Container nginx is running."
    exit 1 # Выходим из скрипта с кодом ошибки
else
    echo "Container nginx is not running."
fi

readonly CERTBOT_STR="managed by Certbot"
readonly REBOOT_CONF_TRUE="REBOOT_CONF=TRUE"

# Путь до файла из репозитория
readonly SRC_FILE=~/test/infrastructure/nginx/delo.conf
# Путь до копии файла
readonly MAIN_FILE=~/test/nginx/delo.conf

if [ -e "$MAIN_FILE" ] && grep -q "$CERTBOT_STR" "$SRC_FILE"; then
  echo "The value '$CERTBOT_STR' is found in $MAIN_FILE."
  if grep -q "$REBOOT_CONF_TRUE" "$SRC_FILE"; then
        echo "The value '$REBOOT_CONF_TRUE' is found in $MAIN_FILE."
        echo "The certificate must be reloaded."
        export NEED_REBOOT_CONF_TRUE="TRUE"
    else
        echo "The value '$REBOOT_CONF_TRUE' is not found in $MAIN_FILE."
        echo "The certificate must not be reloaded."
        export NEED_REBOOT_CONF_TRUE="FALSE"
  fi
else
  echo "Value '$CERTBOT_STR' not found in $MAIN_FILE or file does not exist. Copying $SRC_FILE to $MAIN_FILE."
  cp -f "$SRC_FILE" "$MAIN_FILE"
  export NEED_REBOOT_CONF_TRUE="TRUE"
fi
