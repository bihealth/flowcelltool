# -*- coding: utf-8 -*-
"""Tests for permissions in the views

We only test the "GET" actions as the protection is on a per-CBV level
"""

import datetime
import io
import textwrap

from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse

from test_plus.test import TestCase

from .. import models
from .test_models import SequencingMachineMixin, FlowCellMixin, \
    BarcodeSetMixin, BarcodeSetEntryMixin, LibraryMixin
from .test_views import MessageMixin


GUEST = 'Guest'
INSTRUMENT_OPERATOR = 'Instrument Operator'
DEMUX_OPERATOR = 'Demultiplexing Operator'
DEMUX_ADMIN = 'Demultiplexing Admin'
IMPORT_BOT = 'Import Bot'


# Helpers ---------------------------------------------------------------------


class TestPermissionBase(TestCase):

    def make_user(self, group_name, *args, **kwargs):
        user = super().make_user(*args, **kwargs)
        if group_name:
            user.groups.add(Group.objects.filter(name=group_name).all()[0])
        return user

    def _make_users(self):
        """Create users with the different roles/groups"""
        self.anonymous = None
        self.nogroup = self.make_user(None, username='nogroup')
        self.guest = self.make_user(GUEST, username='guest')
        self.inst_op = self.make_user(INSTRUMENT_OPERATOR, username='inst_op')
        self.demux_op = self.make_user(DEMUX_OPERATOR, username='demux_op')
        self.demux_admin = self.make_user(DEMUX_ADMIN, username='demux_admin')
        self.import_bot = self.make_user(IMPORT_BOT, username='import_bot')
        self.superuser = self.make_user(None, username='superuser')
        self.superuser.is_staff = True
        self.superuser.is_superuser = True
        self.superuser.save()

    def setUp(self):
        self._make_users()

    def assert_render_200_ok(self, url, users):
        for user in users:
            if user:
                with self.login(user):
                    response = self.client.get(url)
                    self.assertEquals(response.status_code, 200,
                                      'user={}'.format(user))
            else:
                response = self.client.get(url)
                self.assertEquals(response.status_code, 200,
                                  'user={}'.format(user))

    def assert_redirect_to_login(self, url, users, redirection=None):
        if redirection is None:
            redirection = reverse('login') + '?next=' + url
        for user in users:
            if user:
                with self.login(user):
                    response = self.client.get(url)
                    self.assertRedirects(
                        response, redirection,
                        msg_prefix='user={}'.format(user))
            else:
                response = self.client.get(url)
                self.assertRedirects(
                    response, redirection,
                    msg_prefix='user={}'.format(user))


# Base Views ------------------------------------------------------------------


class TestBaseViews(TestPermissionBase):

    def test_home(self):
        URL = reverse('home')
        GOOD = (self.inst_op, self.nogroup, self.guest, self.demux_op,
                self.demux_admin, self.import_bot, self.superuser)
        BAD = (self.anonymous,)
        REDIR = reverse('login') + '?next=/'
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD, redirection=REDIR)

    def test_login(self):
        URL = reverse('login')
        GOOD = (self.anonymous, self.nogroup, self.guest, self.inst_op,
                self.demux_op, self.demux_admin, self.import_bot,
                self.superuser)
        self.assert_render_200_ok(URL, GOOD)

    def test_logout(self):
        URL = reverse('login')
        GOOD = (self.anonymous, self.nogroup, self.guest, self.inst_op,
                self.demux_op, self.demux_admin, self.import_bot,
                self.superuser)
        REDIRECTION = '/login/'
        self.assert_render_200_ok(URL, GOOD)

    def test_about(self):
        URL = reverse('about')
        GOOD = (self.anonymous, self.nogroup, self.guest, self.inst_op,
                self.demux_op, self.demux_admin, self.import_bot,
                self.superuser)
        self.assert_render_200_ok(URL, GOOD)

    def test_admin(self):
        URL = '/admin/'
        GOOD = (self.superuser,)
        BAD = (self.anonymous, self.nogroup, self.guest, self.inst_op,
               self.demux_op, self.demux_admin, self.import_bot)
        REDIRECTION = '/admin/login/?next=/admin/'
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD, redirection=REDIRECTION)


