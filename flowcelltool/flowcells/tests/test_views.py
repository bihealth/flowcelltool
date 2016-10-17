# -*- coding: utf-8 -*-
"""Tests for the views from the flowcelltools Django app
"""

import io
import textwrap

from test_plus.test import TestCase

from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.test import Client
from django.contrib.contenttypes.models import ContentType

from .. import views
from .. import models
from ..models import SequencingMachine, FlowCell, BarcodeSet, \
    BarcodeSetEntry, Library

from ...threads import models as threads_models

from .test_models import SequencingMachineMixin, FlowCellMixin, \
    BarcodeSetMixin, BarcodeSetEntryMixin, LibraryMixin


# Helper Classes --------------------------------------------------------------


class SuperUserTestCase(TestCase):

    def make_user(self, *args,  **kwargs):
        kwargs.setdefault('username', 'testuser')
        kwargs.setdefault('password', 'password')
        user = super().make_user(*args, **kwargs)
        user.is_superuser = True
        user.save()
        return user


# FlowCell related ------------------------------------------------------------


class TestFlowCellListView(
        SuperUserTestCase, FlowCellMixin, SequencingMachineMixin):

    def setUp(self):
        self.user = self.make_user()
        self.machine = self._make_machine()
        self.flow_cell_name = '160303_{}_0815_A_BCDEFGHIXX_LABEL'.format(
            self.machine.vendor_id)
        self.flow_cell = self._make_flow_cell(
            self.user, self.flow_cell_name, 8,
            models.FLOWCELL_STATUS_SEQ_COMPLETE, 'John Doe',
            True, 1, models.RTA_VERSION_V2, 151, 'Description')

    def test_render(self):
        """Simply test that rendering the list view works"""
        with self.login(self.user):
            response = self.client.get(reverse('flowcell_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['flowcell_list']), 1)


class TestFlowCellCreateView(
        SuperUserTestCase, FlowCellMixin, SequencingMachineMixin):

    def setUp(self):
        self.user = self.make_user()
        self.machine = self._make_machine()
        self.flow_cell_name = '160303_{}_0815_A_BCDEFGHIXX_LABEL'.format(
            self.machine.vendor_id)
        self.client = Client()

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
        with self.login(self.user):
            response = self.client.post(reverse('flowcell_create'), values)

        # Check resulting database state
        self.assertEqual(FlowCell.objects.all().count(), 1)
        flow_cell = FlowCell.objects.all()[0]
        self.assertIsNotNone(flow_cell)
        EXPECTED = {
            'id': flow_cell.pk,
            'name': self.flow_cell_name,
            'description': '',
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
        with self.login(self.user):
            self.assertRedirects(
                response, reverse('flowcell_view', kwargs={'pk': flow_cell.pk}))


class TestFlowCellDetailView(
        SuperUserTestCase, FlowCellMixin, SequencingMachineMixin):

    def setUp(self):
        self.user = self.make_user()
        self.machine = self._make_machine()
        self.flow_cell_name = '160303_{}_0815_A_BCDEFGHIXX_LABEL'.format(
            self.machine.vendor_id)
        self.client = Client()
        self.flow_cell = self._make_flow_cell(
            self.user, self.flow_cell_name, 8,
            models.FLOWCELL_STATUS_SEQ_COMPLETE, 'John Doe',
            True, 1, models.RTA_VERSION_V2, 151, 'Description')

    def test_render(self):
        """Simply test that rendering the detail view works"""
        # Simulate the GET
        with self.login(self.user):
            response = self.client.get(
                reverse('flowcell_view', kwargs={'pk': self.flow_cell.pk}))

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object'].pk,
                         self.flow_cell.pk)


class TestFlowCellUpdateView(
        SuperUserTestCase, FlowCellMixin, SequencingMachineMixin):

    def setUp(self):
        self.user = self.make_user()
        self.machine = self._make_machine()
        self.flow_cell_name = '160303_{}_0815_A_BCDEFGHIXX_LABEL'.format(
            self.machine.vendor_id)
        self.client = Client()
        self.flow_cell = self._make_flow_cell(
            self.user, self.flow_cell_name, 8,
            models.FLOWCELL_STATUS_SEQ_COMPLETE, 'John Doe',
            True, 1, models.RTA_VERSION_V2, 151, 'Description')

    def test_render(self):
        """Test that the flow cell update POST works"""
        # Check precondition
        self.assertEqual(FlowCell.objects.all().count(), 1)

        # Simulate POST request
        values = model_to_dict(self.flow_cell)
        values['name'] = values['name'] + 'YADAYADAYADA'
        values['status'] = models.FLOWCELL_STATUS_DEMUX_COMPLETE

        # Simulate the POST
        with self.login(self.user):
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
            'description': 'Description',
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
        with self.login(self.user):
            self.assertRedirects(
                response, reverse('flowcell_view', kwargs={'pk': flow_cell.pk}))


class TestFlowCellDeleteView(
        SuperUserTestCase, FlowCellMixin, SequencingMachineMixin):

    def setUp(self):
        self.user = self.make_user()
        self.machine = self._make_machine()
        self.flow_cell_name = '160303_{}_0815_A_BCDEFGHIXX_LABEL'.format(
            self.machine.vendor_id)
        self.client = Client()
        self.flow_cell = self._make_flow_cell(
            self.user, self.flow_cell_name, 8,
            models.FLOWCELL_STATUS_SEQ_COMPLETE, 'John Doe',
            True, 1, models.RTA_VERSION_V2, 151, 'Description')

    def test_render(self):
        """Test that the flow cell delete POST works"""
        # Check precondition
        self.assertEqual(FlowCell.objects.all().count(), 1)

        # Simulate the POST
        with self.login(self.user):
            response = self.client.post(
                reverse('flowcell_delete', kwargs={'pk': self.flow_cell.pk}))

        # Check resulting database state
        self.assertEqual(FlowCell.objects.all().count(), 0)

        # Check resulting response
        with self.login(self.user):
            self.assertRedirects(
                response, reverse('flowcell_list'))


class TestLibraryUpdateView(
    SuperUserTestCase, FlowCellMixin, SequencingMachineMixin, LibraryMixin,
    BarcodeSetMixin, BarcodeSetEntryMixin):

    def setUp(self):
        self.user = self.make_user()
        self.client = Client()
        # Create Machine
        self.machine = self._make_machine()
        # Create Barcode set
        self.barcode_set = self._make_barcode_set()
        self.barcode1 = self._make_barcode_set_entry(
            self.barcode_set, 'AR01', 'CGATCGAT')
        self.barcode2 = self._make_barcode_set_entry(
            self.barcode_set, 'AR02', 'ATTATATA')
        # Create Flow cell
        self.flow_cell_name = '160303_{}_0815_A_BCDEFGHIXX_LABEL'.format(
            self.machine.vendor_id)
        self.flow_cell = self._make_flow_cell(
            self.user, self.flow_cell_name, 8,
            models.FLOWCELL_STATUS_SEQ_COMPLETE, 'John Doe',
            True, 1, models.RTA_VERSION_V2, 151, 'Description')
        self.library1 = self._make_library(
            self.flow_cell, 'LIB_001', models.REFERENCE_HUMAN,
            self.barcode_set, self.barcode1, [1, 2], None, None)
        self.library2 = self._make_library(
            self.flow_cell, 'LIB_002', models.REFERENCE_HUMAN,
            self.barcode_set, self.barcode2, [1, 2], None, None)

    def _test_update(self, more_values):
        """Helper for testing the update functionality"""
        # Check precondition
        self.assertEqual(FlowCell.objects.all().count(), 1)
        self.assertEqual(Library.objects.all().count(), 2)

        values = {
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1',
            'form-0-id': self.library1.pk,
            'form-0-name': 'UPDATED',
            'form-0-reference': 'mm9',
            'form-0-barcode_set': self.library1.barcode_set.pk,
            'form-0-barcode': self.library1.barcode.pk,
            'form-0-barcode_set2': '',
            'form-0-barcode2': '',
            'form-0-lane_numbers': ','.join(
                map(str, self.library1.lane_numbers)),
            'form-1-id': self.library2.pk,
            'form-1-name': 'UPDATED_2',
            'form-1-reference': self.library2.reference,
            'form-1-barcode_set': self.library2.barcode_set.pk,
            'form-1-barcode': self.library2.barcode.pk,
            'form-1-barcode_set2': '',
            'form-1-barcode2': '',
            'form-1-lane_numbers': ','.join(
                map(str, self.library2.lane_numbers)),
        }
        values.update(more_values)

        # Simulate the POST
        with self.login(self.user):
            response = self.client.post(
                reverse('flowcell_updatelibraries',
                        kwargs={'pk': self.flow_cell.pk}),
                values)

        # Check resulting database state
        self.assertEqual(BarcodeSet.objects.all().count(), 1)
        self.assertEqual(BarcodeSetEntry.objects.all().count(), 2)

        library1 = Library.objects.get(pk=self.library1.pk)
        self.assertEquals(library1.name, 'UPDATED')
        self.assertEquals(library1.reference, 'mm9')
        self.assertEquals(library1.barcode_set, self.barcode_set)
        self.assertEquals(library1.barcode, self.barcode1)
        self.assertEquals(library1.barcode_set2, None)
        self.assertEquals(library1.barcode2, None)
        self.assertEquals(library1.lane_numbers, [1, 2])
        library2 = Library.objects.get(pk=self.library2.pk)
        self.assertEquals(library2.name, 'UPDATED_2')
        self.assertEquals(library2.reference, self.library2.reference)
        self.assertEquals(library2.barcode_set, self.barcode_set)
        self.assertEquals(library2.barcode, self.barcode2)
        self.assertEquals(library2.barcode_set2, None)
        self.assertEquals(library2.barcode2, None)
        self.assertEquals(library2.lane_numbers, [1, 2])

        return response

    def test_update(self):
        """Test that updating library entries works correctly"""
        response = self._test_update({'submit': 'submit'})
        # Check resulting response
        with self.login(self.user):
            self.assertRedirects(
                response, reverse('flowcell_view',
                                kwargs={'pk': self.flow_cell.pk}))

    def test_update_more(self):
        """Test that updating library entries works correctly (submit more)"""
        response = self._test_update({'submit_more': 'submit_more'})
        # Check resulting response
        with self.login(self.user):
            self.assertRedirects(
                response, reverse('flowcell_updatelibraries',
                                kwargs={'pk': self.flow_cell.pk}))

    def test_add(self):
        """Test that adding libraries works correctly"""
        # Check precondition
        self.assertEqual(FlowCell.objects.all().count(), 1)
        self.assertEqual(Library.objects.all().count(), 2)

        values = {
            'form-TOTAL_FORMS': '3',
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '2',
            'form-0-id': self.library1.pk,
            'form-0-name': self.library1.name,
            'form-0-reference': self.library1.reference,
            'form-0-barcode_set': self.library1.barcode_set.pk,
            'form-0-barcode': self.library1.barcode.pk,
            'form-0-barcode_set2': '',
            'form-0-barcode2': '',
            'form-0-lane_numbers': ','.join(
                map(str, self.library1.lane_numbers)),
            'form-1-id': self.library2.pk,
            'form-1-name': self.library2.name,
            'form-1-reference': self.library2.reference,
            'form-1-barcode_set': self.library2.barcode_set.pk,
            'form-1-barcode': self.library2.barcode.pk,
            'form-1-barcode_set2': '',
            'form-1-barcode2': '',
            'form-1-lane_numbers': ','.join(
                map(str, self.library2.lane_numbers)),
            'form-2-name': 'LIB_003',
            'form-2-reference': 'hg19',
            'form-2-barcode_set': self.library2.barcode_set.pk,
            'form-2-barcode': self.library2.barcode.pk,
            'form-2-barcode_set2': '',
            'form-2-barcode2': '',
            'form-2-lane_numbers': '5,6',
        }

        # Ensure that no such barcode exists yet
        self.assertEquals(
            Library.objects.filter(name='LIB_003').count(), 0)

        # Simulate the POST
        with self.login(self.user):
            response = self.client.post(
                reverse('flowcell_updatelibraries',
                        kwargs={'pk': self.flow_cell.pk}),
                values)

        # Check resulting database state
        self.assertEqual(FlowCell.objects.all().count(), 1)
        self.assertEqual(Library.objects.all().count(), 3)

        library1 = Library.objects.get(pk=self.library1.pk)
        self.assertEquals(library1.name, self.library1.name)
        library2 = Library.objects.get(pk=self.library2.pk)
        self.assertEquals(library2.name, self.library2.name)
        # Newly created library
        self.assertEquals(
            Library.objects.filter(name='LIB_003').count(), 1)
        library3 = Library.objects.filter(name='LIB_003')[0]
        self.assertEquals(library3.name, 'LIB_003')
        self.assertEquals(library3.reference, 'hg19')
        self.assertEquals(library3.barcode_set, self.barcode_set)
        self.assertEquals(library3.barcode, self.barcode2)
        self.assertEquals(library3.barcode_set2, None)
        self.assertEquals(library3.barcode2, None)
        self.assertEquals(library3.lane_numbers, [5, 6])

        # Check resulting response
        with self.login(self.user):
            self.assertRedirects(
                response, reverse('flowcell_view',
                                kwargs={'pk': self.flow_cell.pk}))

    def test_delete(self):
        """Test that deleting libraries works correctly"""
        # Check precondition
        self.assertEqual(FlowCell.objects.all().count(), 1)
        self.assertEqual(Library.objects.all().count(), 2)

        values = {
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1',
            'form-0-id': self.library1.pk,
            'form-0-name': 'UPDATED',
            'form-0-reference': 'mm9',
            'form-0-barcode_set': self.library1.barcode_set.pk,
            'form-0-barcode': self.library1.barcode.pk,
            'form-0-barcode_set2': '',
            'form-0-barcode2': '',
            'form-0-lane_numbers': ','.join(
                map(str, self.library1.lane_numbers)),
            'form-1-id': self.library2.pk,
            'form-1-name': 'UPDATED_2',
            'form-1-reference': self.library2.reference,
            'form-1-barcode_set': self.library2.barcode_set.pk,
            'form-1-barcode': '',
            'form-1-barcode_set2': '',
            'form-1-barcode2': '',
            'form-1-lane_numbers': ','.join(
                map(str, self.library2.lane_numbers)),
            'form-1-DELETE': 'on',
        }

        # Simulate the POST
        with self.login(self.user):
            response = self.client.post(
                reverse('flowcell_updatelibraries',
                        kwargs={'pk': self.flow_cell.pk}),
                values)

        # Check resulting database state
        self.assertEqual(FlowCell.objects.all().count(), 1)
        self.assertEqual(Library.objects.all().count(), 1)

        library1 = Library.objects.get(pk=self.library1.pk)
        self.assertEquals(library1.name, 'UPDATED')
        self.assertEquals(
            Library.objects.filter(pk=self.library2.pk).count(), 0)

        # Check resulting response
        with self.login(self.user):
            self.assertRedirects(
                response, reverse('flowcell_view',
                                kwargs={'pk': self.flow_cell.pk}))

    def test_prefill_form_first(self):
        """Test that prefilling the form with barcode1 works correctly"""
        with self.login(self.user):
            response = self.client.get(
                reverse('flowcell_updatelibraries',
                        kwargs={'pk': self.flow_cell.pk}),
                {'barcode1': self.barcode_set.pk})

        for form in response.context['formset'].forms[2:]:
            self.assertEquals(form.initial['barcode_set'], self.barcode_set)
            self.assertEquals(form.initial['barcode_set2'], None)

    def test_prefill_form_second(self):
        """Test that prefilling the form with barcode2 works correctly"""
        with self.login(self.user):
            response = self.client.get(
                reverse('flowcell_updatelibraries',
                        kwargs={'pk': self.flow_cell.pk}),
                {'barcode2': self.barcode_set.pk})

        for form in response.context['formset'].forms[2:]:
            self.assertEquals(form.initial['barcode_set'], None)
            self.assertEquals(form.initial['barcode_set2'], self.barcode_set)

    def test_prefill_form_both(self):
        """Test that prefilling the form with barcode1+2 works correctly"""
        with self.login(self.user):
            response = self.client.get(
                reverse('flowcell_updatelibraries',
                        kwargs={'pk': self.flow_cell.pk}),
                {'barcode1': self.barcode_set.pk,
                 'barcode2': self.barcode_set.pk})

        for form in response.context['formset'].forms[2:]:
            self.assertEquals(form.initial['barcode_set'], self.barcode_set)
            self.assertEquals(form.initial['barcode_set2'], self.barcode_set)


# SequencingMachine related ---------------------------------------------------


class TestSequencingMachineListView(
        SuperUserTestCase, SequencingMachineMixin):

    def setUp(self):
        self.user = self.make_user()
        self.machine = self._make_machine()
        self.client = Client()

    def test_render(self):
        """Simply test that rendering the list view works"""
        with self.login(self.user):
            response = self.client.get(reverse('instrument_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 1)


class TestSequencingMachineCreateView(SuperUserTestCase):

    def setUp(self):
        self.user = self.make_user()

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
        with self.login(self.user):
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
        with self.login(self.user):
            self.assertRedirects(
                response, reverse('instrument_view', kwargs={'pk': instrument.pk}))


class TestSequencingMachineDetailView(
        SuperUserTestCase, SequencingMachineMixin):

    def setUp(self):
        self.user = self.make_user()
        self.machine = self._make_machine()
        self.client = Client()

    def test_render(self):
        """Simply test that rendering the detail view works"""
        # Simulate the GET
        with self.login(self.user):
            response = self.client.get(
                reverse('instrument_view', kwargs={'pk': self.machine.pk}))

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object'].pk,
                         self.machine.pk)


class TestSequencingMachineUpdateView(
        SuperUserTestCase, SequencingMachineMixin):

    def setUp(self):
        self.user = self.make_user()
        self.machine = self._make_machine()
        self.client = Client()

    def test_render(self):
        """Test that the instrument update POST works"""
        # Check precondition
        self.assertEqual(SequencingMachine.objects.all().count(), 1)

        # Simulate POST request
        values = model_to_dict(self.machine)
        values['vendor_id'] = values['vendor_id'] + 'YADAYADAYADA'
        values['machine_model'] = models.MACHINE_MODEL_HISEQ1000

        # Simulate the POST
        with self.login(self.user):
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
        with self.login(self.user):
            self.assertRedirects(
                response, reverse('instrument_view', kwargs={'pk': machine.pk}))


class TestSequencingMachineDeleteView(
        SuperUserTestCase, SequencingMachineMixin):

    def setUp(self):
        self.user = self.make_user()
        self.machine = self._make_machine()
        self.client = Client()

    def test_render(self):
        """Test that the instrument delete POST works"""
        # Check precondition
        self.assertEqual(SequencingMachine.objects.all().count(), 1)

        # Simulate the POST
        with self.login(self.user):
            response = self.client.post(
                reverse('instrument_delete', kwargs={'pk': self.machine.pk}))

        # Check resulting database state
        self.assertEqual(SequencingMachine.objects.all().count(), 0)

        # Check resulting response
        with self.login(self.user):
            self.assertRedirects(
                response, reverse('instrument_list'))


class TestFlowCellSetExportView(
        SuperUserTestCase, LibraryMixin, SequencingMachineMixin, FlowCellMixin,
        BarcodeSetEntryMixin, BarcodeSetMixin):

    def setUp(self):
        self.user = self.make_user()
        self.machine = self._make_machine()
        self.barcode_set = self._make_barcode_set()
        self.barcode = self._make_barcode_set_entry(self.barcode_set)
        self.barcode2 = self._make_barcode_set_entry(
            self.barcode_set, 'AR02', 'CGATATA')
        self.flow_cell_name = '160303_{}_0815_A_BCDEFGHIXX_LABEL'.format(
            self.machine.vendor_id)
        self.flow_cell = self._make_flow_cell(
            self.user, self.flow_cell_name, 8,
            models.FLOWCELL_STATUS_SEQ_COMPLETE, 'John Doe',
            True, 1, models.RTA_VERSION_V2, 151, 'Description')
        self.library = self._make_library(
            self.flow_cell, 'LIB_001', models.REFERENCE_HUMAN,
            self.barcode_set, self.barcode, [1, 2],
            self.barcode_set, self.barcode2)

    def test_render(self):
        # Simulate the GET
        with self.login(self.user):
            response = self.client.get(
                reverse('flowcell_export',
                        kwargs={'pk': self.flow_cell.pk}))

        # Check response
        self.assertEqual(response.status_code, 200)
        EXPECTED = textwrap.dedent(r"""
            {
              "name": "160303_NS5001234_0815_A_BCDEFGHIXX_LABEL",
              "description": "Description",
              "num_lanes": 8,
              "status": "seq_complete",
              "operator": "John Doe",
              "is_paired": true,
              "index_read_count": 1,
              "rta_version": 2,
              "read_length": 151,
              "libraries": [
                {
                  "name": "LIB_001",
                  "reference": "hg19",
                  "barcode_set": "SureSelectTest",
                  "barcode_name": "AR01",
                  "barcode_sequence": "ACGTGTTA",
                  "barcode_set2": "SureSelectTest",
                  "barcode_name2": "AR02",
                  "barcode_sequence2": "CGATATA",
                  "lane_numbers": [
                    1,
                    2
                  ]
                }
              ]
            }
            """).lstrip()
        self.assertEqual(response.content.decode('utf-8'), EXPECTED)


class TestFlowCellImportView(
        SuperUserTestCase, SequencingMachineMixin,
        BarcodeSetEntryMixin, BarcodeSetMixin):

    def setUp(self):
        self.user = self.make_user()
        self.client = Client()
        self.machine = self._make_machine()
        self.barcode_set = self._make_barcode_set()
        self.barcode = self._make_barcode_set_entry(self.barcode_set)
        self.barcode2 = self._make_barcode_set_entry(
            self.barcode_set, 'AR02', 'CGATATA')

    def test_render(self):
        # Prepare payload to post
        payload = io.StringIO(textwrap.dedent(r"""
            {
              "name": "160303_NS5001234_0815_A_BCDEFGHIXX_LABEL",
              "description": "Description",
              "num_lanes": 8,
              "status": "seq_complete",
              "operator": "John Doe",
              "is_paired": true,
              "index_read_count": 1,
              "rta_version": 2,
              "read_length": 151,
              "libraries": [
                {
                  "name": "LIB_001",
                  "reference": "hg19",
                  "barcode_set": "SureSelectTest",
                  "barcode_name": "AR01",
                  "barcode_sequence": "ACGTGTTA",
                  "barcode_set2": "SureSelectTest",
                  "barcode_name2": "AR02",
                  "barcode_sequence2": "CGATATA",
                  "lane_numbers": [
                    1,
                    2
                  ]
                }
              ]
            }
            """).lstrip())

        # Check precondition
        self.assertEqual(FlowCell.objects.all().count(), 0)
        self.assertEqual(Library.objects.all().count(), 0)

        # Simulate the POST
        with self.login(self.user):
            response = self.client.post(
                reverse('flowcell_import'),
                {'json_file': payload})

        # Check response
        flowcell = FlowCell.objects.order_by('-created_at')[0]
        with self.login(self.user):
            self.assertRedirects(
                response, reverse('flowcell_view',
                                kwargs={'pk': flowcell.pk}))

        # Check database state afterwards
        self.assertEqual(FlowCell.objects.all().count(), 1)
        self.assertEqual(Library.objects.all().count(), 1)


# BarcodeSet related ----------------------------------------------------------


class TestBarcodeSetListView(
        SuperUserTestCase, BarcodeSetMixin, BarcodeSetEntryMixin):

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
        with self.login(self.user):
            response = self.client.get(reverse('barcodeset_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 1)


class TestBarcodeSetCreateView(SuperUserTestCase):

    def setUp(self):
        self.user = self.make_user()

    def test_render(self):
        """Simply test that post inserts a new flow cell and redirects to the
        list view
        """
        # Check precondition
        self.assertEqual(BarcodeSet.objects.all().count(), 0)

        # Simulate POST request
        values = {
            'name': 'some_barcodes',
            'short_name': 'SBS',
            'description': 'Some barcode set',
        }

        # Simulate the POST
        with self.login(self.user):
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
        with self.login(self.user):
            self.assertRedirects(
                response, reverse('barcodeset_view',
                                kwargs={'pk': barcode_set.pk}))


class TestBarcodeSetDetailView(
        SuperUserTestCase, BarcodeSetMixin, BarcodeSetEntryMixin):

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
        with self.login(self.user):
            response = self.client.get(
                reverse('barcodeset_view',
                        kwargs={'pk': self.barcode_set.pk}))

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object'].pk,
                         self.barcode_set.pk)


class TestBarcodeSetUpdateView(
        SuperUserTestCase, BarcodeSetMixin, BarcodeSetEntryMixin):

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
        self.assertEqual(BarcodeSet.objects.all().count(), 1)

        # Simulate POST request
        values = model_to_dict(self.barcode_set)
        values['name'] = 'Another name'
        values['description'] = 'This is the description'

        # Simulate the POST
        with self.login(self.user):
            response = self.client.post(
                reverse('barcodeset_update',
                        kwargs={'pk': self.barcode_set.pk}),
                values)

        # Check resulting database state
        self.assertEqual(BarcodeSet.objects.all().count(), 1)
        barcode_set = BarcodeSet.objects.get(pk=self.barcode_set.pk)
        EXPECTED = {
            'id': barcode_set.pk,
            'name': values['name'],
            'short_name': self.barcode_set.short_name,
            'description': values['description'],
        }
        self.assertEqual(model_to_dict(barcode_set), EXPECTED)

        # Check resulting response
        with self.login(self.user):
            self.assertRedirects(
                response, reverse('barcodeset_view',
                                kwargs={'pk': barcode_set.pk}))


class TestBarcodeSetDeleteView(
        SuperUserTestCase, BarcodeSetMixin, BarcodeSetEntryMixin):

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
        self.assertEqual(BarcodeSet.objects.all().count(), 1)
        self.assertEqual(BarcodeSetEntry.objects.all().count(), 2)

        # Simulate the POST
        with self.login(self.user):
            response = self.client.post(
                reverse('barcodeset_delete',
                        kwargs={'pk': self.barcode_set.pk}))

        # Check resulting database state
        self.assertEqual(BarcodeSet.objects.all().count(), 0)
        self.assertEqual(BarcodeSetEntry.objects.all().count(), 0)

        # Check resulting response
        with self.login(self.user):
            self.assertRedirects(
                response, reverse('barcodeset_list'))


class TestBarcodeSetUpdateEntriesView(
        SuperUserTestCase, BarcodeSetMixin, BarcodeSetEntryMixin):

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
        self.assertEqual(BarcodeSet.objects.all().count(), 1)
        self.assertEqual(BarcodeSetEntry.objects.all().count(), 2)

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
        with self.login(self.user):
            response = self.client.post(
                reverse('barcodeset_updateentries',
                        kwargs={'pk': self.barcode_set.pk}),
                values)

        # Check resulting database state
        self.assertEqual(BarcodeSet.objects.all().count(), 1)
        self.assertEqual(BarcodeSetEntry.objects.all().count(), 2)

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
        with self.login(self.user):
            self.assertRedirects(
                response, reverse('barcodeset_view',
                                kwargs={'pk': self.barcode_set.pk}))

    def test_update_more(self):
        """Test that updating barcode set entries works correctly"""
        response = self._test_update({'submit_more': 'submit_more'})
        # Check resulting response
        with self.login(self.user):
            self.assertRedirects(
                response, reverse('barcodeset_updateentries',
                                kwargs={'pk': self.barcode_set.pk}))

    def test_add(self):
        """Test that adding barcode set entries works correctly"""
        # Check precondition
        self.assertEqual(BarcodeSet.objects.all().count(), 1)
        self.assertEqual(BarcodeSetEntry.objects.all().count(), 2)

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
        with self.login(self.user):
            response = self.client.post(
                reverse('barcodeset_updateentries',
                        kwargs={'pk': self.barcode_set.pk}),
                values)

        # Check resulting database state
        self.assertEqual(BarcodeSet.objects.all().count(), 1)
        self.assertEqual(BarcodeSetEntry.objects.all().count(), 3)

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
        with self.login(self.user):
            self.assertRedirects(
                response, reverse('barcodeset_view',
                                kwargs={'pk': self.barcode_set.pk}))

    def test_delete(self):
        """Test that deleting barcode set entries works correctly"""
        # Check precondition
        self.assertEqual(BarcodeSet.objects.all().count(), 1)
        self.assertEqual(BarcodeSetEntry.objects.all().count(), 2)

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
        with self.login(self.user):
            response = self.client.post(
                reverse('barcodeset_updateentries',
                        kwargs={'pk': self.barcode_set.pk}),
                values)

        # Check resulting database state
        self.assertEqual(BarcodeSet.objects.all().count(), 1)
        self.assertEqual(BarcodeSetEntry.objects.all().count(), 1)

        barcode1 = BarcodeSetEntry.objects.get(pk=self.barcode1.pk)
        self.assertEquals(barcode1.name, 'UPDATED')
        self.assertEquals(barcode1.sequence, 'GATTACA')
        self.assertEquals(
            BarcodeSetEntry.objects.filter(pk=self.barcode2.pk).count(), 0)

        # Check resulting response
        with self.login(self.user):
            self.assertRedirects(
                response, reverse('barcodeset_view',
                                kwargs={'pk': self.barcode_set.pk}))


class TestBarcodeSetExportView(
        SuperUserTestCase, BarcodeSetMixin, BarcodeSetEntryMixin):

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
        with self.login(self.user):
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


class TestBarcodeSetImportView(SuperUserTestCase):

    def setUp(self):
        self.user = self.make_user()
        self.client = Client()

    def test_render(self):
        """Simply test that rendering the detail view works"""
        # Prepare payload to post
        payload = io.StringIO(textwrap.dedent(r"""
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
            """).lstrip())

        # Check precondition
        self.assertEqual(BarcodeSet.objects.all().count(), 0)
        self.assertEqual(BarcodeSetEntry.objects.all().count(), 0)

        # Simulate the POST
        with self.login(self.user):
            response = self.client.post(
                reverse('barcodeset_import'),
                {'json_file': payload})

        # Check response
        barcodeset = BarcodeSet.objects.order_by('-created_at')[0]
        with self.login(self.user):
            self.assertRedirects(
                response, reverse('barcodeset_view',
                                kwargs={'pk': barcodeset.pk}))

        # Check database state afterwards
        self.assertEqual(BarcodeSet.objects.all().count(), 1)
        self.assertEqual(BarcodeSetEntry.objects.all().count(), 2)


class TestSearchView(
    SuperUserTestCase, FlowCellMixin, SequencingMachineMixin, LibraryMixin,
    BarcodeSetMixin, BarcodeSetEntryMixin):

    def setUp(self):
        self.user = self.make_user()
        self.client = Client()
        # Create Machine
        self.machine = self._make_machine()
        # Create Barcode set
        self.barcode_set = self._make_barcode_set()
        self.barcode1 = self._make_barcode_set_entry(
            self.barcode_set, 'AR01', 'CGATCGAT')
        self.barcode2 = self._make_barcode_set_entry(
            self.barcode_set, 'AR02', 'ATTATATA')
        # Create Flow cell
        self.flow_cell_name = '160303_{}_0815_A_BCDEFGHIXX_LABEL'.format(
            self.machine.vendor_id)
        self.flow_cell = self._make_flow_cell(
            self.user, self.flow_cell_name, 8,
            models.FLOWCELL_STATUS_SEQ_COMPLETE, 'John Doe',
            True, 1, models.RTA_VERSION_V2, 151, 'Description')
        self.library1 = self._make_library(
            self.flow_cell, 'LIB_001', models.REFERENCE_HUMAN,
            self.barcode_set, self.barcode1, [1, 2], None, None)
        self.library2 = self._make_library(
            self.flow_cell, 'LIB_002', models.REFERENCE_HUMAN,
            self.barcode_set, self.barcode2, [1, 2], None, None)

    def test_with_result_of_two(self):
        with self.login(self.user):
            response = self.client.get(reverse('search'), {'q': 'LIB_00'})
        self.assertEqual(len(response.context['results']), 2)

    def test_with_result_of_one(self):
        with self.login(self.user):
            response = self.client.get(reverse('search'), {'q': '001'})
        self.assertEqual(len(response.context['results']), 1)
        self.assertEqual(response.context['results'][0].name, 'LIB_001')

    def test_without_result(self):
        with self.login(self.user):
            response = self.client.get(reverse('search'), {'q': '003'})
        self.assertEqual(len(response.context['results']), 0)


# Message Related -------------------------------------------------------------


class TestMessageCreateView(
    SuperUserTestCase, FlowCellMixin, SequencingMachineMixin, LibraryMixin,
    BarcodeSetMixin, BarcodeSetEntryMixin):

    def setUp(self):
        self.user = self.make_user()
        self.client = Client()
        # Create Machine
        self.machine = self._make_machine()
        # Create Barcode set
        self.barcode_set = self._make_barcode_set()
        self.barcode1 = self._make_barcode_set_entry(
            self.barcode_set, 'AR01', 'CGATCGAT')
        self.barcode2 = self._make_barcode_set_entry(
            self.barcode_set, 'AR02', 'ATTATATA')
        # Create Flow cell
        self.flow_cell_name = '160303_{}_0815_A_BCDEFGHIXX_LABEL'.format(
            self.machine.vendor_id)
        self.flow_cell = self._make_flow_cell(
            self.user, self.flow_cell_name, 8,
            models.FLOWCELL_STATUS_SEQ_COMPLETE, 'John Doe',
            True, 1, models.RTA_VERSION_V2, 151, 'Description')
        self.library1 = self._make_library(
            self.flow_cell, 'LIB_001', models.REFERENCE_HUMAN,
            self.barcode_set, self.barcode1, [1, 2], None, None)
        self.library2 = self._make_library(
            self.flow_cell, 'LIB_002', models.REFERENCE_HUMAN,
            self.barcode_set, self.barcode2, [1, 2], None, None)

    def test_get(self):
        with self.login(self.user):
            response = self.client.get(reverse(
                'flowcell_add_message',
                kwargs={'related_pk': self.flow_cell.pk}))
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        payload = io.StringIO(textwrap.dedent(r"""
            Example File Content
            """).lstrip())

        # Simulate POST request
        values = {
            'title': 'Message Title',
            'body': 'Message Body',
            'attachments': [payload],
        }

        self.assertEquals(
            threads_models.Message.objects.all().count(), 0)
        self.assertEquals(
            threads_models.Attachment.objects.all().count(), 0)
        self.assertEquals(
            threads_models.AttachmentFile.objects.all().count(), 0)

        # Simulate the POST
        with self.login(self.user):
            response = self.client.post(
                reverse('flowcell_add_message',
                        kwargs={'related_pk': self.flow_cell.pk}),
                values)
            self.assertRedirects(
                response, reverse(
                    'flowcell_view', kwargs={'pk': self.flow_cell.pk}))

        self.assertEquals(
            threads_models.Message.objects.all().count(), 1)
        self.assertEquals(
            threads_models.AttachmentFile.objects.all().count(), 1)
        self.assertEquals(
            threads_models.AttachmentFile.objects.all().count(), 1)

        EXPECTED = {
            'object_id': self.flow_cell.pk,
            'title': values['title'],
            'body': values['body'],
            'author': self.user,
            'mime_type': 'text/plain',
        }
        msg = threads_models.Message.objects.all()[0]
        for key, value in EXPECTED.items():
            self.assertEquals(getattr(msg, key), value)

        att = threads_models.Attachment.objects.all()[0]
        self.assertEquals(att.message_id, msg.pk)

        att_file = threads_models.AttachmentFile.objects.all()[0]
        self.assertEquals(att_file.bytes, 'RXhhbXBsZSBGaWxlIENvbnRlbnQK')


class MessageMixin:

    @classmethod
    def _make_message(cls, user, flow_cell, title, body):
        msg = threads_models.Message.objects.create(
            author=user,
            content_type=ContentType.objects.get_for_model(flow_cell),
            object_id=flow_cell.pk,
            title=title,
            body=body)
        return msg


class TestMessageDeleteView(
    SuperUserTestCase, FlowCellMixin, SequencingMachineMixin, LibraryMixin,
    BarcodeSetMixin, BarcodeSetEntryMixin, MessageMixin):

    def setUp(self):
        self.user = self.make_user()
        self.client = Client()
        # Create Machine
        self.machine = self._make_machine()
        # Create Barcode set
        self.barcode_set = self._make_barcode_set()
        self.barcode1 = self._make_barcode_set_entry(
            self.barcode_set, 'AR01', 'CGATCGAT')
        self.barcode2 = self._make_barcode_set_entry(
            self.barcode_set, 'AR02', 'ATTATATA')
        # Create Flow cell
        self.flow_cell_name = '160303_{}_0815_A_BCDEFGHIXX_LABEL'.format(
            self.machine.vendor_id)
        self.flow_cell = self._make_flow_cell(
            self.user, self.flow_cell_name, 8,
            models.FLOWCELL_STATUS_SEQ_COMPLETE, 'John Doe',
            True, 1, models.RTA_VERSION_V2, 151, 'Description')
        self.library1 = self._make_library(
            self.flow_cell, 'LIB_001', models.REFERENCE_HUMAN,
            self.barcode_set, self.barcode1, [1, 2], None, None)
        self.library2 = self._make_library(
            self.flow_cell, 'LIB_002', models.REFERENCE_HUMAN,
            self.barcode_set, self.barcode2, [1, 2], None, None)
        # Create Message
        self.message = self._make_message(
            self.user, self.flow_cell, 'Some Title', 'Some Body')

    def test_get(self):
        with self.login(self.user):
            response = self.client.get(reverse(
                'flowcell_delete_message',
                kwargs={'pk': self.message.pk}))
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.assertEquals(threads_models.Message.objects.all().count(), 1)

        with self.login(self.user):
            response = self.client.post(reverse(
                'flowcell_delete_message',
                kwargs={'pk': self.message.pk}))
            self.assertRedirects(
                response,
                reverse('flowcell_view', kwargs={'pk': self.flow_cell.pk}))

        self.assertEquals(threads_models.Message.objects.all().count(), 0)



class TestMessageUpdateView(
    SuperUserTestCase, FlowCellMixin, SequencingMachineMixin, LibraryMixin,
    BarcodeSetMixin, BarcodeSetEntryMixin, MessageMixin):

    def setUp(self):
        self.user = self.make_user()
        self.client = Client()
        # Create Machine
        self.machine = self._make_machine()
        # Create Barcode set
        self.barcode_set = self._make_barcode_set()
        self.barcode1 = self._make_barcode_set_entry(
            self.barcode_set, 'AR01', 'CGATCGAT')
        self.barcode2 = self._make_barcode_set_entry(
            self.barcode_set, 'AR02', 'ATTATATA')
        # Create Flow cell
        self.flow_cell_name = '160303_{}_0815_A_BCDEFGHIXX_LABEL'.format(
            self.machine.vendor_id)
        self.flow_cell = self._make_flow_cell(
            self.user, self.flow_cell_name, 8,
            models.FLOWCELL_STATUS_SEQ_COMPLETE, 'John Doe',
            True, 1, models.RTA_VERSION_V2, 151, 'Description')
        self.library1 = self._make_library(
            self.flow_cell, 'LIB_001', models.REFERENCE_HUMAN,
            self.barcode_set, self.barcode1, [1, 2], None, None)
        self.library2 = self._make_library(
            self.flow_cell, 'LIB_002', models.REFERENCE_HUMAN,
            self.barcode_set, self.barcode2, [1, 2], None, None)
        # Create Message
        self.message = self._make_message(
            self.user, self.flow_cell, 'Some Title', 'Some Body')

    def test_get(self):
        with self.login(self.user):
            response = self.client.get(reverse(
                'flowcell_update_message',
                kwargs={'pk': self.message.pk}))

        self.assertEqual(response.context['object'], self.message)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.assertEquals(threads_models.Message.objects.all().count(), 1)

        values = {
            'title': 'Updated Title',
            'body': 'Updated Body',
        }

        with self.login(self.user):
            response = self.client.post(reverse(
                'flowcell_update_message',
                kwargs={'pk': self.message.pk}),
                values)
            self.assertRedirects(
                response,
                reverse('flowcell_view', kwargs={'pk': self.flow_cell.pk}))

        self.assertEquals(threads_models.Message.objects.all().count(), 1)
        message = threads_models.Message.objects.all()[0]
        self.assertEquals(message.title, 'Updated Title')
        self.assertEquals(message.body, 'Updated Body')
