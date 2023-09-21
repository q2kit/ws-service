wsgi_app = "src.wsgi:application"
workers = 9
bind = "127.0.0.1:8097"
reload = True
accesslog = errorlog = None
loglevel = ""
capture_output = False
daemon = True