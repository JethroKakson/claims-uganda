# Generated by Django 5.1.3 on 2024-12-01 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Reports', '0001_initial'),
        ('Submissions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='submissions',
            field=models.ManyToManyField(related_name='report_submissions', to='Submissions.submission'),
        ),
    ]
