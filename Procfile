release: python manage.py migrate
release: python manage.py loaddata crm/fixtures/initial_data.json
web: gunicorn project2019.wsgi --env DJANGO_SETTINGS_MODULE=project2019.production --log-file -
