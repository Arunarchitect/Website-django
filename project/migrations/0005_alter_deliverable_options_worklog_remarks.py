# Generated by Django 5.1.7 on 2025-05-20 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0004_alter_worklog_deliverable'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='deliverable',
            options={'ordering': ['project', 'stage', 'name'], 'verbose_name': 'Deliverable', 'verbose_name_plural': 'Deliverables'},
        ),
        migrations.AddField(
            model_name='worklog',
            name='remarks',
            field=models.TextField(blank=True, null=True, verbose_name='Remarks'),
        ),
    ]
