# Generated by Django 5.1.3 on 2024-12-13 09:59

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SupportDocuments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='supportdocument',
            name='date_uploaded',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
