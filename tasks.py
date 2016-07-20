#!/usr/bin/env python

from celery import Celery
from docker import Client

REDIS_URL = 'redis://172.17.0.8:6379/0'
APP_NAME = 'tasks'

app = Celery(APP_NAME, broker=REDIS_URL, backend=REDIS_URL)


@app.task
def add(x, y):
    return x + y

# http://docs.celeryproject.org/en/latest/userguide/tasks.html
@app.task(bind=True)
#def docker(self, image, volumes, args):
def docker(self, args=None):
    cli = Client(version='auto')
    print self.request.id
    if not args:
        args = ['sh','-c','date; sleep 5; date']
    c = cli.create_container(image='centos', command=args,detach=False)
    cli.start(c)
    cli.wait(c)
    print cli.logs(c)
