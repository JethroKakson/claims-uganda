# Generated by Django 5.1.3 on 2025-01-14 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Cases', '0009_case_field_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='customer_reference',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
