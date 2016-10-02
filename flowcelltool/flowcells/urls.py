# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^$',
        view=views.FlowCellListView.as_view(),
        name='list'
    ),
]
