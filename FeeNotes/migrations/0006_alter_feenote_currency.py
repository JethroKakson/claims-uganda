# Generated by Django 5.1.3 on 2025-01-02 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FeeNotes', '0005_feenote_currency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feenote',
            name='currency',
            field=models.CharField(choices=[('USD', 'USD'), ('UGX', 'UGX')], default='UGX', max_length=50),
        ),
    ]
