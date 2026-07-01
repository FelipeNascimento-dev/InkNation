from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from accounts.models import CustomUser, UsernameSequence

ROLE_TO_GROUP = {
    'owner': 'STUDIO_OWNER',
    'staff': 'STUDIO_STAFF',
    'client': 'CLIENT',
}


@receiver(pre_save, sender=CustomUser)
def assign_ink_username(sender, instance, **kwargs):
    if instance.username:
        return
    with transaction.atomic():
        seq, _ = UsernameSequence.objects.select_for_update().get_or_create(pk=1)
        seq.last_number += 1
        seq.save(update_fields=['last_number'])
        instance.username = f'INK{seq.last_number:04d}'


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
    role_groups = role_groups | Group.objects.filter(name='SYSTEM_ADMIN')
    instance.groups.remove(*role_groups.exclude(pk=target_group.pk))
    instance.groups.add(target_group)
