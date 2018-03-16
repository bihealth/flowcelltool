# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views
from .api_v1 import views as api_v1_views


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
        regex=r'^flowcell/updatelibraries/(?P<pk>\d+)$',
        view=views.LibraryUpdateView.as_view(),
        name='flowcell_updatelibraries',
    ),
    url(
        regex=r'^flowcell/delete/(?P<pk>\d+)$',
        view=views.FlowCellDeleteView.as_view(),
        name='flowcell_delete',
    ),
    url(
        regex=r'^flowcell/export/(?P<pk>\d+)$',
        view=views.FlowCellExportView.as_view(),
        name='flowcell_export',
    ),
    url(
        regex=r'^flowcell/import$',
        view=views.FlowCellImportView.as_view(),
        name='flowcell_import',
    ),
    url(
        regex=r'^flowcell/sheet/(?P<pk>\d+)$',
        view=views.FlowCellSampleSheetView.as_view(),
        name='flowcell_sheet',
    ),
    url(
        regex=r'^flowcell/extract/(?P<pk>\d+)$',
        view=views.FlowCellExtractLibrariesView.as_view(
            views.FlowCellExtractLibrariesView.FORMS),
        name='flowcell_extract',
    ),

    # FlowCell-Message related ------------------------------------------------
    url(
        regex=r'^flowcell/add_message/(?P<related_pk>\d+)$',
        view=views.FlowCellAddMessageView.as_view(),
        name='flowcell_add_message',
    ),
    url(
        regex=r'^flowcell/update_message/(?P<pk>\d+)$',
        view=views.FlowCellUpdateMessageView.as_view(),
        name='flowcell_update_message',
    ),
    url(
        regex=r'^flowcell/delete_message/(?P<pk>\d+)$',
        view=views.FlowCellDeleteMessageView.as_view(),
        name='flowcell_delete_message',
    ),

    # Cross-Data Type Query ---------------------------------------------------
    url(
        regex=r'^search$',
        view=views.SearchView.as_view(),
        name='search',
    ),
]

# API
urlpatterns += [
    # SequencingMachine related -----------------------------------------------

    url(
        regex=r'api/v1/instrument/list$',
        view=api_v1_views.SequencingMachineListApiView.as_view(),
        name='instrument_list_api',
    ),
    url(
        regex=r'api/v1/instrument/view/(?P<pk>\d+)$',
        view=api_v1_views.SequencingMachineDetailApiView.as_view(),
        name='instrument_view_api',
    ),
    url(
        regex=r'api/v1/instrument/by_vendor_id/(?P<vendor_id>.+)$',
        view=api_v1_views.SequencingMachineByVendorIdApiView.as_view(),
        name='instrument_by_vendor_id_api',
    ),

    # BarcodeSet related ------------------------------------------------------

    url(
        regex=r'api/v1/barcodeset/list$',
        view=api_v1_views.BarcodeSetListApiView.as_view(),
        name='barcodeset_list_api',
    ),
    url(
        regex=r'api/v1/barcodeset/view/(?P<pk>\d+)$',
        view=api_v1_views.BarcodeSetDetailApiView.as_view(),
        name='barcodeset_view_api',
    ),

    # FlowCell related --------------------------------------------------------

    url(
        regex=r'api/v1/flowcell/list$',
        view=api_v1_views.FlowCellListApiView.as_view(),
        name='flowcell_list_api',
    ),
    url(
        regex=r'api/v1/flowcell/view/(?P<pk>\d+)$',
        view=api_v1_views.FlowCellDetailApiView.as_view(),
        name='flowcell_view_api',
    ),
    url(
        regex=r'api/v1/flowcell/by_vendor_id/(?P<vendor_id>.+)$',
        view=api_v1_views.FlowCellByVendorIdApiView.as_view(),
        name='flowcell_by_vendor_id_api',
    ),
    url(
        regex=r'api/v1/flowcell/sample_sheet/(?P<pk>\d+)$',
        view=api_v1_views.FlowCellSampleSheetApiView.as_view(),
        name='flowcell_sample_sheet_api',
    ),

    # Message related ----------------------------------------------------------

    url(
        regex=r'api/v1/flowcell/list_messages/(?P<related_pk>\d+)$',
        view=api_v1_views.MessageListApiView.as_view(),
        name='flowcell_list_messages_api',
    ),

    # /flowcells/api/v1/flowcell/add_message/:related_pk
    # TODO
]