# SequencingMachine related ---------------------------------------------------


class TestSequencingMachineViews(TestPermissionBase, SequencingMachineMixin):

    def setUp(self):
        super().setUp()
        self.machine = self._make_machine()

    def test_list(self):
        URL = reverse('instrument_list')
        GOOD = (self.inst_op, self.guest, self.demux_op, self.demux_admin,
                self.import_bot, self.superuser)
        BAD = (self.anonymous, self.nogroup)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)

    def test_create(self):
        URL = reverse('instrument_create')
        GOOD = (self.demux_admin, self.superuser)
        BAD = (self.anonymous, self.nogroup, self.guest, self.inst_op,
               self.demux_op, self.import_bot)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)

    def test_view(self):
        URL = reverse('instrument_view', kwargs={'pk': self.machine.pk})
        GOOD = (self.inst_op, self.guest, self.demux_op, self.demux_admin,
                self.import_bot, self.superuser)
        BAD = (self.anonymous, self.nogroup)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)

    def test_update(self):
        URL = reverse('instrument_update', kwargs={'pk': self.machine.pk})
        GOOD = (self.demux_admin, self.superuser)
        BAD = (self.anonymous, self.nogroup, self.guest, self.inst_op,
               self.demux_op, self.import_bot)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)

    def test_delete(self):
        URL = reverse('instrument_delete', kwargs={'pk': self.machine.pk})
        GOOD = (self.demux_admin, self.superuser)
        BAD = (self.anonymous, self.inst_op, self.demux_op, self.import_bot)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)


# BarcodeSet related ----------------------------------------------------------


class TestBarcodeSetViews(TestPermissionBase, BarcodeSetMixin):

    def setUp(self):
        super().setUp()
        self.barcode_set = self._make_barcode_set()

    def test_list(self):
        URL = reverse('barcodeset_list')
        GOOD = (self.inst_op, self.guest, self.demux_op, self.demux_admin,
                self.import_bot, self.superuser)
        BAD = (self.anonymous, self.nogroup)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)

    def test_create(self):
        URL = reverse('barcodeset_create')
        GOOD = (self.demux_admin, self.superuser)
        BAD = (self.anonymous, self.nogroup, self.guest, self.inst_op,
               self.demux_op, self.import_bot)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)

    def test_view(self):
        URL = reverse('barcodeset_view', kwargs={'pk': self.barcode_set.pk})
        GOOD = (self.inst_op, self.guest, self.demux_op, self.demux_admin,
                self.import_bot, self.superuser)
        BAD = (self.anonymous, self.nogroup)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)

    def test_update(self):
        URL = reverse('barcodeset_update', kwargs={'pk': self.barcode_set.pk})
        GOOD = (self.demux_admin, self.superuser)
        BAD = (self.anonymous, self.nogroup, self.guest, self.inst_op,
               self.demux_op, self.import_bot)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)

    def test_updateentries(self):
        URL = reverse('barcodeset_updateentries',
                      kwargs={'pk': self.barcode_set.pk})
        GOOD = (self.demux_admin, self.superuser)
        BAD = (self.anonymous, self.nogroup, self.guest, self.inst_op,
               self.demux_op, self.import_bot)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)

    def test_export(self):
        URL = reverse('barcodeset_export', kwargs={'pk': self.barcode_set.pk})
        GOOD = (self.inst_op, self.guest, self.demux_op, self.demux_admin,
                self.import_bot, self.superuser)
        BAD = (self.anonymous, self.nogroup)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)

    def test_import(self):
        URL = reverse('barcodeset_import')
        GOOD = (self.demux_admin, self.superuser)
        BAD = (self.anonymous, self.nogroup, self.guest, self.inst_op,
               self.demux_op, self.import_bot)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)

    def test_delete(self):
        URL = reverse('barcodeset_delete', kwargs={'pk': self.barcode_set.pk})
        GOOD = (self.demux_admin, self.superuser)
        BAD = (self.anonymous, self.nogroup, self.guest, self.inst_op,
               self.demux_op, self.import_bot)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)


# FlowCell related ------------------------------------------------------------


