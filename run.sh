#!/bin/bash

export FLASK_ENV=development
export FLASK_APP=app
nohup flask run  --host=10.10.57.199 --port=5000 &
