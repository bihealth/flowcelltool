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

    # FlowCell related --------------------------------------------------------
    url(
        regex=r'^$',
        view=views.FlowCellListView.as_view(),
        name='flowcell_list',
    ),
    url(
        regex=r'^create$',
        view=views.FlowCellCreateView.as_view(),
        name='flowcell_create',
    ),
    url(
        regex=r'^view/(?P<pk>\d+)$',
        view=views.FlowCellDetailView.as_view(),
        name='flowcell_view',
    ),
    url(
        regex=r'^update/(?P<pk>\d+)$',
        view=views.FlowCellUpdateView.as_view(),
        name='flowcell_update',
    ),
]
