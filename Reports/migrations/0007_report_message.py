# Generated by Django 5.1.3 on 2025-01-12 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Reports', '0006_alter_report_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='message',
            field=models.TextField(null=True),
        ),
    ]
