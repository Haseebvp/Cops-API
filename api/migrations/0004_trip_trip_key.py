# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-30 10:15
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20170930_0905'),
    ]

    operations = [
        migrations.AddField(
            model_name='trip',
            name='trip_key',
            field=models.UUIDField(default=uuid.uuid1, editable=False),
        ),
    ]
