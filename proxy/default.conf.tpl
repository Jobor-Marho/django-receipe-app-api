server {
    listen ${LISTEN_PORT};

    # Serve static files
    location /static {
        alias /vol/static;
    }
    # serving media files
    location /media {
        alias /vol/static;
    }
    location / {
        uwsgi_pass              ${APP_HOST}:${APP_PORT};
        include                 /etc/nginx/uwsgi_params;
        client_max_body_size    10M;
    }

    # FastAPI application on Render
    location /fastapi/ {
        rewrite ^/fastapi(/.*)$ $1 break;
        proxy_pass https://fastapi-book-project-complete.onrender.com;  # Render URL
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ~ /\. {
        deny all;
    }
}