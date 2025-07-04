# Generated by Django 5.0.1 on 2024-12-27 19:03

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_alter_profilecomment_managers'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profilemedia',
            name='type',
        ),
        migrations.AddField(
            model_name='profilemedia',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2024, 12, 27, 19, 3, 17, 865122, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='subscriptions',
            field=models.ManyToManyField(blank=True, related_name='subscribers', to='users.userprofile'),
        ),
    ]
