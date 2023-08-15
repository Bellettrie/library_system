# syntax=docker/dockerfile:1.4

FROM python:3.11-alpine
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

# run entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
