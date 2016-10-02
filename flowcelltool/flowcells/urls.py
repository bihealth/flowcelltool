# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    # FlowCell related -------------------------------------------------------
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
]
