# Generated by Django 5.1.3 on 2025-01-12 19:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Reports', '0007_report_message'),
        ('Staff', '0009_staff_submissions_received'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='last_author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Staff.staff'),
        ),
    ]
