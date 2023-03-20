#!/bin/bash

source .env && export PROJECT_FOLDER_PATH

# Проверяем, запущен ли контейнер nginx в Docker Compose
if docker-compose -f docker-compose-test.yaml ps | grep -q "nginx"; then
    echo "Container nginx is running."
    exit 1 # Выходим из скрипта с кодом ошибки
else
    echo "Container nginx is not running."
fi

readonly CERTBOT_STR="managed by Certbot"
readonly REBOOT_CONF_TRUE="REBOOT_CONF=TRUE"

# Путь до файла из репозитория
readonly SRC_FILE=$PROJECT_FOLDER_PATH/infrastructure/nginx/delo.conf
# Путь до копии файла
readonly MAIN_FILE=$PROJECT_FOLDER_PATH/nginx/delo.conf
readonly TEMP_MAIN_FILE=$PROJECT_FOLDER_PATH/nginx/delo.temp

if [ -e "$MAIN_FILE" ] && grep -q "$CERTBOT_STR" "$MAIN_FILE"; then
  echo "The value '$CERTBOT_STR' is found in $MAIN_FILE."
  if grep -q "$REBOOT_CONF_TRUE" "$SRC_FILE"; then
        echo "The value '$REBOOT_CONF_TRUE' is found in $SRC_FILE."
        echo "The certificate must be reloaded."
        export NEED_REBOOT_CONF_TRUE="TRUE"
    else
        echo "The value '$REBOOT_CONF_TRUE' is not found in $SRC_FILE."
        echo "The certificate must not be reloaded."
        export NEED_REBOOT_CONF_TRUE="FALSE"
  fi
else
  echo -e "Value '$CERTBOT_STR' not found in $MAIN_FILE or file does not exist.\nCopying $SRC_FILE to $MAIN_FILE."
  cp -f "$SRC_FILE" "$MAIN_FILE"
  echo -e "Copying $MAIN_FILE to $TEMP_MAIN_FILE."
  cp -f "$MAIN_FILE" "$TEMP_MAIN_FILE"
  export NEED_REBOOT_CONF_TRUE="TRUE"
fi
