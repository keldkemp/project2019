release: python manage.py migrate
web: gunicorn project2019.wsgi --env DJANGO_SETTINGS_MODULE=project2019.production --log-file -
