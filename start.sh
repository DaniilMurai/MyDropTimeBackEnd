#!/bin/sh
gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT app:app
