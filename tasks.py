#!/usr/bin/env python

from celery import Celery
from os import getenv
from random import uniform
import subprocess
import sys


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
    out_fn, err_fn = args.pop(0), args.pop(0)
    with open(out_fn, "w") as fo, open(err_fn, "w") as fe:
        ret = subprocess.call(args, stdout=fo, stderr=fe)
    r = {'id': self.request.id, 'rc': ret}
    if ret:
        # Exponential backoff + jitter
        delay_base = app.conf.get('CUSTOM_RETRY_DELAY', 1)
        delay = int(uniform(2, 4) ** self.request.retries * delay_base)
        raise self.retry(countdown=delay, exc=Exception(r))
    return r


def main(argv):
    if len(argv) < 4:
        print app.conf.humanize(with_defaults=False, censored=True)
        sys.stderr.write('USAGE: python %s OUT ERR CMD\n' % argv[0])
        sys.exit(2)
    r = run.delay(args=argv[1:])
    print r


if __name__ == "__main__":
    main(sys.argv)
