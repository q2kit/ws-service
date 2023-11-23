#!/bin/bash
# Start Gunicorn processes
# gunicorn -c gunicorn.py
gunicorn --reload -w 5 src.wsgi:application -b 0.0.0.0:8000 --daemon
# Start Daphne processes
daphne src.asgi:application -p 8001 --proxy-headers > /dev/null 2>&1
