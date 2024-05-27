FROM nginx:latest

COPY nginx.conf /etc/nginx/nginx.conf

COPY cert.pem /etc/nginx/back/certs/cert.pem
COPY key.pem /etc/nginx/back/certs/key.pem

EXPOSE 443