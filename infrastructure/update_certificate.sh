#!/bin/bash

readonly LETSENCRYPT_DIRECTORY=/root/test/nginx/letsencrypt

# Проверяем, запущен ли контейнер nginx в Docker Compose
if docker-compose ps | grep -q "nginx"; then
    echo "Container nginx is running."
else
    echo "Container nginx is not running."
    exit 1 # Выходим из скрипта с кодом ошибки
fi

# if test -d "$LETSENCRYPT_DIRECTORY" &&
if [ -d "$LETSENCRYPT_DIRECTORY" ] &&
   [ "$(find "$LETSENCRYPT_DIRECTORY" -mindepth 1 -print -quit)" ] &&
   [ "$NEED_REBOOT_CONF" = "FALSE" ];
then
    echo "Value NEED_REBOOT_CONF=$NEED_REBOOT_CONF"
    echo "Directory $LETSENCRYPT_DIRECTORY exists and is not empty."
    echo "HTTPS certificate already exists."
else
    echo "Value NEED_REBOOT_CONF=$NEED_REBOOT_CONF"
    echo "Directory $LETSENCRYPT_DIRECTORY does not exist, is empty or NEED_REBOOT_CONF is TRUE."
    echo "Run certbot. Dry run!"
    docker-compose exec nginx certbot certonly --dry-run --nginx --non-interactive --email vasilekx8@yandex.ru --agree-tos --no-eff-email -d admin-delozhivet.sytes.net
    # echo "Run certbot. Install a certificate in your current webserver!"
    # Install a certificate in your current webserver!
    # docker-compose exec nginx certbot --nginx --non-interactive --email vasilekx8@yandex.ru --agree-tos --no-eff-email -d admin-delozhivet.sytes.net
    if [ $? -ne 0 ]; then
        # Код возврата не равен нулю, команда завершилась с ошибкой
        echo "Failed to run certbot, removing  all files of the $LETSENCRYPT_DIRECTORY directory."
        rm -r -d "${LETSENCRYPT_DIRECTORY:?}/"*
        echo "All files of the $LETSENCRYPT_DIRECTORY directory were deleted."
        exit 1
    else
        echo "Successfully received certificate."
        docker-compose exec nginx nginx -s reload
        echo "Reloaded the nginx configuration."
    fi
fi
