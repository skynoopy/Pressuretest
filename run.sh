#!/bin/bash

export FLASK_ENV=development
export FLASK_APP=app
nohup flask run  --host=192.168.2.94 --port=8888 &

