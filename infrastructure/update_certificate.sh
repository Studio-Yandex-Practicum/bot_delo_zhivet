#!/bin/bash

source .env && export HOST_NAME && export CERTBOT_EMAIL

readonly LETSENCRYPT_DIRECTORY=/root/delozhivet/nginx/letsencrypt

# Проверяем, запущен ли контейнер nginx в Docker Compose
if docker-compose -f docker-compose-test.yaml ps | grep -q "nginx"; then
    echo "Container nginx is running."
else
    echo "Container nginx is not running."
    exit 1 # Выходим из скрипта с кодом ошибки
fi

# if test -d "$LETSENCRYPT_DIRECTORY" &&
if [ -d "$LETSENCRYPT_DIRECTORY" ] &&
   [ "$(find "$LETSENCRYPT_DIRECTORY" -mindepth 1 -print -quit)" ] &&
   [ "$NEED_REBOOT_CONF_TRUE" = "FALSE" ];
then
    echo "Value NEED_REBOOT_CONF_TRUE=$NEED_REBOOT_CONF_TRUE"
    echo "Directory $LETSENCRYPT_DIRECTORY exists and is not empty."
    echo "HTTPS certificate already exists."
else
    echo "Value NEED_REBOOT_CONF_TRUE=$NEED_REBOOT_CONF_TRUE"
    echo "Directory $LETSENCRYPT_DIRECTORY does not exist, is empty or NEED_REBOOT_CONF_TRUE is TRUE."
    echo "Run certbot. Dry run!"
    # if [ $? -ne 0 ]; then
    docker-compose -f docker-compose-test.yaml exec nginx certbot certonly --dry-run --nginx --non-interactive --email ${CERTBOT_EMAIL} --agree-tos --no-eff-email -d ${HOST_NAME}
    # echo "Run certbot. Install a certificate in your current webserver!"
    # Install a certificate in your current webserver!
    # docker-compose -f docker-compose-test.yaml exec nginx certbot --nginx --non-interactive --email ${CERTBOT_EMAIL} --agree-tos --no-eff-email -d ${HOST_NAME}
    if [ $? -ne 0 ]; then
        # Код возврата не равен нулю, команда завершилась с ошибкой
        echo "Failed to run certbot, removing  all files of the $LETSENCRYPT_DIRECTORY directory."
        rm -r -d "${LETSENCRYPT_DIRECTORY:?}/"*
        echo "All files of the $LETSENCRYPT_DIRECTORY directory were deleted." >&2
#        exit 1
    else
        echo "Successfully received certificate."
        docker-compose -f docker-compose-test.yaml exec nginx nginx -s reload
        echo "Reloaded the nginx configuration."
        export NEED_REBOOT_CONF_TRUE="FALSE"
        echo "Set NEED_REBOOT_CONF_TRUE=FALSE"
    fi
fi
