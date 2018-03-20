# -*- coding: utf-8 -*-
from django.conf.urls import include, url

from . import views

urlpatterns = [
    # API ---------------------------------------------------------------------

    # Mount API as "/v0" to stress that it's experimental and unstable
    url(r'api/v0/', include('flowcelltool.flowcells.api_v1.urls')),

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
        regex=r'^instrument/view/(?P<uuid>\S+)/$',
        view=views.SequencingMachineDetailView.as_view(),
        name='instrument_view',
    ),
    url(
        regex=r'^instrument/update/(?P<uuid>\S+)/$',
        view=views.SequencingMachineUpdateView.as_view(),
        name='instrument_update',
    ),
    url(
        regex=r'^instrument/delete/(?P<uuid>\S+)/$',
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
        regex=r'^barcodeset/view/(?P<uuid>\S+)/$',
        view=views.BarcodeSetDetailView.as_view(),
        name='barcodeset_view',
    ),
    url(
        regex=r'^barcodeset/update/(?P<uuid>\S+)/$',
        view=views.BarcodeSetUpdateView.as_view(),
        name='barcodeset_update',
    ),
    url(
        regex=r'^barcodeset/updateentries/(?P<uuid>\S+)/$',
        view=views.BarcodeSetEntryUpdateView.as_view(),
        name='barcodeset_updateentries',
    ),
    url(
        regex=r'^barcodeset/delete/(?P<uuid>\S+)/$',
        view=views.BarcodeSetDeleteView.as_view(),
        name='barcodeset_delete',
    ),
    url(
        regex=r'^barcodeset/import$',
        view=views.BarcodeSetImportView.as_view(),
        name='barcodeset_import',
    ),
    url(
        regex=r'^barcodeset/export/(?P<uuid>\S+)/$',
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
        regex=r'^flowcell/view/(?P<uuid>\S+)/$',
        view=views.FlowCellDetailView.as_view(),
        name='flowcell_view',
    ),
    url(
        regex=r'^flowcell/update/(?P<uuid>\S+)/$',
        view=views.FlowCellUpdateView.as_view(),
        name='flowcell_update',
    ),
    url(
        regex=r'^flowcell/updatelibraries/(?P<uuid>\S+)/$',
        view=views.LibraryUpdateView.as_view(),
        name='flowcell_updatelibraries',
    ),
    url(
        regex=r'^flowcell/delete/(?P<uuid>\S+)/$',
        view=views.FlowCellDeleteView.as_view(),
        name='flowcell_delete',
    ),
    url(
        regex=r'^flowcell/export/(?P<uuid>\S+)/$',
        view=views.FlowCellExportView.as_view(),
        name='flowcell_export',
    ),
    url(
        regex=r'^flowcell/import$',
        view=views.FlowCellImportView.as_view(),
        name='flowcell_import',
    ),
    url(
        regex=r'^flowcell/sheet/(?P<uuid>\S+)/$',
        view=views.FlowCellSampleSheetView.as_view(),
        name='flowcell_sheet',
    ),
    url(
        regex=r'^flowcell/extract/(?P<uuid>\S+)/$',
        view=views.FlowCellExtractLibrariesView.as_view(
            views.FlowCellExtractLibrariesView.FORMS),
        name='flowcell_extract',
    ),

    # FlowCell-Message related ------------------------------------------------
    url(
        regex=r'^flowcell/add_message/(?P<related_uuid>\S+)/$',
        view=views.FlowCellAddMessageView.as_view(),
        name='flowcell_add_message',
    ),
    url(
        regex=r'^flowcell/update_message/(?P<uuid>\S+)/$',
        view=views.FlowCellUpdateMessageView.as_view(),
        name='flowcell_update_message',
    ),
    url(
        regex=r'^flowcell/delete_message/(?P<uuid>\S+)/$',
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
