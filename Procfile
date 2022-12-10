release: python manage.py migrate
release: python manage.py collectstatic --no-input
web: gunicorn stdepaul.wsgi --log-file -
