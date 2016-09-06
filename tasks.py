#!/usr/bin/env python

import sys
import os
import errno
import subprocess
from random import uniform

from celery import Celery
from celery.utils.log import get_task_logger

LOGGER = get_task_logger(__name__)
APP_NAME = 'tasks'

try:
    app = Celery(APP_NAME)
    app.config_from_object('celeryconfig', force=True)
except ImportError:
    redis_url = os.getenv('REDIS_URL', 'redis://')
    print 'celeryconfig not found, using %s' % redis_url
    app = Celery(APP_NAME, broker=redis_url, backend=redis_url)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST:
            pass


# http://docs.celeryproject.org/en/latest/userguide/tasks.html
@app.task(bind=True)
def run(self, args):
    out_fn, err_fn = args.pop(0), args.pop(0)
    for fn in out_fn, err_fn:
        mkdir_p(os.path.dirname(os.path.abspath(fn)))
    with open(out_fn, "w") as fo, open(err_fn, "w") as fe:
        ret = subprocess.call(args, stdout=fo, stderr=fe)
    LOGGER.info("stdout: %s" % out_fn)
    LOGGER.info("stderr: %s" % err_fn)
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
    return run.delay(args=argv[1:])


if __name__ == "__main__":
    r = main(sys.argv)
    print r
