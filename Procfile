release: python3 manage.py migrate --noinput --skip-checks
release: python3 manage.py loaddata Locations/data --format=json --app=Locations --skip-checks -i
release: python3 manage.py loaddata Members/data --format=json --app=Members --skip-checks -i
release: python3 manage.py loaddata Schedule/data --format=json --app=Schedule --skip-checks -i
release: python3 manage.py loaddata Scores/data --format=json --app=Scores --skip-checks -i
web: gunicorn ADDL.wsgi