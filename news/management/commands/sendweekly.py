from django.core.management.base import BaseCommand

from news.tasks import send_weekly_newsletter


class Command(BaseCommand):
    help = 'Немедленно отправляет еженедельную рассылку.'

    def handle(self, *args, **options):
        sent_count = send_weekly_newsletter()
        self.stdout.write(
            self.style.SUCCESS(
                f'Еженедельная рассылка выполнена. Писем отправлено: {sent_count}.'
            )
        )
