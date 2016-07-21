#!/usr/bin/env python

from celery import Celery
from docker import Client
from subprocess import PIPE, Popen
import sys

REDIS_URL = 'redis://172.17.0.8:6379/0'
APP_NAME = 'tasks'

app = Celery(APP_NAME, broker=REDIS_URL, backend=REDIS_URL)

@app.task(bind=True)
def run(self, args):
    p = Popen(args, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    r = {'id': self.request.id, 'output': out, 'error': err}
    #print r
    return r

# http://docs.celeryproject.org/en/latest/userguide/tasks.html
@app.task(bind=True)
def docker(self, args, image='centos', volumes=None):
    cli = Client(version='auto')
    if not args:
        args = ['sh','-c','date; sleep 5; date']
    c = cli.create_container(image=image, command=args, volumes=volumes)
    cli.start(c)
    cli.wait(c)
    r = {'id': self.request.id, 'output': cli.logs(c)}
    #print r
    return r


if __name__ == "__main__":
    if len(sys.argv) < 2:
        docker.delay(None)
    else:
        run.delay(args=sys.argv[1:])
