# Generated by Django 5.1.3 on 2025-01-10 18:29

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FeeNotes', '0006_alter_feenote_currency'),
    ]

    operations = [
        migrations.AddField(
            model_name='feenote',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='feenote',
            name='fee_note_number',
            field=models.PositiveIntegerField(null=True, unique=True),
        ),
    ]
