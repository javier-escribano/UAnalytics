# Generated by Django 3.2.2 on 2021-06-12 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UAnalytics', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='history',
            name='dateandtiem',
            field=models.CharField(default=0, max_length=40),
            preserve_default=False,
        ),
    ]
