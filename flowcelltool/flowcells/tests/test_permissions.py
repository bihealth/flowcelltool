# -*- coding: utf-8 -*-
"""Tests for permissions in the views

We only test the "GET" actions as the protection is on a per-CBV level
"""

import io
import textwrap

from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse

from test_plus.test import TestCase

from .. import models
from .test_models import SequencingMachineMixin, FlowCellMixin, \
    BarcodeSetMixin, BarcodeSetEntryMixin, LibraryMixin
from .test_views import MessageMixin


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

    def assert_redirect_to(self, url, redir_url, users):
        for user in users:
            if user:
                with self.login(user):
                    response = self.client.get(url)
                    self.assertRedirects(
                        response, redir_url,
                        msg_prefix='user={}'.format(user))
            else:
                response = self.client.get(url)
                self.assertRedirects(
                    response, redir_url,
                    msg_prefix='user={}'.format(user))


# Base Views ------------------------------------------------------------------


class TestBaseViews(TestPermissionBase):

    def test_home(self):
        self.assert_render_200_ok(
            reverse('home'),
            (self.inst_op, self.demux_op, self.demux_admin,
             self.import_bot, self.superuser))
        self.assert_redirect_to(
            reverse('home'),
            reverse('login') + '?next=/',
            (self.anonymous,))

    def test_login(self):
        self.assert_render_200_ok(
            reverse('login'),
            (self.anonymous, self.inst_op, self.demux_op, self.demux_admin,
             self.import_bot, self.superuser))

    def test_logout(self):
        self.assert_redirect_to(
            reverse('logout'),
            reverse('login'),
            (self.anonymous, self.inst_op, self.demux_op, self.demux_admin,
             self.import_bot, self.superuser))

    def test_about(self):
        self.assert_render_200_ok(
            reverse('about'),
            (self.anonymous, self.inst_op, self.demux_op, self.demux_admin,
             self.import_bot, self.superuser))

    def test_admin(self):
        self.assert_render_200_ok(
            '/admin/',
            (self.superuser,))
        self.assert_redirect_to(
            '/admin/',
            '/admin/login/?next=/admin/',
            (self.anonymous, self.inst_op, self.demux_op, self.demux_admin,
             self.import_bot))


# SequencingMachine related ---------------------------------------------------


class TestSequencingMachineViews(TestPermissionBase, SequencingMachineMixin):

    def setUp(self):
        super().setUp()
        self.machine = self._make_machine()

    def test_list(self):
        self.assert_render_200_ok(
            reverse('instrument_list'),
            (self.inst_op, self.demux_op, self.demux_admin,
             self.import_bot, self.superuser))
        self.assert_redirect_to(
            reverse('instrument_list'),
            reverse('login')  + '?next=' + reverse('instrument_list'),
            (self.anonymous,))

    def test_create(self):
        self.assert_render_200_ok(
            reverse('instrument_create'),
            (self.demux_admin, self.superuser))
        self.assert_redirect_to(
            reverse('instrument_create'),
            reverse('login')  + '?next=' + reverse('instrument_create'),
            (self.anonymous, self.inst_op, self.demux_op, self.import_bot))

    def test_view(self):
        self.assert_render_200_ok(
            reverse('instrument_view',
                    kwargs={'pk': self.machine.pk}),
            (self.inst_op, self.demux_op, self.demux_admin,
             self.import_bot, self.superuser))
        self.assert_redirect_to(
            reverse('instrument_view', kwargs={'pk': self.machine.pk}),
            reverse('login')  + '?next=' + reverse(
                'instrument_view', kwargs={'pk': self.machine.pk}),
            (self.anonymous,))

    def test_update(self):
        self.assert_render_200_ok(
            reverse('instrument_update',
                    kwargs={'pk': self.machine.pk}),
            (self.demux_admin, self.superuser))
        self.assert_redirect_to(
            reverse('instrument_update', kwargs={'pk': self.machine.pk}),
            reverse('login')  + '?next=' + reverse(
                'instrument_update', kwargs={'pk': self.machine.pk}),
            (self.anonymous, self.inst_op, self.demux_op, self.import_bot))

    def test_delete(self):
        self.assert_render_200_ok(
            reverse('instrument_delete',
                    kwargs={'pk': self.machine.pk}),
            (self.demux_admin, self.superuser))
        self.assert_redirect_to(
            reverse('instrument_delete', kwargs={'pk': self.machine.pk}),
            reverse('login')  + '?next=' + reverse(
                'instrument_delete', kwargs={'pk': self.machine.pk}),
            (self.anonymous, self.inst_op, self.demux_op, self.import_bot))


