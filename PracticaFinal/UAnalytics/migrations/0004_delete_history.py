# Generated by Django 2.2.12 on 2021-06-12 16:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('UAnalytics', '0003_rename_dateandtiem_history_dateandtime'),
    ]

    operations = [
        migrations.DeleteModel(
            name='History',
        ),
    ]
