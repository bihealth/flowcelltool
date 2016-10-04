from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from . import models


# SeqeuencingMachine Views ----------------------------------------------------


class SequencingMachineListView(ListView):
    """Shows a list of sequencing machines"""

    model = models.SequencingMachine


class SequencingMachineCreateView(CreateView):
    """View for creating sequencing machine"""

    model = models.SequencingMachine

    fields = ['vendor_id', 'label', 'description', 'machine_model',
              'slot_count', 'dual_index_workflow']


class SequencingMachineDetailView(DetailView):
    """View detail of sequencing machine"""

    model = models.SequencingMachine


class SequencingMachineUpdateView(UpdateView):
    """View for updating sequencing machines"""

    model = models.SequencingMachine

    fields = ['vendor_id', 'label', 'description', 'machine_model',
              'slot_count', 'dual_index_workflow']


class SequencingMachineDeleteView(DeleteView):
    """View for deleting sequencing machines"""

    model = models.SequencingMachine
    success_url = reverse_lazy('instrument_list')


# FlowCell Views --------------------------------------------------------------


class FlowCellListView(ListView):
    """Shows a list of flow cells, this is the index page"""

    model = models.FlowCell


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


class FlowCellDeleteView(DeleteView):
    """View for deleting flow cell"""

    model = models.FlowCell
    success_url = reverse_lazy('flowcell_list')
