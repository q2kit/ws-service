cd /home/q2k/ws-service
source venv/bin/activate
gunicorn -c gunicorn.py
daphne src.asgi:application -p 8098 --proxy-headers > /dev/null 2>&1 &
