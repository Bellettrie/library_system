FROM python:3.6

ENV PYTHONUNBUFFERED 1
RUN mkdir -p /opt/services/djangoapp/src

WORKDIR /opt/services/djangoapp/src

COPY . /opt/services/djangoapp/src
RUN ls -lah
RUN cd /opt/services/djangoapp/src && pip install -r requirements.txt && python manage.py collectstatic --no-input --settings="bellettrie_library_system.settings_production" 

EXPOSE 8000
CMD ["gunicorn", "-c", "config/gunicorn/conf.py", "--bind", ":8000", "--chdir", "bellettrie_library_system", "bellettrie_library_system.wsgi:application"]
