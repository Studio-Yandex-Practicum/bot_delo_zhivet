FROM nginx:alpine

# Устанавливаем Certbot
RUN apk update && apk add --no-cache certbot certbot-nginx

# Add Cronjob
RUN echo "0	0	*	*	*	/usr/bin/certbot renew --quiet" >> /etc/crontabs/root

# Копируем конфигурационный файл nginx
COPY default.conf /etc/nginx/conf.d/default.conf

# Run crond (background) and nginx (foreground)
# CMD ["crond", "&&", "nginx", "-g", "'daemon off;'"]
CMD crond -b && nginx -g "daemon off;"
