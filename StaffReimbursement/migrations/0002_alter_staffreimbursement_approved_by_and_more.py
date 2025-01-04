# Generated by Django 5.1.3 on 2025-01-04 10:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Staff', '0007_staff_notifications'),
        ('StaffReimbursement', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffreimbursement',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Staff.staff'),
        ),
        migrations.AlterField(
            model_name='staffreimbursement',
            name='date_approved',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='staffreimbursement',
            name='total',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
