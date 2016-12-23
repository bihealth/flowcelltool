# -*- coding: utf-8 -*-
"""Tests for the email sending functions
"""

import datetime

from django.core import mail
from django.contrib.auth.models import Group

from .. import emails, models, rules
from .test_models import FlowCellMixin, SequencingMachineMixin

from test_plus.test import TestCase


class FlowCellEmailTest(
        TestCase, FlowCellMixin, SequencingMachineMixin):

    def setUp(self):
        self._create_users()
        self.machine = self._make_machine()
        self.flow_cell_name = '160303_{}_0815_A_BCDEFGHIXX_LABEL'.format(
            self.machine.vendor_id)
        self.flowcell = self._make_flow_cell(
            self.owner, datetime.date(2016, 3, 3), self.machine, 815, 'A',
            'BCDEFGHIXX', 'LABEL', 8, models.FLOWCELL_STATUS_SEQ_COMPLETE,
            'John Doe', True, 1, models.RTA_VERSION_V2, 151, 'Description',
            self.demux_operator)

    def make_user(self, username, email, groups=[], is_superuser=False):
        result = super().make_user(username=username, password='testpassword')
        result.email = email
        result.is_superuser = is_superuser
        result.save()
        for g in groups:
            Group.objects.get(name=g).user_set.add(result)
        return result

    def _create_users(self):
        self.owner = self.make_user('owner', 'owner@example.com')
        self.other = self.make_user('other', 'other@example.com')
        self.role_admin = self.make_user('admin', 'admin@example.com',
                                         [rules.DEMUX_ADMIN])
        self.role_operator = self.make_user(
            'operator', 'operator@example.com',
            [rules.DEMUX_OPERATOR])
        self.demux_operator = self.make_user(
            'demux_operator', 'demux-operator@example.com')
        self.superuser = self.make_user(
            'superuser', 'superuser@example.com', is_superuser=True)

    def test_email_on_created(self):
        emails.email_flowcell_created(self.owner, self.flowcell)
        EXPECTED = {
            'owner@example.com', 'admin@example.com',
            'operator@example.com', 'demux-operator@example.com',
            'superuser@example.com'
        }
        ACTUAL = set(', '.join(m.to) for m in mail.outbox)
        self.assertEqual(EXPECTED, ACTUAL)
        self.assertEqual(5, len(mail.outbox))

    def test_email_on_updated(self):
        emails.email_flowcell_updated(self.other, self.flowcell)
        EXPECTED = {
            'owner@example.com', 'admin@example.com',
            'operator@example.com', 'demux-operator@example.com',
            'other@example.com', 'superuser@example.com'
        }
        ACTUAL = set(', '.join(m.to) for m in mail.outbox)
        self.assertEqual(EXPECTED, ACTUAL)
        self.assertEqual(6, len(mail.outbox))

    def test_email_on_deleted(self):
        emails.email_flowcell_deleted(self.other, self.flowcell)
        EXPECTED = {
            'owner@example.com', 'admin@example.com',
            'operator@example.com', 'demux-operator@example.com',
            'other@example.com', 'superuser@example.com'
        }
        ACTUAL = set(', '.join(m.to) for m in mail.outbox)
        self.assertEqual(EXPECTED, ACTUAL)
        self.assertEqual(6, len(mail.outbox))
