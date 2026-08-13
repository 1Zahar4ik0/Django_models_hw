from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from .models import Post


@shared_task
def send_new_post_notification(post_id):
    post = Post.objects.get(pk=post_id)
    site = Site.objects.get_current()
    post_url = f'http://{site.domain}{reverse("news_detail", args=[post.pk])}'
    subscribers = (
        User.objects
        .filter(subscribed_categories__posts=post)
        .exclude(email='')
        .distinct()
    )

    sent_count = 0

    for user in subscribers:
        html_content = render_to_string(
            'email/new_post_email.html',
            {
                'post': post,
                'user': user,
                'post_url': post_url,
            },
        )
        text_content = (
            f'Здравствуй, {user.username}. '
            f'Новая публикация в твоём любимом разделе!\n\n'
            f'{post.title}\n'
            f'{post.text[:50]}\n\n'
            f'Прочитать публикацию: {post_url}'
        )
        message = EmailMultiAlternatives(
            subject=post.title,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        message.attach_alternative(html_content, 'text/html')
        message.send()
        sent_count += 1

    return sent_count


@shared_task
def send_weekly_newsletter():
    week_ago = timezone.now() - timedelta(days=7)
    site = Site.objects.get_current()
    base_url = f'http://{site.domain}'
    subscribers = (
        User.objects
        .filter(subscribed_categories__isnull=False)
        .exclude(email='')
        .distinct()
    )

    sent_count = 0

    for user in subscribers:
        posts = (
            Post.objects
            .filter(
                categories__subscribers=user,
                created_at__gte=week_ago,
            )
            .distinct()
            .order_by('-created_at')
        )

        if not posts.exists():
            continue

        html_content = render_to_string(
            'email/weekly_posts.html',
            {
                'user': user,
                'posts': posts,
                'base_url': base_url,
            },
        )
        text_lines = [
            f'Здравствуй, {user.username}!',
            '',
            'Новые статьи за прошедшую неделю:',
            '',
        ]

        for post in posts:
            post_url = f'{base_url}{reverse("news_detail", args=[post.pk])}'
            text_lines.extend([
                post.title,
                post.text[:100],
                post_url,
                '',
            ])

        message = EmailMultiAlternatives(
            subject='Новые статьи News Portal за неделю',
            body='\n'.join(text_lines),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        message.attach_alternative(html_content, 'text/html')
        message.send()
        sent_count += 1

    return sent_count
