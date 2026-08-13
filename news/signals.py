from allauth.account.signals import user_signed_up
from django.contrib.auth.models import Group
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .models import Post
from .tasks import send_new_post_notification


@receiver(user_signed_up)
def add_user_to_common_group(request, user, **kwargs):
    common_group = Group.objects.get(name='common')
    user.groups.add(common_group)


@receiver(m2m_changed, sender=Post.categories.through)
def notify_subscribers_about_new_post(sender, instance, action, **kwargs):
    if action != 'post_add':
        return

    send_new_post_notification.delay(instance.pk)
