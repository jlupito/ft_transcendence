#le Dockerfile est facultatif dans le cas de la db, veillez
# a la bonne copie des volumes et data
FROM postgres

WORKDIR /app

COPY /srcs/postgresql/init.sql /docker-entrypoint-initdb.d/
RUN pg_ctl -D /var/lib/postgresql/data -l logfile start

CMD ["postgres"]
