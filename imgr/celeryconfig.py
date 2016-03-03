from datetime import timedelta
import os

rootdir = os.getenv('OPENSHIFT_DATA_DIR', '/home/helder/git/imgr/')
rootdir += 'imgr'

CELERYBEAT_SCHEDULE = {
    'syncfs-task': {
        'task': 'imgr.tasks.syncfs',
        'schedule': timedelta(minutes=10),
        'args': [rootdir]
    },
}

CELERY_TIMEZONE = 'UTC'