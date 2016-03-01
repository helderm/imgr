from datetime import timedelta

CELERY_IMPORTS=('tasks',)
CELERYBEAT_SCHEDULE = {
    'list-files': {
        'task': 'tasks.list',
        'schedule': timedelta(seconds=10),
        'args': ['/home/helder/git/imgr/imgr']
    },
}

CELERY_TIMEZONE = 'UTC'