release: python3 manage.py migrate --noinput --skip-checks
release: python3 manage.py loaddata fixture/data.json --app Locations --skip-checks --ignorenonexistent
release: python3 manage.py loaddata fixture/data.json --app Members --skip-checks --ignorenonexistent
release: python3 manage.py loaddata fixture/data.json --app Schedule --skip-checks --ignorenonexistent
release: python3 manage.py loaddata fixture/data.json --app Scores --skip-checks --ignorenonexistent
web: gunicorn ADDL.wsgi