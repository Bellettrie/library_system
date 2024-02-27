FROM postgres:15.1-alpine

ARG DUMP_NAME
COPY "${DUMP_NAME}" /docker-entrypoint-initdb.d/dump.sql

