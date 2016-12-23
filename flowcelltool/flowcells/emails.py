# -*- coding: utf-8 -*-
"""Module for sending out emails
"""

from django.core.mail import send_mass_mail
from django.db.models import Q
from django.conf import settings

from flowcelltool.users.models import User

from . import rules


# Templates -------------------------------------------------------------------

TEMPLATE_FLOWCELL_CREATED = r"""
Dear {recipient},

The user {user} just created a new flow cell with the following id:

    {full_name}

You can see the created flow cell at the following URL:

    {flowcell_url}

You are receiving this email because you have the Demultiplexing Administrator
or the Demultiplexing Operator role.
""".lstrip()

TEMPLATE_FLOWCELL_UPDATED = r"""
Dear {recipient},

The user {user} just updated the flow cell with the following id:

    {full_name}

You can see the created flow cell at the following URL:

    {flowcell_url}

You are receiving this email because you have the Demultiplexing Administrator
or the Demultiplexing Operator role, or you have been assigned as the
demultiplexing operator for this flow cell.
""".lstrip()

TEMPLATE_FLOWCELL_DELETED = r"""
Dear {recipient},

The user {user} just deleted the flow cell with the following id:

    {full_name}

You are receiving this email because you have the Demultiplexing Administrator
or the Demultiplexing Operator role, or you have were assigned as the
demultiplexing operator for this flow cell.
""".lstrip()


# Helper Functions ------------------------------------------------------------


def _or_queries(queries):
    """Helper function that concatenates lazy Django queries"""
    result = queries.pop()
    for item in queries:
        result |= item
    return result


# Signal Handlers -------------------------------------------------------------


def email_flowcell_created(user, flowcell, request=None):
    """Send email on flow cell creation"""
    if not settings.FLOWCELLS_SEND_EMAILS:
        return
    # Gather groups to send emails to
    TO_GROUPS = (rules.DEMUX_ADMIN, rules.DEMUX_OPERATOR)
    # Build queries and perform the actual sending of emails
    queries = [Q(groups__name=group_name) for group_name in TO_GROUPS]
    queries.append(Q(is_superuser=True))
    queries.append(Q(pk=user.pk))
    if flowcell.demux_operator:
        queries.append(Q(pk=flowcell.demux_operator.pk))
    if flowcell.owner:
        queries.append(Q(pk=flowcell.owner.pk))
    users = User.objects.filter(_or_queries(queries))
    users = users.exclude(email__isnull=True).exclude(email__exact='')
    # Prepare values to push into email
    absolute_url = flowcell.get_absolute_url()
    if request:
        absolute_url = request.build_absolute_uri(absolute_url)
    vals = {
        'EMAIL_SUBJECT_PREFIX': settings.EMAIL_SUBJECT_PREFIX,
        'full_name': flowcell.get_full_name(),
        'flowcell_url': absolute_url,
        'user': user,
    }
    # Create email data tuple generator
    TEMPLATE_SUBJECT = (
        '{EMAIL_SUBJECT_PREFIX}{user} created new flow cell {full_name}')
    emails = (
        (
            TEMPLATE_SUBJECT.format(**vals),
            TEMPLATE_FLOWCELL_CREATED.format(recipient=u, **vals),
            settings.EMAIL_SENDER,
            [u.email]
        ) for u in users)
    # Actually send the emails
    send_mass_mail(emails, fail_silently=not settings.DEBUG)


def email_flowcell_updated(user, flowcell, request=None):
    """Send email on flow cell update"""
    if not settings.FLOWCELLS_SEND_EMAILS:
        return
    # Gather groups to send emails to
    TO_GROUPS = (rules.DEMUX_ADMIN, rules.DEMUX_OPERATOR)
    # Build queries and perform the actual sending of emails
    queries = [Q(groups__name=group_name) for group_name in TO_GROUPS]
    queries.append(Q(is_superuser=True))
    queries.append(Q(pk=user.pk))
    if flowcell.owner:
        queries.append(Q(pk=flowcell.owner.pk))
    if flowcell.demux_operator:
        queries.append(Q(pk=flowcell.demux_operator.pk))
    users = User.objects.filter(_or_queries(queries))
    users = users.exclude(email__isnull=True).exclude(email__exact='')
    # Prepare values to push into email
    absolute_url = flowcell.get_absolute_url()
    if request:
        absolute_url = request.build_absolute_uri(absolute_url)
    vals = {
        'EMAIL_SUBJECT_PREFIX': settings.EMAIL_SUBJECT_PREFIX,
        'full_name': flowcell.get_full_name(),
        'flowcell_url': absolute_url,
        'user': user,
    }
    # Create email data tuple generator
    TEMPLATE_SUBJECT = (
        '{EMAIL_SUBJECT_PREFIX}{user} updated flow cell {full_name}')
    emails = (
        (
            TEMPLATE_SUBJECT.format(**vals),
            TEMPLATE_FLOWCELL_UPDATED.format(recipient=u, **vals),
            settings.EMAIL_SENDER,
            [u.email]
        ) for u in users)
    # Actually send the emails
    send_mass_mail(emails, fail_silently=not settings.DEBUG)


def email_flowcell_deleted(user, flowcell, request=None):
    """Send email on flow cell deletion"""
    if not settings.FLOWCELLS_SEND_EMAILS:
        return
    # Gather groups to send emails to
    TO_GROUPS = (rules.DEMUX_ADMIN, rules.DEMUX_OPERATOR)
    # Build queries and perform the actual sending of emails
    queries = [Q(groups__name=group_name) for group_name in TO_GROUPS]
    queries.append(Q(is_superuser=True))
    queries.append(Q(pk=user.pk))
    if flowcell.owner:
        queries.append(Q(pk=flowcell.owner.pk))
    if flowcell.demux_operator:
        queries.append(Q(pk=flowcell.demux_operator.pk))
    users = User.objects.filter(_or_queries(queries))
    users = users.exclude(email__isnull=True).exclude(email__exact='')
    # Prepare values to push into email
    vals = {
        'EMAIL_SUBJECT_PREFIX': settings.EMAIL_SUBJECT_PREFIX,
        'full_name': flowcell.get_full_name(),
        'user': user,
    }
    # Create email data tuple generator
    TEMPLATE_SUBJECT = (
        '{EMAIL_SUBJECT_PREFIX}{user} deleted flow cell {full_name}')
    emails = (
        (
            TEMPLATE_SUBJECT.format(**vals),
            TEMPLATE_FLOWCELL_DELETED.format(recipient=u, **vals),
            settings.EMAIL_SENDER,
            [u.email]
        ) for u in users)
    # Actually send the emails
    send_mass_mail(emails, fail_silently=not settings.DEBUG)
