# syntax=docker/dockerfile:1.4
FROM python:3.14
# This contains the name given to the individual copy of the site that's running this one.
# This is so we can identify which specific copy of the site is healthy/unhealthy.

WORKDIR /app

# Install requirements
COPY requirements_production.txt /app
RUN pip3 install -r requirements_production.txt --no-cache-dir

COPY . /app 
# copy entrypoint.sh
COPY ./entrypoint.sh .
# Ready script for running
RUN sed -i 's/\r$//g' /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
# copy project
COPY . .

# Set default entrypoint to running the application start script
ENTRYPOINT ["/app/entrypoint.sh"]
