#!bin/nash

echo "Starting django server"
python manage.py makemigrations
python manage.py migrate

python manage.py runserver 0.0.0.0:82