# BarcodeSet related ----------------------------------------------------------


class TestBarcodeSetViews(TestPermissionBase, BarcodeSetMixin):

    def setUp(self):
        super().setUp()
        self.barcode_set = self._make_barcode_set()

    def test_list(self):
        self.assert_render_200_ok(
            reverse('barcodeset_list'),
            (self.inst_op, self.demux_op, self.demux_admin,
             self.import_bot, self.superuser))
        self.assert_redirect_to(
            reverse('barcodeset_list'),
            reverse('login')  + '?next=' + reverse('barcodeset_list'),
            (self.anonymous,))

    def test_create(self):
        self.assert_render_200_ok(
            reverse('barcodeset_create'),
            (self.demux_admin, self.superuser))
        self.assert_redirect_to(
            reverse('barcodeset_create'),
            reverse('login')  + '?next=' + reverse('barcodeset_create'),
            (self.anonymous, self.inst_op, self.demux_op, self.import_bot))

    def test_view(self):
        self.assert_render_200_ok(
            reverse('barcodeset_view',
                    kwargs={'pk': self.barcode_set.pk}),
            (self.inst_op, self.demux_op, self.demux_admin,
             self.import_bot, self.superuser))
        self.assert_redirect_to(
            reverse('barcodeset_view', kwargs={'pk': self.barcode_set.pk}),
            reverse('login')  + '?next=' + reverse(
                'barcodeset_view', kwargs={'pk': self.barcode_set.pk}),
            (self.anonymous,))

    def test_update(self):
        self.assert_render_200_ok(
            reverse('barcodeset_update',
                    kwargs={'pk': self.barcode_set.pk}),
            (self.demux_admin, self.superuser))
        self.assert_redirect_to(
            reverse('barcodeset_update', kwargs={'pk': self.barcode_set.pk}),
            reverse('login')  + '?next=' + reverse(
                'barcodeset_update', kwargs={'pk': self.barcode_set.pk}),
            (self.anonymous, self.inst_op, self.demux_op, self.import_bot))

    def test_updateentries(self):
        self.assert_render_200_ok(
            reverse('barcodeset_updateentries',
                    kwargs={'pk': self.barcode_set.pk}),
            (self.demux_admin, self.superuser))
        self.assert_redirect_to(
            reverse('barcodeset_updateentries',
                    kwargs={'pk': self.barcode_set.pk}),
            reverse('login')  + '?next=' + reverse(
                'barcodeset_updateentries',
                kwargs={'pk': self.barcode_set.pk}),
            (self.anonymous, self.inst_op, self.demux_op, self.import_bot))

    def test_export(self):
        self.assert_render_200_ok(
            reverse('barcodeset_export',
                    kwargs={'pk': self.barcode_set.pk}),
            (self.inst_op, self.demux_op, self.demux_admin,
             self.import_bot, self.superuser))
        self.assert_redirect_to(
            reverse('barcodeset_export',
                    kwargs={'pk': self.barcode_set.pk}),
            reverse('login')  + '?next=' + reverse(
                'barcodeset_export',
                kwargs={'pk': self.barcode_set.pk}),
            (self.anonymous,))

    def test_import(self):
        self.assert_render_200_ok(
            reverse('barcodeset_import'),
            (self.demux_admin, self.superuser))
        self.assert_redirect_to(
            reverse('barcodeset_import'),
            reverse('login')  + '?next=' + reverse('barcodeset_import'),
            (self.anonymous, self.inst_op, self.demux_op, self.import_bot))

    def test_delete(self):
        self.assert_render_200_ok(
            reverse('barcodeset_delete',
                    kwargs={'pk': self.barcode_set.pk}),
            (self.demux_admin, self.superuser))
        self.assert_redirect_to(
            reverse('barcodeset_delete', kwargs={'pk': self.barcode_set.pk}),
            reverse('login')  + '?next=' + reverse(
                'barcodeset_delete', kwargs={'pk': self.barcode_set.pk}),
            (self.anonymous, self.inst_op, self.demux_op, self.import_bot))


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
            self.inst_op, self.flow_cell_name1, 8,
            models.FLOWCELL_STATUS_SEQ_COMPLETE, 'John Doe',
            True, 1, models.RTA_VERSION_V2, 151, 'Description')
        self.import_bot_flow_cell = self._make_flow_cell(
            self.import_bot, self.flow_cell_name2, 8,
            models.FLOWCELL_STATUS_SEQ_COMPLETE, 'John Doe',
            True, 1, models.RTA_VERSION_V2, 151, 'Description')

    def test_list(self):
        self.assert_render_200_ok(
            reverse('flowcell_list'),
            (self.inst_op, self.demux_op, self.demux_admin,
             self.import_bot, self.superuser))
        self.assert_redirect_to(
            reverse('flowcell_list'),
            reverse('login')  + '?next=' + reverse('flowcell_list'),
            (self.anonymous,))

    def test_create(self):
        self.assert_render_200_ok(
            reverse('flowcell_create'),
            (self.inst_op, self.demux_op, self.import_bot, self.demux_admin,
             self.superuser))
        self.assert_redirect_to(
            reverse('flowcell_create'),
            reverse('login')  + '?next=' + reverse('flowcell_create'),
            (self.anonymous,))

    def test_view(self):
        self.assert_render_200_ok(
            reverse('flowcell_view',
                    kwargs={'pk': self.inst_op_flow_cell.pk}),
            (self.inst_op, self.demux_op, self.demux_admin,
             self.import_bot, self.superuser))
        self.assert_redirect_to(
            reverse('flowcell_view', kwargs={'pk': self.inst_op_flow_cell.pk}),
            reverse('login')  + '?next=' + reverse(
                'flowcell_view', kwargs={'pk': self.inst_op_flow_cell.pk}),
            (self.anonymous,))

    def test_update(self):
        # Flow cell owned by instrument operator
        self.assert_render_200_ok(
            reverse('flowcell_update',
                    kwargs={'pk': self.inst_op_flow_cell.pk}),
            (self.inst_op, self.demux_admin, self.superuser))
        self.assert_redirect_to(
            reverse('flowcell_update',
                    kwargs={'pk': self.inst_op_flow_cell.pk}),
            reverse('login')  + '?next=' + reverse(
                'flowcell_update', kwargs={'pk': self.inst_op_flow_cell.pk}),
            (self.anonymous, self.import_bot))
        # Flow cell owned by import bot
        self.assert_render_200_ok(
            reverse('flowcell_update',
                    kwargs={'pk': self.import_bot_flow_cell.pk}),
            (self.import_bot, self.demux_op, self.demux_admin, self.superuser))
        self.assert_redirect_to(
            reverse('flowcell_update',
                    kwargs={'pk': self.import_bot_flow_cell.pk}),
            reverse('login')  + '?next=' + reverse(
                'flowcell_update',
                kwargs={'pk': self.import_bot_flow_cell.pk}),
            (self.anonymous, self.inst_op))

    def test_updateentries(self):
        # Flow cell owned by instrument operator
        self.assert_render_200_ok(
            reverse('flowcell_updatelibraries',
                    kwargs={'pk': self.inst_op_flow_cell.pk}),
            (self.inst_op, self.demux_admin, self.superuser))
        self.assert_redirect_to(
            reverse('flowcell_updatelibraries',
                    kwargs={'pk': self.inst_op_flow_cell.pk}),
            reverse('login')  + '?next=' + reverse(
                'flowcell_updatelibraries',
                kwargs={'pk': self.inst_op_flow_cell.pk}),
            (self.anonymous, self.import_bot))
        # Flow cell owned by import bot
        self.assert_render_200_ok(
            reverse('flowcell_updatelibraries',
                    kwargs={'pk': self.import_bot_flow_cell.pk}),
            (self.import_bot, self.demux_op, self.demux_admin, self.superuser))
        self.assert_redirect_to(
            reverse('flowcell_updatelibraries',
                    kwargs={'pk': self.import_bot_flow_cell.pk}),
            reverse('login')  + '?next=' + reverse(
                'flowcell_updatelibraries',
                kwargs={'pk': self.import_bot_flow_cell.pk}),
            (self.anonymous, self.inst_op))

    def test_export(self):
        self.assert_render_200_ok(
            reverse('flowcell_export',
                    kwargs={'pk': self.inst_op_flow_cell.pk}),
            (self.inst_op, self.demux_op, self.demux_admin,
             self.import_bot, self.superuser))
        self.assert_redirect_to(
            reverse('flowcell_export',
                    kwargs={'pk': self.inst_op_flow_cell.pk}),
            reverse('login')  + '?next=' + reverse(
                'flowcell_export', kwargs={'pk': self.inst_op_flow_cell.pk}),
            (self.anonymous,))

    def test_import(self):
        self.assert_render_200_ok(
            reverse('flowcell_import'),
            (self.inst_op, self.demux_op, self.import_bot, self.demux_admin,
             self.superuser))
        self.assert_redirect_to(
            reverse('flowcell_import'),
            reverse('login')  + '?next=' + reverse('flowcell_import'),
            (self.anonymous,))

    def test_delete(self):
        # Flow cell owned by instrument operator
        self.assert_render_200_ok(
            reverse('flowcell_delete',
                    kwargs={'pk': self.inst_op_flow_cell.pk}),
            (self.inst_op, self.demux_admin, self.superuser))
        self.assert_redirect_to(
            reverse('flowcell_delete',
                    kwargs={'pk': self.inst_op_flow_cell.pk}),
            reverse('login')  + '?next=' + reverse(
                'flowcell_delete',
                kwargs={'pk': self.inst_op_flow_cell.pk}),
            (self.anonymous, self.import_bot))
        # Flow cell owned by import bot
        self.assert_render_200_ok(
            reverse('flowcell_delete',
                    kwargs={'pk': self.import_bot_flow_cell.pk}),
            (self.import_bot, self.demux_op, self.demux_admin, self.superuser))
        self.assert_redirect_to(
            reverse('flowcell_delete',
                    kwargs={'pk': self.import_bot_flow_cell.pk}),
            reverse('login')  + '?next=' + reverse(
                'flowcell_delete',
                kwargs={'pk': self.import_bot_flow_cell.pk}),
            (self.anonymous, self.inst_op))


