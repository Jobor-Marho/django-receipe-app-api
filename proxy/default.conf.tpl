server {
    listen ${LISTEN_PORT} ;


    # Serve static files
    location /static/ {
        alias /vol/static/;
    }

    # Serve media files
    location /media/ {
        alias /vol/static/;
    }

    # Proxy requests to Django (via uWSGI)
    location / {
        uwsgi_pass ${APP_HOST}:${APP_PORT};
        include /etc/nginx/uwsgi_params;
        client_max_body_size 10M;
    }


    # Block hidden files
    location ~ /\. {
        deny all;
    }
}
