# -*- coding: utf-8 -*-
""""Tests for permission checking in the API."""

import datetime
import uuid

from django.forms.models import model_to_dict
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from .. import models

from .test_models import (
    SequencingMachineMixin, FlowCellMixin, BarcodeSetMixin)
from .test_permissions import TestPermissionBase


# TODO: creation is not tested at the moment


class TestApiPermissionBase(TestPermissionBase):

    def assert_render_200_ok(self, url, users, method='get', setup_again=(), *args, **kwargs):
        for user in users:
            client = APIClient()
            client.force_authenticate(user=user)
            response = getattr(client, method)(url, *args, **kwargs, format='json')
            self.assertEquals(response.status_code, 200,
                              'user={}'.format(user))
            for fun in setup_again:
                fun()

    def assert_render_204_no_content(self, url, users, method='get', setup_again=(), *args, **kwargs):
        for user in users:
            client = APIClient()
            client.force_authenticate(user=user)
            response = getattr(client, method)(url, *args, **kwargs, format='json')
            self.assertEquals(response.status_code, 204,
                              'user={}'.format(user))
            for fun in setup_again:
                fun()

    def assert_render_403_permission_denied(self, url, users, method='get', *args, **kwargs):
        for user in users:
            client = APIClient()
            client.force_authenticate(user=user)
            response = getattr(client, method)(url, *args, **kwargs, format='json')
            self.assertEquals(response.status_code, 403,
                              'user={}'.format(user))


class TestPermissionsSequencingMachine(SequencingMachineMixin, TestApiPermissionBase):

    def setUp(self):
        super().setUp()
        self.sequencing_machine_uuid = uuid.uuid4()
        self.setupMembersIdempotently()

    def setupMembersIdempotently(self):
        """Setup member in an idempotent fashion"""
        if hasattr(self, 'sequencing_machine'):
            self.sequencing_machine.delete()
        self.sequencing_machine = self._make_machine(uuid=self.sequencing_machine_uuid)

    def test_sequencing_machine_list(self):
        URL = reverse('api_v1:sequencingmachine-list')
        GOOD = (self.inst_op, self.guest, self.demux_op, self.demux_admin,
                self.import_bot, self.superuser)
        BAD = (self.anonymous, self.nogroup)
        self.assert_render_200_ok(URL, GOOD, 'get')
        self.assert_render_403_permission_denied(URL, BAD, 'get')

    def test_sequencing_machine_retrieve(self):
        URL = reverse('api_v1:sequencingmachine-detail', kwargs={'uuid': self.sequencing_machine.uuid})
        GOOD = (self.inst_op, self.guest, self.demux_op, self.demux_admin,
                self.import_bot, self.superuser)
        BAD = (self.anonymous, self.nogroup)
        self.assert_render_200_ok(URL, GOOD, 'get')
        self.assert_render_403_permission_denied(URL, BAD, 'get')

    def test_sequencing_machine_destroy(self):
        URL = reverse('api_v1:sequencingmachine-detail', kwargs={'uuid': self.sequencing_machine.uuid})
        GOOD = (self.demux_admin, self.superuser)
        BAD = (self.anonymous, self.nogroup, self.inst_op, self.guest, self.demux_op, self.import_bot)
        self.assert_render_204_no_content(URL, GOOD, 'delete', (self.setupMembersIdempotently,))
        self.assert_render_403_permission_denied(URL, BAD, 'delete')

    def test_sequencing_machine_partial_update(self):
        URL = reverse('api_v1:sequencingmachine-detail', kwargs={'uuid': self.sequencing_machine.uuid})
        GOOD = (self.demux_admin, self.superuser)
        BAD = (self.anonymous, self.nogroup, self.inst_op, self.guest, self.demux_op, self.import_bot)
        data = {'name': 'New name'}
        self.assert_render_200_ok(URL, GOOD, 'patch', (self.setupMembersIdempotently,), data=data)
        self.assert_render_403_permission_denied(URL, BAD, 'patch', data=data)

    def test_sequencing_machine_update(self):
        URL = reverse('api_v1:sequencingmachine-detail', kwargs={'uuid': self.sequencing_machine.uuid})
        GOOD = (self.demux_admin, self.superuser)
        BAD = (self.anonymous, self.nogroup, self.inst_op, self.guest, self.demux_op, self.import_bot)
        data = {
            'vendor_id': 'NS5001234',
            'label': 'NextSeq#1',
            'description': 'In corner of lab 101',
            'machine_model': models.MACHINE_MODEL_NEXTSEQ500,
            'slot_count': 1,
            'dual_index_workflow': models.INDEX_WORKFLOW_A,
        }
        self.assert_render_200_ok(URL, GOOD, 'put', (self.setupMembersIdempotently,), data=data)
        self.assert_render_403_permission_denied(URL, BAD, 'put', data=data)


