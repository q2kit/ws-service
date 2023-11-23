wsgi_app = "src.wsgi:application"
workers = 9
bind = "127.0.0.1:8097"
reload = False
accesslog = errorlog = None
loglevel = ""
capture_output = False
daemon = False
proc_name = "ws-service"
