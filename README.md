Celery example
==============

Start redis

    docker run -d --name redis redis
    docker inspect -f '{{ .NetworkSettings.IPAddress }}' redis

Edit tasks.py to set the redis URL and start the worker

    celery -A tasks worker --loglevel=info

Submit some tasks

    ipython
    import tasks
    tasks.add.delay(1, 3)
    tasks.docker.delay()
