from datetime import timedelta
import os

rootdir = os.getenv('OPENSHIFT_DATA_DIR', '/home/helder/git/imgr/imgr')

CELERYBEAT_SCHEDULE = {
    'syncfs-task': {
        'task': 'imgr.tasks.syncfs',
        'schedule': timedelta(minutes=1),
        'args': [rootdir]
    },
}

CELERY_TIMEZONE = 'UTC'