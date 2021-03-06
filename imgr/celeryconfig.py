from datetime import timedelta
import os

static_dir = os.getenv('OPENSHIFT_DATA_DIR', os.path.dirname(__file__))
static_dir = os.path.join(static_dir, 'static')

CELERYBEAT_SCHEDULE = {
    'syncfs-task': {
        'task': 'imgr.tasks.syncfs',
        'schedule': timedelta(minutes=5),
        'args': [static_dir]
    },
}

CELERY_TIMEZONE = 'UTC'
