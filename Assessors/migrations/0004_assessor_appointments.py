# Generated by Django 5.1.3 on 2024-12-10 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Appointments', '0001_initial'),
        ('Assessors', '0003_assessor_fee_notes_assessor_reports'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessor',
            name='appointments',
            field=models.ManyToManyField(blank=True, related_name='assessor_appointments', to='Appointments.appointment'),
        ),
    ]
