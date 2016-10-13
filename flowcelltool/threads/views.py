# -*- coding: utf-8 -*-
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import redirect, get_object_or_404

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field

from .models import Message
from . import forms


class MessageCreateView(CreateView):
    """CBV for creating Message

    Meant for subclassing, related_model must be set
    """

    #: Required Model type to "thread" messages on, override in child class
    related_model = None

    #: The Model type to handle
    model = Message

    #: The Form class to use
    form_class = forms.MessageForm

    def dispatch(self, *args, **kwargs):
        if not self.related_model:
            raise ValueError('Missing setting "related_model"')
        self.related_object = get_object_or_404(  # noqa
            self.related_model, pk=kwargs['related_pk'])
        return super().dispatch(*args, **kwargs)

    def get_success_url(self):
        """Return absolute URL of the related object"""
        return self.related_object.get_absolute_url()

    def form_valid(self, form):
        self.object = form.save(self.request, self.related_object)  # noqa
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_object'] = self.related_object
        # Setup djangocrispy-forms helper
        context['helper'] = FormHelper()
        context['helper'].form_tag = False
        context['helper'].layout = Layout(
            Field('title'),
            Field('body'),
            Field('attachments', css_class='multi-upload'),
        )
        return context


class MessageUpdateView(UpdateView):
    """CBV for updating messages"""

    #: The Model type to handle
    model = Message

    #: The fields to show in the form
    fields = ['title', 'body']

    def get_success_url(self):
        """Return absolute URL of the related object"""
        return self.object.content_object.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Setup djangocrispy-forms helper
        context['helper'] = FormHelper()
        context['helper'].form_tag = False
        context['helper'].layout = Layout(
            Field('title'),
            Field('body'),
        )
        return context


class MessageDeleteView(DeleteView):
    """CBV for deleting messages"""

    #: The Model type to handle
    model = Message

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = self.object.content_object.get_absolute_url()
        return context

    def get_success_url(self):
        """Return absolute URL of the related object"""
        return self.object.content_object.get_absolute_url()
