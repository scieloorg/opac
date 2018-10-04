#!/bin/sh
export REDIS_URL=redis://$OPAC_RQ_REDIS_HOST:$OPAC_RQ_REDIS_PORT/0
export APP_PATH="/app/opac/"

cd /app/opac && python manager.py setup_scheduler_tasks

rqscheduler \
    --url=$REDIS_URL \
    --path=$APP_PATH \
    --interval=2 \
    --verbose
