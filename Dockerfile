# syntax=docker/dockerfile:1.4
FROM python:3.11-alpine
ARG HOST
# This contains the name given to the individual copy of the site that's running this one.
# This is so we can identify which specific copy of the site is healthy/unhealthy.
ENV MY_HOST_NAME=$HOST

WORKDIR /app 
COPY requirements_dockerized.txt /app
RUN pip3 install -r requirements_dockerized.txt --no-cache-dir
COPY . /app 
# copy entrypoint.sh
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# copy project
COPY . .
RUN rm -rf /statictarget/*
RUN python manage.py migrate
RUN python manage.py collectstatic
# run entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
