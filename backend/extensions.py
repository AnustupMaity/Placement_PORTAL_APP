from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from celery import Celery

# sqlalcmy orm 
db = SQLAlchemy()

# fskmail
mail = Mail()

# redis cache
redis_client = None

# socketio
from flask_socketio import SocketIO
socketio = SocketIO(cors_allowed_origins="*")


def init_redis(app):
    
    global redis_client
    import redis
    redis_client = redis.from_url(
        app.config.get('REDIS_URL', 'redis://localhost:6379/0'),
        decode_responses=True
    )
    try:
        redis_client.ping()
        app.logger.info('Redis successfully.')
    except Exception as e:
        app.logger.warning(
            f' could not  reached: {e}. '

        )
        redis_client = None

def make_celery(app): # celery app make 
    import ssl

    broker_url = app.config.get('CELERY_BROKER_URL') or app.config.get('REDIS_URL')
    result_backend = app.config.get('CELERY_RESULT_BACKEND') or app.config.get('REDIS_URL')

    celery = Celery(
        app.import_name,
        broker=broker_url,
        backend=result_backend,
        include=['tasks.reminders', 'tasks.reports', 'tasks.emails']
    )

    conf_dict = {
        'broker_url': broker_url,
        'result_backend': result_backend,
    }

    if broker_url and broker_url.startswith('rediss://'):
        conf_dict['broker_use_ssl'] = {'ssl_cert_reqs': ssl.CERT_NONE}
        conf_dict['redis_backend_use_ssl'] = {'ssl_cert_reqs': ssl.CERT_NONE}

    celery.conf.update(conf_dict)


    from celery.schedules import crontab
    celery.conf.beat_schedule = {
        'daily-reminders-at-8am': {
            'task': 'tasks.reminders.send_daily_reminders',
            'schedule': crontab(hour=8, minute=0)
        },
        'monthly-report-on-1st': {
            'task': 'tasks.reports.generate_monthly_report',
            'schedule': crontab(day_of_month='1', hour=0, minute=0)
        }
    }

#this edit was made using suggest from llm line 43 to 50
    
    class ContextTask(celery.Task):
        """ task runs inside"""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
