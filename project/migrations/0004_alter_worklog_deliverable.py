# Generated by Django 5.1.7 on 2025-05-12 17:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0003_deliverable_assignee_deliverable_validation_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worklog',
            name='deliverable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='worklogs', to='project.deliverable', verbose_name='Deliverable'),
        ),
    ]
