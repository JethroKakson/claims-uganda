# Generated by Django 5.1.3 on 2024-12-13 10:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Cases', '0007_alter_case_pictures'),
        ('Pictures', '0002_picture_caption'),
    ]

    operations = [
        migrations.AddField(
            model_name='picture',
            name='case',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='case_pictures', to='Cases.case'),
        ),
    ]
