# -*- coding: utf-8 -*-
"""Tests for the views from the flowcelltools Django app
"""

from test_plus.test import TestCase

from django.core.urlresolvers import reverse
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