class TestFlowCellViews(
        TestPermissionBase, FlowCellMixin, SequencingMachineMixin):

    def setUp(self):
        super().setUp()
        self.machine = self._make_machine()
        # Create one flow cell owned by instrument operator and one owned by
        # the import bot for testing with owner feature
        self.flow_cell_name1 = '160303_{}_0815_A_BCDEFGHIXX_LABEL'.format(
            self.machine.vendor_id)
        self.flow_cell_name2 = '160303_{}_0815_B_CCDEFGHIXX_LABEL'.format(
            self.machine.vendor_id)
        self.inst_op_flow_cell = self._make_flow_cell(
            self.inst_op, datetime.date(2016, 3, 3), self.machine, 815, 'A',
            'BCDEFGHIXX', 'LABEL', 8, models.FLOWCELL_STATUS_SEQ_COMPLETE,
            'John Doe', True, 1, models.RTA_VERSION_V2, 151, 'Description')
        self.import_bot_flow_cell = self._make_flow_cell(
            self.import_bot, datetime.date(2016, 3, 3), self.machine, 815, 'A',
            'BCDEFGHIXX', 'LABEL', 8, models.FLOWCELL_STATUS_SEQ_COMPLETE,
            'John Doe', True, 1, models.RTA_VERSION_V2, 151, 'Description')

    def test_list(self):
        URL = reverse('flowcell_list')
        GOOD = (self.inst_op, self.guest, self.demux_op, self.demux_admin,
                self.import_bot, self.superuser)
        BAD = (self.anonymous, self.nogroup)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)

    def test_create(self):
        URL = reverse('flowcell_create')
        GOOD = (self.inst_op, self.demux_op, self.import_bot,
                self.demux_admin, self.superuser)
        BAD = (self.anonymous, self.nogroup, self.guest)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)

    def test_view(self):
        URL = reverse('flowcell_view',
                      kwargs={'pk': self.inst_op_flow_cell.pk})
        GOOD = (self.inst_op, self.guest, self.demux_op, self.demux_admin,
                self.import_bot, self.superuser)
        BAD = (self.anonymous, self.nogroup)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)

    def test_update_inst_op_owned(self):
        URL = reverse('flowcell_update',
                      kwargs={'pk': self.inst_op_flow_cell.pk})
        GOOD = (self.inst_op, self.demux_admin, self.superuser)
        BAD = (self.anonymous, self.nogroup, self.guest, self.import_bot)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)

    def test_update_import_bot_owned(self):
        URL = reverse('flowcell_update',
                      kwargs={'pk': self.import_bot_flow_cell.pk})
        GOOD = (self.import_bot, self.demux_op, self.demux_admin,
                self.superuser)
        BAD = (self.anonymous, self.nogroup, self.guest, self.inst_op)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)

    def test_updateentries_inst_op_owned(self):
        URL = reverse('flowcell_updatelibraries',
                      kwargs={'pk': self.inst_op_flow_cell.pk})
        GOOD = (self.inst_op, self.demux_admin, self.superuser)
        BAD = (self.anonymous, self.nogroup, self.guest, self.import_bot)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)

    def test_updateentries_import_bot_owned(self):
        URL = reverse('flowcell_updatelibraries',
                      kwargs={'pk': self.import_bot_flow_cell.pk})
        GOOD = (self.import_bot, self.demux_op, self.demux_admin,
                self.superuser)
        BAD = (self.anonymous, self.nogroup, self.guest, self.inst_op)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)

    def test_export(self):
        URL = reverse('flowcell_export',
                      kwargs={'pk': self.inst_op_flow_cell.pk})
        GOOD = (self.inst_op, self.guest, self.demux_op, self.demux_admin,
                self.import_bot, self.superuser)
        BAD = (self.anonymous, self.nogroup)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)

    def test_import(self):
        URL = reverse('flowcell_import')
        GOOD = (self.inst_op, self.demux_op, self.import_bot, self.demux_admin,
                self.superuser)
        BAD = (self.anonymous, self.nogroup, self.guest)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)

    def test_delete_inst_op_owned(self):
        URL = reverse('flowcell_delete',
                      kwargs={'pk': self.inst_op_flow_cell.pk})
        GOOD = (self.inst_op, self.demux_admin, self.superuser)
        BAD = (self.anonymous, self.nogroup, self.guest, self.import_bot)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)

    def test_delete_import_op_owned(self):
        URL = reverse('flowcell_delete',
                      kwargs={'pk': self.import_bot_flow_cell.pk})
        GOOD = (self.import_bot, self.demux_op, self.demux_admin,
                self.superuser)
        BAD = (self.anonymous, self.nogroup, self.guest, self.inst_op)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)


