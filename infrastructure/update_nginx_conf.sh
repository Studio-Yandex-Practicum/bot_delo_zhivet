#!/bin/bash

source .env && export PROJECT_FOLDER_PATH && export RELOAD_NGINX_CONFIG

# Проверяем, запущен ли контейнер nginx в Docker Compose
if docker-compose -f docker-compose.yaml ps | grep -q "nginx"; then
    echo "Container nginx is running."
    exit 1 # Выходим из скрипта с кодом ошибки
else
    echo "Container nginx is not running."
fi

readonly CERTBOT_STR="managed by Certbot"
# Путь до файла из репозитория
readonly SRC_FILE=$PROJECT_FOLDER_PATH/infrastructure/nginx/delo.conf
# Путь до копии файла
readonly MAIN_FILE=$PROJECT_FOLDER_PATH/nginx/delo.conf
# Путь до копии MAIN_FILE, нужен для динамического конфигурирования nginx
readonly TEMP_MAIN_FILE=$PROJECT_FOLDER_PATH/nginx/delo.temp
readonly TRUE="True"
readonly FALSE="False"

if [ -e "$MAIN_FILE" ] && grep -q "$CERTBOT_STR" "$MAIN_FILE"; then
  echo "The value '$CERTBOT_STR' is found in $MAIN_FILE."
  if [ "$RELOAD_NGINX_CONFIG" = "$TRUE" ]; then
        echo "The env RELOAD_NGINX_CONFIG is $TRUE."
        echo "The certificate 'Let’s Encrypt' must be reloaded."
        #
        echo -e "Copying $SRC_FILE to $MAIN_FILE."
        cp -f "$SRC_FILE" "$MAIN_FILE"
        echo -e "Copying $MAIN_FILE to $TEMP_MAIN_FILE."
        cp -f "$MAIN_FILE" "$TEMP_MAIN_FILE"
        #
        export NEED_RELOAD_NGINX_CONFIG=$TRUE
    else
        echo "The env RELOAD_NGINX_CONFIG is $FALSE."
        echo "The certificate 'Let’s Encrypt' must not be reloaded."
        export NEED_RELOAD_NGINX_CONFIG=$FALSE
  fi
else
  echo -e "Value '$CERTBOT_STR' not found in $MAIN_FILE or file does not exist."
  echo -e "Copying $SRC_FILE to $MAIN_FILE."
  cp -f "$SRC_FILE" "$MAIN_FILE"
  echo -e "Copying $MAIN_FILE to $TEMP_MAIN_FILE."
  cp -f "$MAIN_FILE" "$TEMP_MAIN_FILE"
  export NEED_RELOAD_NGINX_CONFIG=$TRUE
fi
