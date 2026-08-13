from django.core.management.base import BaseCommand

from news.tasks import send_weekly_newsletter


class Command(BaseCommand):
    help = 'Немедленно отправляет еженедельную рассылку.'

    def handle(self, *args, **options):
        result = send_weekly_newsletter.delay()
        self.stdout.write(
            self.style.SUCCESS(
                f'Еженедельная рассылка поставлена в очередь. Task ID: {result.id}'
            )
        )
