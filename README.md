Celery Example
==============


Start Redis (WARNING: this is insecure)

    docker run -d --name redis -p 6379:6379 redis

Start a worker with two processes from this directory

    celery -A tasks worker --loglevel=info -c 2

`tasks` refers to the `tasks.py` file in this directory, see the [Celery docs](http://docs.celeryproject.org/en/latest/getting-started/index.html) for more information on naming and packaging tasks.

Submit some task(s)

    ./tasks.py command arguments ...

The task(s) will be added to Redis, and will be consumed by the worker.

If Redis is not running on `localhost:6379` set `REDIS_URL` to point to the Redis server

    export REDIS_URL=redis://redis.example.org:6379

You can start workers on other nodes too as long as they can access the Redis server.
If you omit `-c` it will default to the number of CPUs.

You can use `./example.sh` to test the support for automatic retries
(note this will create an `celery-example-output` directory)

    for f in $(seq 10); do ./tasks.py ./example.sh 1; done

A GUI is available for monitoring tasks

    pip install flower
    celery flower -A tasks
