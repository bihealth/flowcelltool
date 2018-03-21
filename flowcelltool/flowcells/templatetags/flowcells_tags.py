# -*- coding: utf-8 -*-
"""Custom template tags for the flowcells app"""
from django import template
from django.contrib.auth.models import Group

import pagerange

register = template.Library()


@register.filter
def sizify(value):
    """
    Simple kb/mb/gb size snippet for templates:

    {{ product.file.size|sizify }}
    """
    if value < 512000:
        value = value / 1024.0
        ext = 'kb'
    elif value < 4194304000:
        value = value / 1048576.0
        ext = 'mb'
    else:
        value = value / 1073741824.0
        ext = 'gb'
    return '%s %s' % (str(round(value, 2)), ext)


@register.filter
def fa_mime_type(value):
    mapping = {
        'application/pdf': 'file-pdf-o',
        ('application/vnd.openxmlformats-officedocument.'
         'spreadsheetml.sheet'): 'file-excel-o',
        'text/html': 'file-text-o',
    }
    return mapping.get(value, 'file-o')


@register.filter
def integer_range(value):
    return pagerange.PageRange(value).range


@register.filter
def multiply(value, arg):
    return value * arg


@register.filter
def startswith(text, starts):
    return (text or '').startswith(starts)


@register.filter
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return group in user.groups.all()


@register.filter(is_safe=True)
def flow_cell_mode(info_reads):
    """Return flow cell sequencing mode."""
    res = ''
    if info_reads:
        read_lens = [
            a['num_cycles'] for a in info_reads if not a['is_indexed_read']]
        if len(read_lens) == 1:
            res = '1x{}'.format(read_lens[0])
        elif len(set(read_lens)) == 1:
            res = '2x{}'.format(read_lens[0])
        else:
            res = ' + '.join(map(str, read_lens))
        index_lens = [
            a['num_cycles'] for a in info_reads if a['is_indexed_read']]
        if index_lens:
            res += '/'
            if len(set(index_lens)) == 1:
                res += '{}x{}'.format(len(index_lens), index_lens[0])
            else:
                res += '+'.join(map(str, index_lens))
    return res or '?x?'


@register.filter
def flowcell_mode_ok(flowcell):
    if (not flowcell.info_planned_reads or
            not flowcell.info_final_reads):
        return False
    return (flow_cell_mode(flowcell.info_planned_reads) ==
            flow_cell_mode(flowcell.info_final_reads))


@register.filter
def status_to_icon(status):
    return {
        'initial': 'fa fa-question text-muted',
        'seq_running': 'fa fa-hourglass text-success',
        'seq_complete': 'fa fa-hourglass-end text-success',
        'seq_failed': 'fa fa-close text-danger',
        'seq_release': 'fa fa-check text-success',
        'demux_started': 'fa fa-hourglass text-muted',
        'demux_failed': 'fa fa-close text-danger',
        'demux_complete': 'fa fa-hourglass-end text-success',
        'demux_delivered': 'fa fa-check text-success',
        'bcl_delivered': 'fa fa-check text-success',
    }.get(status)
