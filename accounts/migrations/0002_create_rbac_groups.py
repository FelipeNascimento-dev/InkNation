from django.db import migrations

RBAC_GROUPS = [
    'SYSTEM_ADMIN',
    'STUDIO_OWNER',
    'STUDIO_STAFF',
    'CLIENT',
]


def create_rbac_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    for name in RBAC_GROUPS:
        Group.objects.get_or_create(name=name)


def remove_rbac_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=RBAC_GROUPS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_rbac_groups, remove_rbac_groups),
    ]
