import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from news.tasks import send_weekly_newsletter


logger = logging.getLogger(__name__)


def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = 'Запускает планировщик еженедельной рассылки.'

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), 'default')

        scheduler.add_job(
            send_weekly_newsletter,
            trigger=CronTrigger(
                day_of_week='mon',
                hour='08',
                minute='00',
            ),
            id='weekly_newsletter',
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Добавлена задача 'weekly_newsletter'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week='mon',
                hour='00',
                minute='00',
            ),
            id='delete_old_job_executions',
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Добавлена задача 'delete_old_job_executions'.")

        try:
            logger.info('Запуск планировщика...')
            scheduler.start()
        except KeyboardInterrupt:
            logger.info('Остановка планировщика...')
            scheduler.shutdown()
            logger.info('Планировщик остановлен.')
