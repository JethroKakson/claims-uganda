# Generated by Django 5.1.3 on 2025-01-02 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Staff', '0005_staff_api_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='date_of_birth',
            field=models.DateField(null=True),
        ),
    ]
