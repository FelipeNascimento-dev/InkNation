from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import CustomUser
from core.constants import CLIENT, STUDIO_OWNER, STUDIO_STAFF, SYSTEM_ADMIN

ROLE_TO_GROUP = {
    SYSTEM_ADMIN: 'SYSTEM_ADMIN',
    STUDIO_OWNER: 'STUDIO_OWNER',
    STUDIO_STAFF: 'STUDIO_STAFF',
    CLIENT: 'CLIENT',
}


@receiver(post_save, sender=CustomUser)
def sync_user_role_group(sender, instance, created, **kwargs):
    if instance.is_superuser:
        group_name = 'SYSTEM_ADMIN'
    else:
        group_name = ROLE_TO_GROUP.get(instance.role)
        if not group_name:
            return

    try:
        target_group = Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        return

    role_groups = Group.objects.filter(name__in=ROLE_TO_GROUP.values())
    instance.groups.remove(*role_groups.exclude(pk=target_group.pk))
    instance.groups.add(target_group)
