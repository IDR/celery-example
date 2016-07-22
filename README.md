Celery Example
==============


Start Redis on localhost, e.g. using Docker (WARNING: this is insecure)

    docker run -d --name redis -p 6379:6379 redis

Start a worker with two processes from this directory

    celery -A tasks worker --loglevel=info -c 2

`tasks` refers to the `tasks.py` file in this directory, see the [Celery docs](http://docs.celeryproject.org/en/latest/getting-started/index.html) for more information on naming and packaging tasks.

Submit some task(s)

    ./tasks.py command arguments ...

The task(s) will be added to Redis, and will be consumed by the worker.


Configuration
-------------

If Redis is not running on `localhost:6379` create a configuration file `celeryconfig.py` in the same directory as `tasks.py` with

    BROKER_URL = 'redis://redis.example.org:6379'
    CELERY_RESULT_BACKEND = 'redis://redis.example.org:6379'

This configuration file will be automatically loaded by `tasks.py`, see `celeryconfig.py.example` for more examples.

If you do not have a configuration file you can set the environment variable `REDIS_URL`

    export REDIS_URL=redis://redis.example.org:6379

You can start workers on other nodes too as long as they can access the Redis server.
If you omit `-c` it will default to the number of CPUs.

You can use `./example.sh` to test the support for automatic retries
(note this will create an `celery-example-output` directory)

    for f in $(seq 100); do ./tasks.py ./example.sh 1; done

A GUI is available for monitoring tasks

    pip install flower
    celery flower -A tasks


Redis security
--------------

You can set a [password and other configuration options](http://docs.celeryproject.org/en/latest/getting-started/brokers/redis.html) when starting Redis, or in the Redis configuration file.
Note that all communication is in plain text so does not guard against network sniffing.

    docker run -d --name redis -p 6379:6379 redis --requirepass PASSWORD

    BROKER_URL = 'redis://:PASSWORD@redis.example.org:6379'
