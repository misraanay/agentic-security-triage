from celery import Celery
app = Celery('app', broker="redis://redis:6379/0", include=['app.tasks'])