# Message related -------------------------------------------------------------


class TestFlowCellMessageViews(
        TestPermissionBase, FlowCellMixin, SequencingMachineMixin,
        MessageMixin):

    def setUp(self):
        super().setUp()
        self.machine = self._make_machine()
        self.flow_cell = self._make_flow_cell(
            self.inst_op, datetime.date(2016, 3, 3), self.machine, 815, 'A',
            'BCDEFGHIXX', 'LABEL', 8, models.FLOWCELL_STATUS_SEQ_COMPLETE,
            'John Doe', True, 1, models.RTA_VERSION_V2, 151, 'Description')
        # One message by import bot, instrument operator, and demux operator
        self.msg_import_bot = self._make_message(
            self.import_bot, self.flow_cell, 'Title', 'Body')
        self.msg_inst_op = self._make_message(
            self.inst_op, self.flow_cell, 'Title', 'Body')
        self.msg_demux_op = self._make_message(
            self.demux_op, self.flow_cell, 'Title', 'Body')

    def test_add_message(self):
        URL = reverse('flowcell_add_message',
                      kwargs={'related_pk': self.flow_cell.pk})
        GOOD = (self.inst_op, self.demux_op, self.demux_admin,
                self.import_bot, self.superuser)
        BAD = (self.anonymous, self.nogroup, self.guest)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)

    def test_change_message_import_bot_owned(self):
        URL = reverse('flowcell_update_message',
                      kwargs={'pk': self.msg_import_bot.pk})
        GOOD = (self.import_bot, self.demux_admin, self.superuser)
        BAD = (self.anonymous, self.nogroup, self.guest, self.demux_op,
               self.demux_op)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)

    def test_change_message_inst_op_owned(self):
        URL = reverse('flowcell_update_message',
                      kwargs={'pk': self.msg_inst_op.pk})
        GOOD = (self.inst_op, self.demux_admin, self.superuser)
        BAD = (self.anonymous, self.nogroup, self.guest, self.import_bot,
               self.demux_op)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)

    def test_change_message_demux_owned(self):
        URL = reverse('flowcell_update_message',
                      kwargs={'pk': self.msg_demux_op.pk})
        GOOD = (self.demux_op, self.demux_admin, self.superuser)
        BAD = (self.anonymous, self.nogroup, self.guest, self.import_bot,
               self.inst_op)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)

    def test_delete_message_import_bot_owned(self):
        URL = reverse('flowcell_delete_message',
                      kwargs={'pk': self.msg_import_bot.pk})
        GOOD = (self.import_bot, self.demux_admin, self.superuser)
        BAD = (self.anonymous, self.nogroup, self.guest, self.demux_op,
               self.demux_op)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)

    def test_delete_message_inst_op_owned(self):
        URL = reverse('flowcell_delete_message',
                      kwargs={'pk': self.msg_inst_op.pk})
        GOOD = (self.inst_op, self.demux_admin, self.superuser)
        BAD = (self.anonymous, self.nogroup, self.guest, self.import_bot,
               self.demux_op)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)

    def test_delete_message_demux_owned(self):
        URL = reverse('flowcell_delete_message',
                      kwargs={'pk': self.msg_demux_op.pk})
        GOOD = (self.demux_op, self.demux_admin, self.superuser)
        BAD = (self.anonymous, self.nogroup, self.guest, self.import_bot,
               self.inst_op)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)


# Search ----------------------------------------------------------------------


class TestSearchView(TestPermissionBase):

    def test_search(self):
        URL = reverse('search')
        GOOD = (self.inst_op, self.demux_op, self.demux_admin,
                self.import_bot, self.superuser)
        BAD = (self.anonymous,)
        self.assert_render_200_ok(URL, GOOD)
        self.assert_redirect_to_login(URL, BAD)
