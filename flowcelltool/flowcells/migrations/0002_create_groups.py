# -*- coding: utf-8 -*-
"""Setup required groups for flowcell app
"""
from __future__ import unicode_literals

from django.db import migrations
from django.core.management.sql import emit_post_migrate_signal


INSTRUMENT_OPERATOR = 'Instrument Operator'
DEMUX_OPERATOR = 'Demultiplexing Operator'
DEMUX_ADMIN = 'Demultiplexing Admin'
IMPORT_BOT = 'Import Bot'


def make_groups(apps, schema_editor):
    """Create initial groups"""
    Group = apps.get_model('auth', 'Group')
    # Instrument operator
    inst_op, _ = Group.objects.get_or_create(name=INSTRUMENT_OPERATOR)
    # Demultiplexing operator
    demux_op, _ = Group.objects.get_or_create(name=DEMUX_OPERATOR)
    # Demultiplexing admin
    demux_admin, _ = Group.objects.get_or_create(name=DEMUX_ADMIN)
    # Flow cell import bot
    import_bot, _ = Group.objects.get_or_create(name=IMPORT_BOT)


def delete_groups(apps, schema_editor):
    """Remove initial groups again"""
    Group = apps.get_model('auth', 'Group')
    for name in (INSTRUMENT_OPERATOR, DEMUX_OPERATOR, IMPORT_BOT):
        Group.objects.filter(name=name).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('flowcells', '0001_initial'),
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(make_groups, delete_groups),
    ]
