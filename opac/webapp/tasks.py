# coding: utf-8

from flask import current_app
from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler


def get_scheduler(queue_name):
    redis_conn = Redis(**current_app.config["RQ_REDIS_SETTINGS"])
    queue = Queue(queue_name, connection=redis_conn)
    return Scheduler(queue=queue, connection=redis_conn)


def setup_scheduler(task_function, queue_name, cron_string):
    timeout = current_app.config["DEFAULT_SCHEDULER_TIMEOUT"]
    scheduler = get_scheduler(queue_name)
    scheduler.cron(
        cron_string, func=task_function, queue_name=queue_name, timeout=timeout
    )


def clear_scheduler(queue_name):
    scheduler = get_scheduler(queue_name)
    for job in scheduler.get_jobs():
        if job.origin == queue_name:
            print("removendo job %s do scheduler" % job.id)
            scheduler.cancel(job)
