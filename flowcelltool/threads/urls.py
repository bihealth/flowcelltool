# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^add-for/(?P<app_label>[\w\-]+)/(?P<model_name>[\w\-]+)/(?P<pk>\d+)/$',
        views.MessageAddView.as_view(), name='add'),
    url(r'^delete/(?P<attachment_pk>\d+)/$',
        views.MessageDeleteView.as_view(), name='delete'),
]
