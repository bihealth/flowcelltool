# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    # SequencingMachine related -----------------------------------------------
    url(
        regex=r'^instrument/list$',
        view=views.SequencingMachineListView.as_view(),
        name='instrument_list',
    ),
    url(
        regex=r'^instrument/create$',
        view=views.SequencingMachineCreateView.as_view(),
        name='instrument_create',
    ),
    url(
        regex=r'^instrument/view/(?P<pk>\d+)$',
        view=views.SequencingMachineDetailView.as_view(),
        name='instrument_view',
    ),
    url(
        regex=r'^instrument/update/(?P<pk>\d+)$',
        view=views.SequencingMachineUpdateView.as_view(),
        name='instrument_update',
    ),
    url(
        regex=r'^instrument/delete/(?P<pk>\d+)$',
        view=views.SequencingMachineDeleteView.as_view(),
        name='instrument_delete',
    ),

    # BarcodeSet related ------------------------------------------------------
    url(
        regex=r'^barcodeset/list$',
        view=views.BarcodeSetListView.as_view(),
        name='barcodeset_list',
    ),
    url(
        regex=r'^barcodeset/create$',
        view=views.BarcodeSetCreateView.as_view(),
        name='barcodeset_create',
    ),
    url(
        regex=r'^barcodeset/view/(?P<pk>\d+)$',
        view=views.BarcodeSetDetailView.as_view(),
        name='barcodeset_view',
    ),
    url(
        regex=r'^barcodeset/update/(?P<pk>\d+)$',
        view=views.BarcodeSetUpdateView.as_view(),
        name='barcodeset_update',
    ),
    url(
        regex=r'^barcodeset/updateentries/(?P<pk>\d+)$',
        view=views.BarcodeSetEntryUpdateView.as_view(),
        name='barcodeset_updateentries',
    ),
    url(
        regex=r'^barcodeset/delete/(?P<pk>\d+)$',
        view=views.BarcodeSetDeleteView.as_view(),
        name='barcodeset_delete',
    ),
    url(
        regex=r'^barcodeset/import$',
        view=views.BarcodeSetImportView.as_view(),
        name='barcodeset_import',
    ),
    url(
        regex=r'^barcodeset/export/(?P<pk>\d+)$',
        view=views.BarcodeSetExportView.as_view(),
        name='barcodeset_export',
    ),

    # FlowCell related --------------------------------------------------------
    url(
        regex=r'^flowcell/list$',
        view=views.FlowCellListView.as_view(),
        name='flowcell_list',
    ),
    url(
        regex=r'^flowcell/create$',
        view=views.FlowCellCreateView.as_view(),
        name='flowcell_create',
    ),
    url(
        regex=r'^flowcell/view/(?P<pk>\d+)$',
        view=views.FlowCellDetailView.as_view(),
        name='flowcell_view',
    ),
    url(
        regex=r'^flowcell/update/(?P<pk>\d+)$',
        view=views.FlowCellUpdateView.as_view(),
        name='flowcell_update',
    ),
    url(
        regex=r'^flowcell/delete/(?P<pk>\d+)$',
        view=views.FlowCellDeleteView.as_view(),
        name='flowcell_delete',
    ),
]
