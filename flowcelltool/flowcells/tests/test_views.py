# -*- coding: utf-8 -*-
"""Tests for the views from the flowcelltools Django app
"""

from test_plus.test import TestCase

from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.test import Client

from .. import views
from .. import models
from ..models import SequencingMachine, FlowCell

from .test_models import SequencingMachineMixin, FlowCellMixin


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
        response = self.client.get('/flowcells/')
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
        response = self.client.post('/flowcells/create', values)

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

        # Simulate the POST
        response = self.client.post(
            reverse('flowcell_update', kwargs={'pk': self.flow_cell.pk}))

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
