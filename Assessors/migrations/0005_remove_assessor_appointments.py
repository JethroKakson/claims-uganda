# Generated by Django 5.1.3 on 2024-12-10 06:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Assessors', '0004_assessor_appointments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assessor',
            name='appointments',
        ),
    ]
