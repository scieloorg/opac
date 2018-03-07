# coding: utf-8
# from datetime import datetime

from redis import Redis
from rq import Queue
from flask import current_app
from rq_scheduler import Scheduler
from webapp.utils.utils import send_audit_log_daily_report
# from webapp import rq


def setup_schedule():
    redis_conn = Redis(**current_app.config['RQ_REDIS_SETTINGS'])
    MAILING_QUEUE_NAME = 'mailing'
    queue = Queue(MAILING_QUEUE_NAME, connection=redis_conn)
    scheduler = Scheduler(queue=queue, connection=redis_conn)
    cron_string = '*/1 * * * *'

    for job in scheduler.get_jobs():
        print('removendo job %s do scheduler' % job.id)
        job.cancel()

    scheduler.cron(
        cron_string,
        func=send_audit_log_daily_report,
        queue_name=MAILING_QUEUE_NAME,
        timeout=30)
