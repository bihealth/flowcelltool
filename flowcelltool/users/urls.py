# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from flowcelltool.users import views

urlpatterns = [
    # TODO: add /profile/
    url(
        regex=r'^(?P<username>\S+)/$',
        view=views.UserTokenListView.as_view(),
        name='detail',
    ),

    url(
        regex=r'^token/$',
        view=views.UserTokenListView.as_view(),
        name='token_list',
    ),

    url(
        regex=r'^token/create/$',
        view=views.UserTokenCreateView.as_view(),
        name='token_create',
    ),

    url(
        regex=r'^token/delete/(?P<pk>.+)/$',
        view=views.UserTokenDeleteView.as_view(),
        name='token_delete',
    ),
]
