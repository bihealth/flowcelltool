import re

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from crispy_forms.helper import FormHelper

from . import models, forms, import_export


# SequencingMachine Views -----------------------------------------------------


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


# SeqeuencingMachine Views ----------------------------------------------------


class BarcodeSetListView(ListView):
    """Shows a list of sequencing machines"""

    model = models.BarcodeSet


class BarcodeSetCreateView(CreateView):
    """View for creating sequencing machine"""

    model = models.BarcodeSet

    #: Fields to show in creation form
    fields = ['name', 'short_name', 'description']


class BarcodeSetDetailView(DetailView):
    """View detail of sequencing machine"""

    model = models.BarcodeSet


class BarcodeSetUpdateView(UpdateView):
    """View for updating sequencing machines"""

    model = models.BarcodeSet

    #: Fields to show in creation form
    fields = ['name', 'short_name', 'description']


class BarcodeSetDeleteView(DeleteView):
    """View for deleting sequencing machines"""

    model = models.BarcodeSet

    #: URL to redirect to on success
    success_url = reverse_lazy('barcodeset_list')


class BarcodeSetExportView(View):
    """Exporting of BarcodeSet objects to JSON"""

    def dispatch(self, request, *args, **kwargs):
        barcode_set = get_object_or_404(
            models.BarcodeSet, pk=kwargs['pk'])
        dumper = import_export.BarcodeSetDumper()
        response = HttpResponse(dumper.run(barcode_set),
                                content_type='text/plain')
        fname = re.sub('[^a-zA-Z0-9_-]', '_', barcode_set.name)
        response['Content-Disposition'] = (
            'attachment; filename="{}.json"'.format(fname))
        return response


# BarcodeSetEntry Views -------------------------------------------------------


class BarcodeSetEntryUpdateView(UpdateView):
    """Form for updating all adapter barcode set entries of a barcode set
    """

    model = models.BarcodeSet

    #: Fields to allow in update form
    fields = ['name', 'short_name', 'description']

    #: Template to use for the form
    template_name = 'flowcells/barcodeset_updateentries.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        barcode_set_entry_form = self._construct_formset(**kwargs)
        return self.render_to_response(
            self.get_context_data(self.object.id,
                                  formset=barcode_set_entry_form))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        barcode_set_entry_form = self._construct_formset(request.POST, **kwargs)
        if barcode_set_entry_form.is_valid():
            return self.form_valid(request, barcode_set_entry_form)
        else:
            return self.form_invalid(barcode_set_entry_form)

    def _construct_formset(self, data=None, **kwargs):
        barcode_set_entry_form = forms.BarcodeSetEntryFormSet(
            data=data, barcode_set=self.object)
        return barcode_set_entry_form

    def form_valid(self, request, barcode_set_entry_form):
        for form in barcode_set_entry_form:
            form.instance.barcode_set = self.object
        barcode_set_entry_form.save()
        if request.POST.get('submit_more'):
            return redirect(request.get_full_path())
        else:
            return redirect(self.get_success_url())

    def form_invalid(self, barcode_set_entry_form):
        return self.render_to_response(
            self.get_context_data(self.object.id,
                                  formset=barcode_set_entry_form))

    def get_context_data(self, pk, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object = models.BarcodeSet.objects.get(pk=pk)
        context['object'] = self.object
        context['formset'] = kwargs['formset']
        context['helper'] = FormHelper()
        context['helper'].form_tag = False
        context['helper'].template = \
            'bootstrap4/table_inline_formset.html'
        return context


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

    #: URL to redirect to on success
    success_url = reverse_lazy('flowcell_list')
