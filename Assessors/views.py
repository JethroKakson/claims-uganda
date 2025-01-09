from django.shortcuts import render
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User


@receiver(post_delete, sender=User)
def user_deleted(sender, instance, **kwargs):
    try:
        instance.assessor.delete()
    except Assessor.DoesNotExist:
        pass

