# Generated by Django 5.1.3 on 2024-12-23 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Staff', '0004_staff_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='api_key',
            field=models.UUIDField(null=True),
        ),
    ]
