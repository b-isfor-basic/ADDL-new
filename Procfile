release: python3 manage.py migrate --noinput --skip-checks
release: python3 manage.py loaddata --app Locations --skip-checks --ignorenonexistent
release: python3 manage.py loaddata --app Members --skip-checks --ignorenonexistent
release: python3 manage.py loaddata --app Schedule --skip-checks --ignorenonexistent
release: python3 manage.py loaddata --app Scores --skip-checks --ignorenonexistent
web: gunicorn ADDL.wsgi