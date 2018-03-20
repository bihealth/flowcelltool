# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-03-20 06:22
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('threads', '0003_auto_20180320_0622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='uuid',
            field=models.UUIDField(unique=True),
        ),
        migrations.AlterField(
            model_name='attachmentfile',
            name='uuid',
            field=models.UUIDField(unique=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='uuid',
            field=models.UUIDField(unique=True),
        ),
    ]
