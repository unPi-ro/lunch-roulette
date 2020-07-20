web: flask db upgrade; gunicorn roulette:app
worker: rq worker -u $REDIS_URL roulette-tasks
