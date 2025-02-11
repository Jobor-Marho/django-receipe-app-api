server {
    listen ${LISTEN_PORT} default_server;
    server_name _;

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

    # ✅ Corrected FastAPI proxy settings
    location /fastapi/ {
        proxy_pass https://fastapi-book-project-complete.onrender.com/;
        proxy_set_header Host fastapi-book-project-complete.onrender.com;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }

    # Block hidden files
    location ~ /\. {
        deny all;
    }
}
