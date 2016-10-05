# -*- coding: utf-8 -*-
"""Tests for the views from the flowcelltools Django app
"""

import textwrap

from test_plus.test import TestCase

from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.test import Client

from .. import views
from .. import models
from ..models import SequencingMachine, FlowCell, BarcodeSet, BarcodeSetEntry

from .test_models import SequencingMachineMixin, FlowCellMixin, \
    BarcodeSetMixin, BarcodeSetEntryMixin


# FlowCell related ------------------------------------------------------------


class TestFlowCellListView(TestCase, FlowCellMixin, SequencingMachineMixin):

    def setUp(self):
        self.user = self.make_user()
        self.machine = self._make_machine()
        self.flow_cell_name = '160303_{}_0815_A_BCDEFGHIXX_LABEL'.format(
            self.machine.vendor_id)
        self.flow_cell = self._make_flow_cell(
            self.user, self.flow_cell_name, 8,
            models.FLOWCELL_STATUS_SEQ_COMPLETE, 'John Doe',
            True, 1, models.RTA_VERSION_V2, 151)
        self.client = Client()

    def test_render(self):
        """Simply test that rendering the list view works"""
        response = self.client.get(reverse('flowcell_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['flowcell_list']), 1)


class TestFlowCellCreateView(TestCase, FlowCellMixin, SequencingMachineMixin):

    def setUp(self):
        self.user = self.make_user(password='password')
        self.machine = self._make_machine()
        self.flow_cell_name = '160303_{}_0815_A_BCDEFGHIXX_LABEL'.format(
            self.machine.vendor_id)
        self.client = Client()
        assert self.client.login(username=self.user.username,
                                 password='password')

    def test_render(self):
        """Simply test that post inserts a new flow cell and redirects to the
        list view
        """
        # Check precondition
        self.assertEqual(FlowCell.objects.all().count(), 0)

        # Simulate POST request
        values = {
            'name': self.flow_cell_name,
            'num_lanes': 8,
            'status': models.FLOWCELL_STATUS_INITIAL,
            'operator': 'John Doe',
            'is_paired': True,
            'index_read_count': 1,
            'rta_version': models.RTA_VERSION_V2,
            'read_length': 151,
        }

        # Simulate the POST
        response = self.client.post(reverse('flowcell_create'), values)

        # Check resulting database state
        self.assertEqual(FlowCell.objects.all().count(), 1)
        flow_cell = FlowCell.objects.all()[0]
        self.assertIsNotNone(flow_cell)
        EXPECTED = {
            'id': flow_cell.pk,
            'name': self.flow_cell_name,
            'description': None,
            'owner': self.user.pk,
            'num_lanes': 8,
            'status': models.FLOWCELL_STATUS_INITIAL,
            'operator': 'John Doe',
            'is_paired': True,
            'index_read_count': 1,
            'rta_version': models.RTA_VERSION_V2,
            'sequencing_machine': self.machine.pk,
            'read_length': 151,
        }
        self.assertEqual(model_to_dict(flow_cell), EXPECTED)

        # Check resulting response
        self.assertRedirects(
            response, reverse('flowcell_view', kwargs={'pk': flow_cell.pk}))


class TestFlowCellDetailView(TestCase, FlowCellMixin, SequencingMachineMixin):

    def setUp(self):
        self.user = self.make_user(password='password')
        self.machine = self._make_machine()
        self.flow_cell_name = '160303_{}_0815_A_BCDEFGHIXX_LABEL'.format(
            self.machine.vendor_id)
        self.client = Client()
        self.flow_cell = self._make_flow_cell(
            self.user, self.flow_cell_name, 8,
            models.FLOWCELL_STATUS_SEQ_COMPLETE, 'John Doe',
            True, 1, models.RTA_VERSION_V2, 151)
        assert self.client.login(username=self.user.username,
                                 password='password')

    def test_render(self):
        """Simply test that rendering the detail view works"""
        # Simulate the GET
        response = self.client.get(
            reverse('flowcell_view', kwargs={'pk': self.flow_cell.pk}))

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object'].pk,
                         self.flow_cell.pk)


class TestFlowCellUpdateView(TestCase, FlowCellMixin, SequencingMachineMixin):

    def setUp(self):
        self.user = self.make_user(password='password')
        self.machine = self._make_machine()
        self.flow_cell_name = '160303_{}_0815_A_BCDEFGHIXX_LABEL'.format(
            self.machine.vendor_id)
        self.client = Client()
        self.flow_cell = self._make_flow_cell(
            self.user, self.flow_cell_name, 8,
            models.FLOWCELL_STATUS_SEQ_COMPLETE, 'John Doe',
            True, 1, models.RTA_VERSION_V2, 151)
        assert self.client.login(username=self.user.username,
                                 password='password')

    def test_render(self):
        """Test that the flow cell update POST works"""
        # Check precondition
        self.assertEqual(FlowCell.objects.all().count(), 1)

        # Simulate POST request
        values = model_to_dict(self.flow_cell)
        values['name'] = values['name'] + 'YADAYADAYADA'
        values['status'] = models.FLOWCELL_STATUS_DEMUX_COMPLETE

        # Simulate the POST
        response = self.client.post(
            reverse('flowcell_update', kwargs={'pk': self.flow_cell.pk}),
            values)

        # Check resulting database state
        self.assertEqual(FlowCell.objects.all().count(), 1)
        flow_cell = FlowCell.objects.all()[0]
        self.assertIsNotNone(flow_cell)
        EXPECTED = {
            'id': flow_cell.pk,
            'name': values['name'],
            'description': None,
            'owner': self.user.pk,
            'num_lanes': 8,
            'status': models.FLOWCELL_STATUS_DEMUX_COMPLETE,
            'operator': 'John Doe',
            'is_paired': True,
            'index_read_count': 1,
            'rta_version': models.RTA_VERSION_V2,
            'sequencing_machine': self.machine.pk,
            'read_length': 151,
        }
        self.assertEqual(model_to_dict(flow_cell), EXPECTED)

        # Check resulting response
        self.assertRedirects(
            response, reverse('flowcell_view', kwargs={'pk': flow_cell.pk}))


class TestFlowCellDeleteView(TestCase, FlowCellMixin, SequencingMachineMixin):

    def setUp(self):
        self.user = self.make_user(password='password')
        self.machine = self._make_machine()
        self.flow_cell_name = '160303_{}_0815_A_BCDEFGHIXX_LABEL'.format(
            self.machine.vendor_id)
        self.client = Client()
        self.flow_cell = self._make_flow_cell(
            self.user, self.flow_cell_name, 8,
            models.FLOWCELL_STATUS_SEQ_COMPLETE, 'John Doe',
            True, 1, models.RTA_VERSION_V2, 151)
        assert self.client.login(username=self.user.username,
                                 password='password')

    def test_render(self):
        """Test that the flow cell delete POST works"""
        # Check precondition
        self.assertEqual(FlowCell.objects.all().count(), 1)

        # Simulate the POST
        response = self.client.post(
            reverse('flowcell_delete', kwargs={'pk': self.flow_cell.pk}))

        # Check resulting database state
        self.assertEqual(FlowCell.objects.all().count(), 0)

        # Check resulting response
        self.assertRedirects(
            response, reverse('flowcell_list'))


# SequencingMachine related ---------------------------------------------------


class TestSequencingMachineListView(TestCase, SequencingMachineMixin):

    def setUp(self):
        self.user = self.make_user()
        self.machine = self._make_machine()
        self.client = Client()

    def test_render(self):
        """Simply test that rendering the list view works"""
        response = self.client.get(reverse('instrument_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 1)


class TestSequencingMachineCreateView(TestCase):

    def setUp(self):
        self.user = self.make_user(password='password')
        assert self.client.login(username=self.user.username,
                                 password='password')

    def test_render(self):
        """Simply test that post inserts a new flow cell and redirects to the
        list view
        """
        # Check precondition
        self.assertEqual(SequencingMachine.objects.all().count(), 0)

        # Simulate POST request
        values = {
            'vendor_id': 'NS5001234',
            'label': 'NextSeq#1',
            'description': 'In corner of lab 101',
            'machine_model': models.MACHINE_MODEL_NEXTSEQ500,
            'slot_count': 1,
            'dual_index_workflow': models.INDEX_WORKFLOW_A,
        }

        # Simulate the POST
        response = self.client.post(reverse('instrument_create'), values)

        # Check resulting database state
        self.assertEqual(SequencingMachine.objects.all().count(), 1)
        instrument = SequencingMachine.objects.all()[0]
        self.assertIsNotNone(instrument)
        EXPECTED = {
            'id': instrument.pk,
            'vendor_id': 'NS5001234',
            'label': 'NextSeq#1',
            'description': 'In corner of lab 101',
            'machine_model': models.MACHINE_MODEL_NEXTSEQ500,
            'slot_count': 1,
            'dual_index_workflow': models.INDEX_WORKFLOW_A,
        }
        self.assertEqual(model_to_dict(instrument), EXPECTED)

        # Check resulting response
        self.assertRedirects(
            response, reverse('instrument_view', kwargs={'pk': instrument.pk}))


class TestSequencingMachineDetailView(TestCase, SequencingMachineMixin):

    def setUp(self):
        self.user = self.make_user(password='password')
        self.machine = self._make_machine()
        self.client = Client()
        assert self.client.login(username=self.user.username,
                                 password='password')

    def test_render(self):
        """Simply test that rendering the detail view works"""
        # Simulate the GET
        response = self.client.get(
            reverse('instrument_view', kwargs={'pk': self.machine.pk}))

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object'].pk,
                         self.machine.pk)


class TestSequencingMachineUpdateView(TestCase, SequencingMachineMixin):

    def setUp(self):
        self.user = self.make_user(password='password')
        self.machine = self._make_machine()
        self.client = Client()
        assert self.client.login(username=self.user.username,
                                 password='password')

    def test_render(self):
        """Test that the instrument update POST works"""
        # Check precondition
        self.assertEqual(SequencingMachine.objects.all().count(), 1)

        # Simulate POST request
        values = model_to_dict(self.machine)
        values['vendor_id'] = values['vendor_id'] + 'YADAYADAYADA'
        values['machine_model'] = models.MACHINE_MODEL_HISEQ1000

        # Simulate the POST
        response = self.client.post(
            reverse('instrument_update', kwargs={'pk': self.machine.pk}),
            values)

        # Check resulting database state
        self.assertEqual(SequencingMachine.objects.all().count(), 1)
        machine = SequencingMachine.objects.all()[0]
        self.assertIsNotNone(machine)
        EXPECTED = {
            'id': machine.pk,
            'vendor_id': values['vendor_id'],
            'label': 'NextSeq#1',
            'description': 'In corner of lab 101',
            'machine_model': models.MACHINE_MODEL_HISEQ1000,
            'slot_count': 1,
            'dual_index_workflow': models.INDEX_WORKFLOW_A,
        }
        self.assertEqual(model_to_dict(machine), EXPECTED)

        # Check resulting response
        self.assertRedirects(
            response, reverse('instrument_view', kwargs={'pk': machine.pk}))


class TestSequencingMachineDeleteView(TestCase, SequencingMachineMixin):

    def setUp(self):
        self.user = self.make_user(password='password')
        self.machine = self._make_machine()
        self.client = Client()
        assert self.client.login(username=self.user.username,
                                 password='password')

    def test_render(self):
        """Test that the instrument delete POST works"""
        # Check precondition
        self.assertEqual(SequencingMachine.objects.all().count(), 1)

        # Simulate the POST
        response = self.client.post(
            reverse('instrument_delete', kwargs={'pk': self.machine.pk}))

        # Check resulting database state
        self.assertEqual(SequencingMachine.objects.all().count(), 0)

        # Check resulting response
        self.assertRedirects(
            response, reverse('instrument_list'))


# BarcodeSet related ----------------------------------------------------------


class TestBarcodeSetListView(TestCase, BarcodeSetMixin, BarcodeSetEntryMixin):

    def setUp(self):
        self.user = self.make_user()
        self.barcode_set = self._make_barcode_set()
        self.barcode1 = self._make_barcode_set_entry(
            self.barcode_set, 'AR01', 'CGATCGAT')
        self.barcode2 = self._make_barcode_set_entry(
            self.barcode_set, 'AR02', 'ATTATATA')
        self.client = Client()

    def test_render(self):
        """Simply test that rendering the list view works"""
        response = self.client.get(reverse('barcodeset_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 5)


class TestBarcodeSetCreateView(TestCase):

    def setUp(self):
        self.user = self.make_user(password='password')
        assert self.client.login(username=self.user.username,
                                 password='password')

    def test_render(self):
        """Simply test that post inserts a new flow cell and redirects to the
        list view
        """
        # Check precondition
        self.assertEqual(BarcodeSet.objects.all().count(), 4)

        # Simulate POST request
        values = {
            'name': 'some_barcodes',
            'short_name': 'SBS',
            'description': 'Some barcode set',
        }

        # Simulate the POST
        response = self.client.post(reverse('barcodeset_create'), values)

        # Check resulting database state
        self.assertEqual(
            BarcodeSet.objects.filter(name='some_barcodes').count(), 1)
        barcode_set = BarcodeSet.objects.filter(name='some_barcodes')[0]
        self.assertIsNotNone(barcode_set)
        EXPECTED = {
            'id': barcode_set.pk,
            'name': 'some_barcodes',
            'short_name': 'SBS',
            'description': 'Some barcode set',
        }
        self.assertEqual(model_to_dict(barcode_set), EXPECTED)

        # Check resulting response
        self.assertRedirects(
            response, reverse('barcodeset_view',
                              kwargs={'pk': barcode_set.pk}))


class TestBarcodeSetDetailView(
        TestCase, BarcodeSetMixin, BarcodeSetEntryMixin):

    def setUp(self):
        self.user = self.make_user()
        self.barcode_set = self._make_barcode_set()
        self.barcode1 = self._make_barcode_set_entry(
            self.barcode_set, 'AR01', 'CGATCGAT')
        self.barcode2 = self._make_barcode_set_entry(
            self.barcode_set, 'AR02', 'ATTATAAA')
        self.client = Client()

    def test_render(self):
        """Simply test that rendering the detail view works"""
        # Simulate the GET
        response = self.client.get(
            reverse('barcodeset_view',
                    kwargs={'pk': self.barcode_set.pk}))

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object'].pk,
                         self.barcode_set.pk)


class TestBarcodeSetUpdateView(
        TestCase, BarcodeSetMixin, BarcodeSetEntryMixin):

    def setUp(self):
        self.user = self.make_user()
        self.barcode_set = self._make_barcode_set()
        self.barcode1 = self._make_barcode_set_entry(
            self.barcode_set, 'AR01', 'CGATCGAT')
        self.barcode2 = self._make_barcode_set_entry(
            self.barcode_set, 'AR02', 'ATTATAAA')
        self.client = Client()

    def test_render(self):
        """Test that the barcode set update POST works"""
        # Check precondition
        self.assertEqual(BarcodeSet.objects.all().count(), 5)

        # Simulate POST request
        values = model_to_dict(self.barcode_set)
        values['name'] = 'Another name'
        values['description'] = 'This is the description'

        # Simulate the POST
        response = self.client.post(
            reverse('barcodeset_update', kwargs={'pk': self.barcode_set.pk}),
            values)

        # Check resulting database state
        self.assertEqual(BarcodeSet.objects.all().count(), 5)
        barcode_set = BarcodeSet.objects.get(pk=self.barcode_set.pk)
        EXPECTED = {
            'id': barcode_set.pk,
            'name': values['name'],
            'short_name': self.barcode_set.short_name,
            'description': values['description'],
        }
        self.assertEqual(model_to_dict(barcode_set), EXPECTED)

        # Check resulting response
        self.assertRedirects(
            response, reverse('barcodeset_view',
                              kwargs={'pk': barcode_set.pk}))


class TestBarcodeSetDeleteView(
        TestCase, BarcodeSetMixin, BarcodeSetEntryMixin):

    def setUp(self):
        self.user = self.make_user()
        self.barcode_set = self._make_barcode_set()
        self.barcode1 = self._make_barcode_set_entry(
            self.barcode_set, 'AR01', 'CGATCGAT')
        self.barcode2 = self._make_barcode_set_entry(
            self.barcode_set, 'AR02', 'ATTATAAA')
        self.client = Client()

    def test_render(self):
        """Test that the barcode set delete POST works"""
        # Check precondition
        self.assertEqual(BarcodeSet.objects.all().count(), 5)
        self.assertEqual(BarcodeSetEntry.objects.all().count(), 66)

        # Simulate the POST
        response = self.client.post(
            reverse('barcodeset_delete',
                    kwargs={'pk': self.barcode_set.pk}))

        # Check resulting database state
        self.assertEqual(BarcodeSet.objects.all().count(), 4)
        self.assertEqual(BarcodeSetEntry.objects.all().count(), 64)

        # Check resulting response
        self.assertRedirects(
            response, reverse('barcodeset_list'))


class TestBarcodeSetUpdateEntriesView(
        TestCase, BarcodeSetMixin, BarcodeSetEntryMixin):

    def setUp(self):
        self.user = self.make_user()
        self.barcode_set = self._make_barcode_set()
        self.barcode1 = self._make_barcode_set_entry(
            self.barcode_set, 'AR01', 'CGATCGAT')
        self.barcode2 = self._make_barcode_set_entry(
            self.barcode_set, 'AR02', 'ATTATAAA')
        self.client = Client()

    def _test_update(self, more_values):
        """Helper for testing the update functionality"""
        # Check precondition
        self.assertEqual(BarcodeSet.objects.all().count(), 5)
        self.assertEqual(BarcodeSetEntry.objects.all().count(), 66)

        values = {
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1',
            'form-0-id': self.barcode1.pk,
            'form-0-name': 'UPDATED',
            'form-0-sequence': 'GATTACA',
            'form-1-id': self.barcode2.pk,
            'form-1-name': self.barcode2.name,
            'form-1-sequence': self.barcode2.sequence,
        }
        values.update(more_values)

        # Simulate the POST
        response = self.client.post(
            reverse('barcodeset_updateentries',
                    kwargs={'pk': self.barcode_set.pk}),
            values)

        # Check resulting database state
        self.assertEqual(BarcodeSet.objects.all().count(), 5)
        self.assertEqual(BarcodeSetEntry.objects.all().count(), 66)

        barcode1 = BarcodeSetEntry.objects.get(pk=self.barcode1.pk)
        self.assertEquals(barcode1.name, 'UPDATED')
        self.assertEquals(barcode1.sequence, 'GATTACA')
        barcode2 = BarcodeSetEntry.objects.get(pk=self.barcode2.pk)
        self.assertEquals(barcode2.name, self.barcode2.name)
        self.assertEquals(barcode2.sequence, self.barcode2.sequence)

        return response

    def test_update(self):
        """Test that updating barcode set entries works correctly"""
        response = self._test_update({'submit': 'submit'})
        # Check resulting response
        self.assertRedirects(
            response, reverse('barcodeset_view',
                              kwargs={'pk': self.barcode_set.pk}))

    def test_update_more(self):
        """Test that updating barcode set entries works correctly"""
        response = self._test_update({'submit_more': 'submit_more'})
        # Check resulting response
        self.assertRedirects(
            response, reverse('barcodeset_updateentries',
                              kwargs={'pk': self.barcode_set.pk}))

    def test_add(self):
        """Test that adding barcode set entries works correctly"""
        # Check precondition
        self.assertEqual(BarcodeSet.objects.all().count(), 5)
        self.assertEqual(BarcodeSetEntry.objects.all().count(), 66)

        values = {
            'form-TOTAL_FORMS': '3',
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '2',
            'form-0-id': self.barcode1.pk,
            'form-0-name': 'UPDATED',
            'form-0-sequence': 'GATTACA',
            'form-1-id': self.barcode2.pk,
            'form-1-name': self.barcode2.name,
            'form-1-sequence': self.barcode2.sequence,
            'form-2-id': '',
            'form-2-name': 'AR03',
            'form-2-sequence': 'TAAATAAA',
        }

        # Ensure that no such barcode exists yet
        self.assertEquals(
            BarcodeSetEntry.objects.filter(sequence='TAAATAAA').count(), 0)

        # Simulate the POST
        response = self.client.post(
            reverse('barcodeset_updateentries',
                    kwargs={'pk': self.barcode_set.pk}),
            values)

        # Check resulting database state
        self.assertEqual(BarcodeSet.objects.all().count(), 5)
        self.assertEqual(BarcodeSetEntry.objects.all().count(), 67)

        barcode1 = BarcodeSetEntry.objects.get(pk=self.barcode1.pk)
        self.assertEquals(barcode1.name, 'UPDATED')
        self.assertEquals(barcode1.sequence, 'GATTACA')
        barcode2 = BarcodeSetEntry.objects.get(pk=self.barcode2.pk)
        self.assertEquals(barcode2.name, self.barcode2.name)
        self.assertEquals(barcode2.sequence, self.barcode2.sequence)
        self.assertEquals(
            BarcodeSetEntry.objects.filter(sequence='TAAATAAA').count(), 1)
        barcode3 = BarcodeSetEntry.objects.filter(sequence='TAAATAAA')[0]
        self.assertEquals(barcode3.name, 'AR03')
        self.assertEquals(barcode3.sequence, 'TAAATAAA')

        # Check resulting response
        self.assertRedirects(
            response, reverse('barcodeset_view',
                              kwargs={'pk': self.barcode_set.pk}))

    def test_delete(self):
        """Test that deleting barcode set entries works correctly"""
        # Check precondition
        self.assertEqual(BarcodeSet.objects.all().count(), 5)
        self.assertEqual(BarcodeSetEntry.objects.all().count(), 66)

        values = {
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1',
            'form-0-id': self.barcode1.pk,
            'form-0-name': 'UPDATED',
            'form-0-sequence': 'GATTACA',
            'form-1-id': self.barcode2.pk,
            'form-1-name': self.barcode2.name,
            'form-1-sequence': self.barcode2.sequence,
            'form-1-DELETE': 'on',
        }

        # Simulate the POST
        response = self.client.post(
            reverse('barcodeset_updateentries',
                    kwargs={'pk': self.barcode_set.pk}),
            values)

        # Check resulting database state
        self.assertEqual(BarcodeSet.objects.all().count(), 5)
        self.assertEqual(BarcodeSetEntry.objects.all().count(), 65)

        barcode1 = BarcodeSetEntry.objects.get(pk=self.barcode1.pk)
        self.assertEquals(barcode1.name, 'UPDATED')
        self.assertEquals(barcode1.sequence, 'GATTACA')
        self.assertEquals(
            BarcodeSetEntry.objects.filter(pk=self.barcode2.pk).count(), 0)

        # Check resulting response
        self.assertRedirects(
            response, reverse('barcodeset_view',
                              kwargs={'pk': self.barcode_set.pk}))


class TestBarcodeSetExportView(
        TestCase, BarcodeSetMixin, BarcodeSetEntryMixin):

    def setUp(self):
        self.user = self.make_user()
        self.barcode_set = self._make_barcode_set()
        self.barcode1 = self._make_barcode_set_entry(
            self.barcode_set, 'AR01', 'CGATCGAT')
        self.barcode2 = self._make_barcode_set_entry(
            self.barcode_set, 'AR02', 'ATTATAAA')
        self.client = Client()

    def test_render(self):
        """Simply test that rendering the detail view works"""
        # Simulate the GET
        response = self.client.get(
            reverse('barcodeset_export',
                    kwargs={'pk': self.barcode_set.pk}))

        # Check response
        self.assertEqual(response.status_code, 200)
        EXPECTED = textwrap.dedent(r"""
            {
              "name": "Agilent SureSelect XT Test",
              "short_name": "SureSelectTest",
              "description": null,
              "entries": [
                {
                  "name": "AR01",
                  "sequence": "CGATCGAT"
                },
                {
                  "name": "AR02",
                  "sequence": "ATTATAAA"
                }
              ]
            }
            """).lstrip()
        self.assertEqual(response.content.decode('utf-8'), EXPECTED)
