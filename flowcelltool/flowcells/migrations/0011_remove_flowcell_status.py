# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-03-22 08:14
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flowcells', '0010_auto_20180322_0757'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flowcell',
            name='status',
        ),
    ]
