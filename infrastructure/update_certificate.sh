#!/bin/bash

source .env && export HOST_NAME && export CERTBOT_EMAIL && export PROJECT_FOLDER_PATH

readonly LETSENCRYPT_DIRECTORY=$PROJECT_FOLDER_PATH/nginx/letsencrypt
readonly TRUE="True"
readonly FALSE="False"

# Проверяем, запущен ли контейнер nginx в Docker Compose
if docker-compose -f docker-compose.yaml ps | grep -q "nginx"; then
    echo "Container nginx is running."
else
    echo "Container nginx is not running."
    exit 1 # Выходим из скрипта с кодом ошибки
fi


if [ -d "$LETSENCRYPT_DIRECTORY" ] &&
   [ "$(find "$LETSENCRYPT_DIRECTORY" -mindepth 1 -print -quit)" ] &&
   [ "$NEED_RELOAD_NGINX_CONFIG" = $FALSE ];
then
    echo "Value NEED_RELOAD_NGINX_CONFIG=$NEED_RELOAD_NGINX_CONFIG"
    echo "Directory $LETSENCRYPT_DIRECTORY exists and is not empty."
    echo "HTTPS certificate already exists."
else
    echo "Value NEED_RELOAD_NGINX_CONFIG=$NEED_RELOAD_NGINX_CONFIG"
    echo "Directory $LETSENCRYPT_DIRECTORY does not exist, is empty or NEED_RELOAD_NGINX_CONFIG is $TRUE."
    echo "Run certbot. Dry run!"
    docker-compose -f docker-compose.yaml exec nginx certbot certonly --dry-run --nginx --non-interactive --email "${CERTBOT_EMAIL}" --agree-tos --no-eff-email -d "${HOST_NAME}"
    # Install a certificate in your current webserver!
    # echo "Run certbot. Install a certificate in your current webserver!"
    # docker-compose -f docker-compose.yaml exec nginx certbot --nginx --non-interactive --email "${CERTBOT_EMAIL}" --agree-tos --no-eff-email -d "${HOST_NAME}"
    if [ $? -ne 0 ]; then
        # Код возврата не равен нулю, команда завершилась с ошибкой
        echo "Failed to run certbot, removing  all files of the $LETSENCRYPT_DIRECTORY directory."
        rm -r -d "${LETSENCRYPT_DIRECTORY:?}/"*
        echo "All files of the $LETSENCRYPT_DIRECTORY directory were deleted." >&2
#        exit 1
    else
        echo "Successfully received certificate."
        docker-compose -f docker-compose.yaml exec nginx nginx -s reload
        echo "Reloaded the nginx configuration."
        echo "Set NEED_RELOAD_NGINX_CONFIG=$FALSE"
        export NEED_RELOAD_NGINX_CONFIG=$FALSE
    fi
fi
