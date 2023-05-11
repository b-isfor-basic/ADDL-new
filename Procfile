release: python3 manage.py migrate --noinput --skip-checks
release: python3 manage.py loaddata ./Locations/fixtures/data.json --skip-checks
release: python3 manage.py loaddata ./Members/fixtures/data.json --skip-checks
release: python3 manage.py loaddata ./Schedule/fixtures/data.json --skip-checks
release: python3 manage.py loaddata ./Scores/fixtures/data.json --skip-checks
web: gunicorn ADDL.wsgi