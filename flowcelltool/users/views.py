# -*- coding: utf-8 -*-

import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, FormView
from django.views.generic.list import ListView

from rules.contrib.views import PermissionRequiredMixin

from knox import models as knox_models

from . import forms

UserModel = get_user_model()


class ProfileView(LoginRequiredMixin, DetailView):
    """CBV for viewing the user profile."""

    model = DetailView
    template_name = 'profile/user_detail.html'

    def get_object(self):
        return self.request.user


class UserTokenListView(LoginRequiredMixin, ListView):
    """CBV for listing user tokens."""

    model = knox_models.AuthToken
    template_name = 'profile/token_list.html'

    def get_queryset(self):
        return knox_models.AuthToken.objects.filter(user=self.request.user)


class UserTokenCreateView(LoginRequiredMixin, FormView):
    """CBV for creating user tokens."""

    template_name = 'profile/token_create.html'
    form_class = forms.UserTokenCreateForm

    def form_valid(self, form):
        """Called after the form validates"""
        ttl = datetime.timedelta(hours=form.clean().get('ttl')) or None
        context = self.get_context_data()
        context['token'] = knox_models.AuthToken.objects.create(self.request.user, ttl)
        return render(self.request, 'profile/token_create_success.html', context)


class UserTokenDeleteView(
        LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """CBV for deleting user tokens."""
    permission_required = 'users.delete_token'

    model = knox_models.AuthToken
    template_name = 'profile/token_confirm_delete.html'
    success_url = reverse_lazy('profile:token_list')
