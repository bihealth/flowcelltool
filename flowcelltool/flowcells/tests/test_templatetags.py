# -*- coding: utf-8 -*-
"""Tests for template tags
"""

from test_plus.test import TestCase

from ..templatetags import flowcells_tags


class TestSizify(TestCase):

    def test_kb(self):
        self.assertEquals(
            flowcells_tags.sizify(100), '0.1 kb')
        self.assertEquals(
            flowcells_tags.sizify(512000 - 1), '500.0 kb')

    def test_mb(self):
        self.assertEquals(
            flowcells_tags.sizify(512000), '0.49 mb')
        self.assertEquals(
            flowcells_tags.sizify(4194304000 - 1), '4000.0 mb')

    def test_gb(self):
        self.assertEquals(
            flowcells_tags.sizify(4194304000), '3.91 gb')
        self.assertEquals(
            flowcells_tags.sizify(1000 * 1000 * 1000 * 1000), '931.32 gb')


class TestFAMimeType(TestCase):

    def test_pdf(self):
        self.assertEquals(
            flowcells_tags.fa_mime_type('application/pdf'), 'file-pdf-o')

    def test_xls(self):
        self.assertEquals(flowcells_tags.fa_mime_type(
            'application/vnd.openxmlformats-officedocument.'
            'spreadsheetml.sheet'),
            'file-excel-o')

    def test_html(self):
        self.assertEquals(
            flowcells_tags.fa_mime_type('text/html'), 'file-text-o')

    def test_other(self):
        self.assertEquals(
            flowcells_tags.fa_mime_type(''), 'file-o')
