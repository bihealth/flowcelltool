# -*- coding: utf-8 -*-
"""Custom template tags for the flowcells app"""
import textwrap

from django.shortcuts import reverse
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
        'initial': 'fa fc-fw fa-asterisk text-muted fc-super-muted',
        'ready': 'fa fc-fw fa-hourglass-1 text-info',
        'in_progress': 'fc-fw fa fa-hourglass-half',
        'complete': 'fa fc-fw fa-hourglass-end text-success',
        'failed': 'fa fc-fw fa-hourglass-end text-danger',
        'closed': 'fa fc-fw fa-check text-success',
        'closed_warnings': 'fa fc-fw fa-warning text-warning',
        'canceled': 'fa fc-fw fa-close text-danger',
        'skipped': 'fa fc-fw fa-minus text-muted',
    }.get(status)


@register.filter
def status_to_title(status):
    return {
        'initial': 'not started',
        'ready': 'ready to start',
        'in_progress': 'in progress',
        'complete': 'complete (but unconfirmed)',
        'failed': 'failed / canceled',
        'closed': 'released confirmed',
        'closed_warnings': 'complete with warnings',
        'canceled': 'canceled confirmed',
        'skipped': 'skipped or N/A',
    }.get(status)


@register.simple_tag
def get_status_form(flowcell, attribute, csrf_tag):
    tpl = textwrap.dedent(r"""
        <form action="{action}" method="post">
          <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_tag}" />
          <input type="hidden" name="attribute" value="{attribute}" />
            <button type="submit" name="status" value="initial" class="list-group-item list-group-item-action list-group-item-light p-2">
                <i class="fa fa-fw fa-asterisk"></i>
                reset to &quot;initial&quot;
            </button>
            <button type="submit" name="status" value="ready" class="list-group-item list-group-item-action list-group-item-info p-2">
                <i class="fa fa-fw fa-hourglass-1"></i>
                mark &quot;ready&quot;
            </button>
            <button type="submit" name="status" value="canceled" class="list-group-item list-group-item-action list-group-item-danger p-2">
                <i class="fa fa-fw fa-close"></i>
                confirm failure
            </button>
            <button type="submit" name="status" value="closed" class="list-group-item list-group-item-action list-group-item-success p-2">
                <i class="fa fa-fw fa-check"></i>
                confirm success
            </button>
            <button type="submit" name="status" value="closed_warnings" class="list-group-item list-group-item-action list-group-item-warning p-2">
                <i class="fa fa-fw fa-warning"></i>
                mark &quot;complete with warnings&quot;
            </button>
            <button type="submit" name="status" value="skipped" class="list-group-item list-group-item-action list-group-item-secondary p-2">
                <i class="fa fa-fw fa-minus"></i>
                mark skipped
            </button>
          </div>
        </form>
    """)
    return tpl.format(
        flowcell=flowcell,
        action=reverse('flowcell_update_status', kwargs={'uuid': flowcell.uuid}),
        attribute=attribute,
        csrf_tag=csrf_tag)
