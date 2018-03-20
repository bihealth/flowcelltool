# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-03-20 06:22
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('flowcells', '0007_auto_20180320_0622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='barcodeset',
            name='uuid',
            field=models.UUIDField(unique=True),
        ),
        migrations.AlterField(
            model_name='barcodesetentry',
            name='uuid',
            field=models.UUIDField(unique=True),
        ),
        migrations.AlterField(
            model_name='flowcell',
            name='uuid',
            field=models.UUIDField(unique=True),
        ),
        migrations.AlterField(
            model_name='library',
            name='uuid',
            field=models.UUIDField(unique=True),
        ),
        migrations.AlterField(
            model_name='sequencingmachine',
            name='uuid',
            field=models.UUIDField(unique=True),
        ),
    ]