class TestPermissionsBarcodeSetApi(BarcodeSetMixin, TestApiPermissionBase):

    def setUp(self):
        super().setUp()
        self.barcode_set_uuid = uuid.uuid4()
        self.setupMembersIdempotently()

    def setupMembersIdempotently(self):
        """Setup member in an idempotent fashion"""
        if hasattr(self, 'barcode_set'):
            self.barcode_set.delete()
        self.barcode_set = self._make_barcode_set(uuid=self.barcode_set_uuid)

    def test_barcodeset_list(self):
        URL = reverse('api_v1:barcodeset-list')
        GOOD = (self.inst_op, self.guest, self.demux_op, self.demux_admin,
                self.import_bot, self.superuser)
        BAD = (self.anonymous, self.nogroup)
        self.assert_render_200_ok(URL, GOOD, 'get')
        self.assert_render_403_permission_denied(URL, BAD, 'get')

    def test_barcodeset_retrieve(self):
        URL = reverse('api_v1:barcodeset-detail', kwargs={'uuid': self.barcode_set.uuid})
        GOOD = (self.inst_op, self.guest, self.demux_op, self.demux_admin,
                self.import_bot, self.superuser)
        BAD = (self.anonymous, self.nogroup)
        self.assert_render_200_ok(URL, GOOD, 'get')
        self.assert_render_403_permission_denied(URL, BAD, 'get')

    def test_barcodeset_destroy(self):
        URL = reverse('api_v1:barcodeset-detail', kwargs={'uuid': self.barcode_set.uuid})
        GOOD = (self.demux_admin, self.superuser)
        BAD = (self.anonymous, self.nogroup, self.inst_op, self.guest, self.demux_op, self.import_bot)
        self.assert_render_204_no_content(URL, GOOD, 'delete', (self.setupMembersIdempotently,))
        self.assert_render_403_permission_denied(URL, BAD, 'delete')

    def test_barcodeset_partial_update(self):
        URL = reverse('api_v1:barcodeset-detail', kwargs={'uuid': self.barcode_set.uuid})
        GOOD = (self.demux_admin, self.superuser)
        BAD = (self.anonymous, self.nogroup, self.inst_op, self.guest, self.demux_op, self.import_bot)
        data = {'name': 'New name'}
        self.assert_render_200_ok(URL, GOOD, 'patch', (self.setupMembersIdempotently,), data=data)
        self.assert_render_403_permission_denied(URL, BAD, 'patch', data=data)

    def test_barcodeset_update(self):
        URL = reverse('api_v1:barcodeset-detail', kwargs={'uuid': self.barcode_set.uuid})
        GOOD = (self.demux_admin, self.superuser)
        BAD = (self.anonymous, self.nogroup, self.inst_op, self.guest, self.demux_op, self.import_bot)
        data = {
            'name': 'New name',
            'short_name': 'NewShortname',
        }
        self.assert_render_200_ok(URL, GOOD, 'put', (self.setupMembersIdempotently,), data=data)
        self.assert_render_403_permission_denied(URL, BAD, 'put', data=data)


