from django.shortcuts import render
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import StaffReimbursement, ExpenditurePurpose


@receiver(post_save, sender=ExpenditurePurpose)
def add_up_total(sender, **kwargs):
    created = kwargs['created']
    instance = kwargs['instance']
    instance.reimbursement.total += instance.total
    instance.reimbursement.expenditures.add(instance)


@receiver(pre_save, sender=ExpenditurePurpose)
def sum_up(sender, **kwargs):
    instance = kwargs['instance']
    instance.total = instance.daily_amount * instance.days