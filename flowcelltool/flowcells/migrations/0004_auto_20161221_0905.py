# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-21 09:05
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('flowcells', '0003_auto_20161024_0648'),
    ]

    operations = [
        migrations.AddField(
            model_name='flowcell',
            name='demux_operator',
            field=models.ForeignKey(blank=True, help_text='User responsible for demultiplexing', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='demuxed_flowcells', to=settings.AUTH_USER_MODEL, verbose_name='Demultiplexing Operator'),
        ),
        migrations.AlterField(
            model_name='flowcell',
            name='operator',
            field=models.CharField(max_length=100, verbose_name='Sequencer Operator'),
        ),
        migrations.AlterField(
            model_name='flowcell',
            name='status',
            field=models.CharField(choices=[('initial', 'initial'), ('seq_complete', 'sequecing complete'), ('seq_failed', 'sequencing failed'), ('demux_complete', 'demultiplexing complete'), ('demux_started', 'demultiplexing started'), ('demux_delivered', 'demultiplexing results delivered'), ('bcl_delivered', 'base calls delivered')], default='initial', help_text='Processing status of flow cell', max_length=50),
        ),
        migrations.AlterField(
            model_name='sequencingmachine',
            name='machine_model',
            field=models.CharField(choices=[('MiSeq', 'MiSeq'), ('MiniSeq', 'MiniSeq'), ('NextSeq500', 'NextSeq 500'), ('HiSeq1000', 'HiSeq 1000'), ('HiSeq1500', 'HiSeq 1500'), ('HiSeq2000', 'HiSeq 2000'), ('HiSeq3000', 'HiSeq 3000'), ('HiSeq4000', 'HiSeq 4000'), ('other', 'Other')], help_text='The model of the machine', max_length=100),
        ),
    ]
