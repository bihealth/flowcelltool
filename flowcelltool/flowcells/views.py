from django.urls import reverse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from . import models


class FlowCellListView(TemplateView):
    """Shows a list of flow cells, this is the index page"""

    template_name = 'flowcells/flowcell_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['flowcell_list'] = \
            models.FlowCell.objects.all().order_by('name')
        return context


class FlowCellCreateView(CreateView):
    """Show the view for creating a flow cell"""

    #: The model type to create
    model = models.FlowCell

    #: Fields to show in the create view, the rest is auto-filled
    fields = ('name', 'num_lanes', 'status', 'operator', 'is_paired',
              'index_read_count', 'rta_version', 'read_length')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()
        return redirect(reverse(
            'flowcell_view', kwargs={'pk': self.object.pk}))


class FlowCellDetailView(DetailView):
    """Show the view for creating a flow cell"""

    #: The model type to create
    model = models.FlowCell

    #: Fields to show in the create view, the rest is auto-filled
    fields = ('name', 'num_lanes', 'status', 'operator', 'is_paired',
              'index_read_count', 'rta_version', 'read_length')


class FlowCellUpdateView(UpdateView):
    """Show the view for updating a flow cell"""

    #: The model type to create
    model = models.FlowCell

    #: Fields to show in the create view, the rest is auto-filled
    fields = ('name', 'num_lanes', 'status', 'operator', 'is_paired',
              'index_read_count', 'rta_version', 'read_length')
