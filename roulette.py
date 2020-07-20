from app import app, db
from app.models import User, Company, Notification, Message, Timezone

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Company': Company, 'Message': Message, 'Notification': Notification, 'Timezone': Timezone}
