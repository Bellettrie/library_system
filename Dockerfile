FROM python:3.9

ENV PYTHONUNBUFFERED 1
RUN mkdir -p /opt/services/djangoapp/src

WORKDIR /opt/services/djangoapp/src

COPY . . 
RUN  pip install -r requirements.txt
RUN python manage.py collectstatic --no-input

RUN ls -lah
EXPOSE 8000
