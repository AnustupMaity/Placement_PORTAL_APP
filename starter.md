Steps to Run 

1. Start Redis
redis-server

2. Packages Install
cd  to the "backend" folder
py -m pip install -r requirements.txt

3. Backend
cd  to the "backend" folder
py app.py

4. Start Celery Worker - background work
cd  to the "backend" folder
py -m celery -A app:celery worker --loglevel=info --pool=solo

5.  Celery Beat - scheduled work
cd  to the "backend" folder
py -m celery -A app:celery beat --loglevel=info

App at - http://127.0.0.1:5000

Username:  admin / admin@ppa.com        Password: admin123


