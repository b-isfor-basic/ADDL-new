release: python3 manage.py flush
release: python3 manage.py makemigrations --noinput
release: python3 manage.py migrate --noinput
release: python3 manage.py loaddata db.json
web: gunicorn ADDL.wsgi