# Message related -------------------------------------------------------------


class TestFlowCellMessageViews(
        TestPermissionBase, FlowCellMixin, SequencingMachineMixin,
        MessageMixin):

    def setUp(self):
        super().setUp()
        self.machine = self._make_machine()
        self.flow_cell_name = '160303_{}_0815_A_BCDEFGHIXX_LABEL'.format(
            self.machine.vendor_id)
        self.flow_cell = self._make_flow_cell(
            self.inst_op, self.flow_cell_name, 8,
            models.FLOWCELL_STATUS_SEQ_COMPLETE, 'John Doe',
            True, 1, models.RTA_VERSION_V2, 151, 'Description')
        # One message by import bot, instrument operator, and demux operator
        self.msg_import_bot = self._make_message(
            self.import_bot, self.flow_cell, 'Title', 'Body')
        self.msg_inst_op = self._make_message(
            self.inst_op, self.flow_cell, 'Title', 'Body')
        self.msg_demux_op = self._make_message(
            self.demux_op, self.flow_cell, 'Title', 'Body')

    def test_add_message(self):
        self.assert_render_200_ok(
            reverse('flowcell_add_message',
                    kwargs={'related_pk': self.flow_cell.pk}),
            (self.inst_op, self.demux_op, self.demux_admin,
             self.import_bot, self.superuser))
        self.assert_redirect_to(
            reverse('flowcell_add_message',
                    kwargs={'related_pk': self.flow_cell.pk}),
            reverse('login')  + '?next=' + reverse(
                'flowcell_add_message',
                kwargs={'related_pk': self.flow_cell.pk}),
            (self.anonymous,))

    def test_change_message(self):
        # Message owned by import bot
        self.assert_render_200_ok(
            reverse('flowcell_update_message',
                    kwargs={'pk': self.msg_import_bot.pk}),
            (self.import_bot, self.demux_admin, self.superuser))
        self.assert_redirect_to(
            reverse('flowcell_update_message',
                    kwargs={'pk': self.msg_import_bot.pk}),
            reverse('login')  + '?next=' + reverse(
                'flowcell_update_message',
                kwargs={'pk': self.msg_import_bot.pk}),
            (self.anonymous, self.demux_op, self.demux_op))
        # Message owned by instrument operator
        self.assert_render_200_ok(
            reverse('flowcell_update_message',
                    kwargs={'pk': self.msg_inst_op.pk}),
            (self.inst_op, self.demux_admin, self.superuser))
        self.assert_redirect_to(
            reverse('flowcell_update_message',
                    kwargs={'pk': self.msg_inst_op.pk}),
            reverse('login')  + '?next=' + reverse(
                'flowcell_update_message',
                kwargs={'pk': self.msg_inst_op.pk}),
            (self.anonymous, self.import_bot, self.demux_op))
        # Message owned by demux operator
        self.assert_render_200_ok(
            reverse('flowcell_update_message',
                    kwargs={'pk': self.msg_demux_op.pk}),
            (self.demux_op, self.demux_admin, self.superuser))
        self.assert_redirect_to(
            reverse('flowcell_update_message',
                    kwargs={'pk': self.msg_demux_op.pk}),
            reverse('login')  + '?next=' + reverse(
                'flowcell_update_message',
                kwargs={'pk': self.msg_demux_op.pk}),
            (self.anonymous, self.import_bot, self.inst_op))

    def test_delete_message(self):
        # Message owned by import bot
        self.assert_render_200_ok(
            reverse('flowcell_delete_message',
                    kwargs={'pk': self.msg_import_bot.pk}),
            (self.import_bot, self.demux_admin, self.superuser))
        self.assert_redirect_to(
            reverse('flowcell_delete_message',
                    kwargs={'pk': self.msg_import_bot.pk}),
            reverse('login')  + '?next=' + reverse(
                'flowcell_delete_message',
                kwargs={'pk': self.msg_import_bot.pk}),
            (self.anonymous, self.demux_op, self.demux_op))
        # Message owned by instrument operator
        self.assert_render_200_ok(
            reverse('flowcell_delete_message',
                    kwargs={'pk': self.msg_inst_op.pk}),
            (self.inst_op, self.demux_admin, self.superuser))
        self.assert_redirect_to(
            reverse('flowcell_delete_message',
                    kwargs={'pk': self.msg_inst_op.pk}),
            reverse('login')  + '?next=' + reverse(
                'flowcell_delete_message',
                kwargs={'pk': self.msg_inst_op.pk}),
            (self.anonymous, self.import_bot, self.demux_op))
        # Message owned by demux operator
        self.assert_render_200_ok(
            reverse('flowcell_delete_message',
                    kwargs={'pk': self.msg_demux_op.pk}),
            (self.demux_op, self.demux_admin, self.superuser))
        self.assert_redirect_to(
            reverse('flowcell_delete_message',
                    kwargs={'pk': self.msg_demux_op.pk}),
            reverse('login')  + '?next=' + reverse(
                'flowcell_delete_message',
                kwargs={'pk': self.msg_demux_op.pk}),
            (self.anonymous, self.import_bot, self.inst_op))


# Search ----------------------------------------------------------------------


class TestSearchView(TestPermissionBase):

    def test_search(self):
        self.assert_render_200_ok(
            reverse('search'),
            (self.inst_op, self.demux_op, self.demux_admin,
             self.import_bot, self.superuser))
        self.assert_redirect_to(
            reverse('search'),
            reverse('login') + '?next=' + reverse('search'),
            (self.anonymous,))
