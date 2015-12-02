#!/bin/sh

export OPAC_CONFIG="config.production"

python manager.py runserver
