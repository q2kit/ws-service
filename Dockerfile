FROM python:3.11.6-slim-bookworm
WORKDIR /srv/wsservice
RUN apt update && apt autoremove -y && apt upgrade -y
RUN apt install -y gcc g++ nano dos2unix libpq-dev nginx
RUN pip install psycopg2-binary==2.9.9
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY ./nginx.conf /etc/nginx/nginx.conf
COPY . .
RUN chmod +x start.sh
RUN dos2unix start.sh
RUN python manage.py collectstatic --noinput
CMD service nginx start && bash start.sh
