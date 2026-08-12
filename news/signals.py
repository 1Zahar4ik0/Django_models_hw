from allauth.account.signals import user_signed_up
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse

from .models import ARTICLE, Post


@receiver(user_signed_up)
def add_user_to_common_group(request, user, **kwargs):
    common_group = Group.objects.get(name='common')
    user.groups.add(common_group)


@receiver(m2m_changed, sender=Post.categories.through)
def notify_subscribers_about_new_post(sender, instance, action, **kwargs):
    if action != 'post_add' or instance.post_type != ARTICLE:
        return

    site = Site.objects.get_current()
    post_url = f'http://{site.domain}{reverse("news_detail", args=[instance.pk])}'

    subscribers = (
        User.objects
        .filter(subscribed_categories__posts=instance)
        .exclude(email='')
        .distinct()
    )

    for user in subscribers:
        html_content = render_to_string(
            'email/new_post_email.html',
            {
                'post': instance,
                'user': user,
                'post_url': post_url,
            },
        )
        text_content = (
            f'Здравствуй, {user.username}. '
            f'Новая статья в твоём любимом разделе!\n\n'
            f'{instance.title}\n'
            f'{instance.text[:50]}\n\n'
            f'Прочитать статью: {post_url}'
        )
        message = EmailMultiAlternatives(
            subject=instance.title,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        message.attach_alternative(html_content, 'text/html')
        message.send()