class TestPermissionsFlowCellApi(FlowCellMixin, SequencingMachineMixin, TestApiPermissionBase):

    def setUp(self):
        super().setUp()
        self.inst_op_flow_cell_uuid = uuid.uuid4()
        self.bot_flow_cell_uuid = uuid.uuid4()
        self.machine = self._make_machine()
        self.setupMembersIdempotently()

    def setupMembersIdempotently(self):
        """Setup member in an idempotent fashion"""
        if hasattr(self, 'inst_op_flow_cell'):
            self.inst_op_flow_cell.delete()
        if hasattr(self, 'import_bot_flow_cell'):
            self.import_bot_flow_cell.delete()
        self.inst_op_flow_cell = self._make_flow_cell(
            self.inst_op, datetime.date(2016, 3, 3), self.machine, 815, 'A',
            'BCDEFGHIXX', 'LABEL', 8, models.FLOWCELL_STATUS_SEQ_COMPLETE,
            'John Doe', True, 1, models.RTA_VERSION_V2, 151, 'Description',
            uuid=self.inst_op_flow_cell_uuid)
        self.import_bot_flow_cell = self._make_flow_cell(
            self.import_bot, datetime.date(2016, 3, 3), self.machine, 816, 'A',
            'BCDEFGHIXY', 'LABEL', 8, models.FLOWCELL_STATUS_SEQ_COMPLETE,
            'John Doe', True, 1, models.RTA_VERSION_V2, 151, 'Description',
            uuid=self.bot_flow_cell_uuid)

    def test_flowcell_list(self):
        URL = reverse('api_v1:flowcell-list')
        GOOD = (self.inst_op, self.guest, self.demux_op, self.demux_admin,
                self.import_bot, self.superuser)
        BAD = (self.anonymous, self.nogroup)
        self.assert_render_200_ok(URL, GOOD, 'get')
        self.assert_render_403_permission_denied(URL, BAD, 'get')

    def test_flowcell_retrieve(self):
        URL = reverse('api_v1:flowcell-detail', kwargs={'uuid': self.import_bot_flow_cell.uuid})
        GOOD = (self.inst_op, self.guest, self.demux_op, self.demux_admin,
                self.import_bot, self.superuser)
        BAD = (self.anonymous, self.nogroup)
        self.assert_render_200_ok(URL, GOOD, 'get')
        self.assert_render_403_permission_denied(URL, BAD, 'get')

    def test_flowcell_destroy_inst_op_owned(self):
        URL = reverse('api_v1:flowcell-detail', kwargs={'uuid': self.inst_op_flow_cell.uuid})
        GOOD = (self.demux_admin, self.superuser, self.demux_op, self.inst_op)
        BAD = (self.anonymous, self.nogroup, self.guest, self.import_bot)
        self.assert_render_204_no_content(URL, GOOD, 'delete', (self.setupMembersIdempotently,))
        self.assert_render_403_permission_denied(URL, BAD, 'delete')

    def test_flowcell_destroy_import_bot_owned(self):
        URL = reverse('api_v1:flowcell-detail', kwargs={'uuid': self.import_bot_flow_cell.uuid})
        GOOD = (self.demux_admin, self.superuser, self.demux_op, self.import_bot)
        BAD = (self.anonymous, self.nogroup, self.inst_op, self.guest)
        self.assert_render_204_no_content(URL, GOOD, 'delete', (self.setupMembersIdempotently,))
        self.assert_render_403_permission_denied(URL, BAD, 'delete')

    def test_flowcell_partial_update_inst_op_owned(self):
        URL = reverse('api_v1:flowcell-detail', kwargs={'uuid': self.inst_op_flow_cell.uuid})
        GOOD = (self.demux_admin, self.superuser, self.demux_op, self.inst_op)
        BAD = (self.anonymous, self.nogroup, self.guest, self.import_bot)
        data = {'operator': 'New Operator'}
        self.assert_render_200_ok(URL, GOOD, 'patch', (self.setupMembersIdempotently,), data=data)
        self.assert_render_403_permission_denied(URL, BAD, 'patch', data=data)

    def test_flowcell_partial_update_import_bot_owned(self):
        URL = reverse('api_v1:flowcell-detail', kwargs={'uuid': self.import_bot_flow_cell.uuid})
        GOOD = (self.demux_admin, self.superuser, self.demux_op, self.import_bot)
        BAD = (self.anonymous, self.nogroup, self.inst_op, self.guest)
        data = {'operator': 'New Operator'}
        self.assert_render_200_ok(URL, GOOD, 'patch', (self.setupMembersIdempotently,), data=data)
        self.assert_render_403_permission_denied(URL, BAD, 'patch', data=data)

    def test_flowcell_update_inst_op_owned(self):
        URL = reverse('api_v1:flowcell-detail', kwargs={'uuid': self.inst_op_flow_cell.uuid})
        GOOD = (self.demux_admin, self.superuser, self.demux_op, self.inst_op)
        BAD = (self.anonymous, self.nogroup, self.guest, self.import_bot)
        data = model_to_dict(self.inst_op_flow_cell)
        self.assert_render_200_ok(URL, GOOD, 'put', (self.setupMembersIdempotently,), data=data)
        self.assert_render_403_permission_denied(URL, BAD, 'put', data=data)

    def test_flowcell_update_import_bot_owned(self):
        URL = reverse('api_v1:flowcell-detail', kwargs={'uuid': self.import_bot_flow_cell.uuid})
        GOOD = (self.demux_admin, self.superuser, self.demux_op, self.import_bot)
        BAD = (self.anonymous, self.nogroup, self.inst_op, self.guest)
        data = model_to_dict(self.import_bot_flow_cell)
        self.assert_render_200_ok(URL, GOOD, 'put', (self.setupMembersIdempotently,), data=data)
        self.assert_render_403_permission_denied(URL, BAD, 'put', data=data)
