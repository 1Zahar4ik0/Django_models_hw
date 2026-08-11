from allauth.account.signals import user_signed_up
from django.contrib.auth.models import Group
from django.dispatch import receiver


@receiver(user_signed_up)
def add_user_to_common_group(request, user, **kwargs):
    common_group = Group.objects.get(name='common')
    user.groups.add(common_group)
