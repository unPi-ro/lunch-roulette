import time
from rq import get_current_job
from app import app, db
from app.models import Task, User
import json
from flask import render_template
from app.email import send_email

def lunch(user_id, sec): example(user_id, sec)

def example(user_id, seconds):
    try:
        user = User.query.get(user_id)
        _set_task_progress(0)
        i = 0
        for i in range(seconds):
            time.sleep(1)
            i += 1
            _set_task_progress(100 * i // seconds)
    except:
        _set_task_progress(100)
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())

def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        task.user.add_notification('task_progress', {'task_id': job.get_id(),
                                                     'progress': progress})
        if progress >= 100:
            task.complete = True
        db.session.commit()
