from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify

from studios.models import Studio


@receiver(pre_save, sender=Studio)
def generate_studio_slug(sender, instance, **kwargs):
    if instance.slug:
        return
    base_slug = slugify(instance.name) or 'studio'
    slug = base_slug
    counter = 1
    while Studio.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
        slug = f'{base_slug}-{counter}'
        counter += 1
    instance.slug = slug
