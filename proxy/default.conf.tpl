server {
    listen ${LISTEN_PORT};

    # Serve static files
    location /static/ {
        alias /vol/web/static/;
    }

    # Serve media files
    location /media/ {
        alias /vol/web/media/;
    }

    location / {
        uwsgi_pass              ${APP_HOST}:${APP_PORT};
        include                 /etc/nginx/uwsgi_params;
        client_max_body_size    10M;
    }
}