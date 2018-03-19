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
