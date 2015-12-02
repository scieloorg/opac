#!/bin/sh

export OPAC_CONFIG="config.development"

python manager.py runserver
