# Generated by Django 5.1.3 on 2025-01-07 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Staff', '0008_staff_last_seen'),
        ('Submissions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='submissions_received',
            field=models.ManyToManyField(blank=True, related_name='staff_submissions_received', to='Submissions.submission'),
        ),
    ]
