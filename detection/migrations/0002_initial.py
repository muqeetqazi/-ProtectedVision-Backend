# Generated by Django 5.1.7 on 2025-04-27 12:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('detection', '0001_initial'),
        ('documents', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='detectionjob',
            name='document',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detection_jobs', to='documents.document'),
        ),
        migrations.AddField(
            model_name='detectionjob',
            name='models_used',
            field=models.ManyToManyField(related_name='jobs', to='detection.detectionmodel'),
        ),
    ]
