#!/usr/bin/env python

from celery import Celery
from os import getenv
from random import uniform
from subprocess import PIPE, Popen
import sys

# Initial approximate delay in seconds
RETRY_DELAY = 1
APP_NAME = 'tasks'

try:
    app = Celery(APP_NAME)
    app.config_from_object('celeryconfig', force=True)
except ImportError:
    redis_url = getenv('REDIS_URL', 'redis://')
    print 'celeryconfig not found, using %s' % redis_url
    app = Celery(APP_NAME, broker=redis_url, backend=redis_url)


# http://docs.celeryproject.org/en/latest/userguide/tasks.html
@app.task(bind=True)
def run(self, args):
    p = Popen(args, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    r = {
        'id': self.request.id,
        'output': out,
        'error': err,
        'rc': p.returncode
    }
    if p.returncode:
        # Exponential backoff + jitter
        delay_base = app.conf.get('CUSTOM_RETRY_DELAY', 1)
        delay = int(uniform(2, 4) ** self.request.retries * delay_base)
        raise self.retry(countdown=delay, exc=Exception(r))
    return r


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print app.conf.humanize(with_defaults=False, censored=True)
        sys.stderr.write('ERROR: No command given\n')
        sys.exit(2)
    r = run.delay(args=sys.argv[1:])
    print r
