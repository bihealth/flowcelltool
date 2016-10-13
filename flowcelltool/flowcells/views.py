import logging
import re

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, \
    FormView
from django.db import IntegrityError

from crispy_forms.helper import FormHelper
from rules.contrib.views import PermissionRequiredMixin

from . import models, forms, import_export
from ..threads.views import MessageCreateView, MessageUpdateView, \
    MessageDeleteView


LOGGER = logging.getLogger(__name__)


# Home View -------------------------------------------------------------------


class HomeView(LoginRequiredMixin, TemplateView):
    """For displaying the home screen"""

    #: The template with the form to render
    template_name = 'flowcells/home.html'

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        result['num_flow_cells'] = models.FlowCell.objects.count()
        result['num_libraries'] = models.FlowCell.objects.count()
        result['num_barcode_sets'] = models.BarcodeSet.objects.count()
        return result


# SequencingMachine Views -----------------------------------------------------


class SequencingMachineListView(
        LoginRequiredMixin, ListView):
    """Shows a list of sequencing machines"""

    model = models.SequencingMachine


class SequencingMachineCreateView(
        LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """View for creating sequencing machine"""

    permission_required = 'flowcells.add_sequencingmachine'

    model = models.SequencingMachine

    fields = ['vendor_id', 'label', 'description', 'machine_model',
              'slot_count', 'dual_index_workflow']


class SequencingMachineDetailView(
        LoginRequiredMixin, DetailView):
    """View detail of sequencing machine"""

    model = models.SequencingMachine


class SequencingMachineUpdateView(
        LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """View for updating sequencing machines"""

    permission_required = 'flowcells.change_sequencingmachine'

    model = models.SequencingMachine

    fields = ['vendor_id', 'label', 'description', 'machine_model',
              'slot_count', 'dual_index_workflow']


class SequencingMachineDeleteView(
        LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """View for deleting sequencing machines"""

    permission_required = 'flowcells.delete_sequencingmachine'

    model = models.SequencingMachine

    success_url = reverse_lazy('instrument_list')


# SeqeuencingMachine Views ----------------------------------------------------


class BarcodeSetListView(
        LoginRequiredMixin, ListView):
    """Shows a list of sequencing machines"""

    model = models.BarcodeSet


class BarcodeSetCreateView(
        LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """View for creating sequencing machine"""

    permission_required = 'flowcells.add_barcodeset'

    model = models.BarcodeSet

    #: Fields to show in creation form
    fields = ['name', 'short_name', 'description']


class BarcodeSetDetailView(
        LoginRequiredMixin, DetailView):
    """View detail of sequencing machine"""

    model = models.BarcodeSet


class BarcodeSetUpdateView(
        LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """View for updating sequencing machines"""

    permission_required = 'flowcells.change_barcodeset'

    model = models.BarcodeSet

    #: Fields to show in creation form
    fields = ['name', 'short_name', 'description']


class BarcodeSetDeleteView(
        LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """View for deleting sequencing machines"""

    permission_required = 'flowcells.delete_barcodeset'

    model = models.BarcodeSet

    #: URL to redirect to on success
    success_url = reverse_lazy('barcodeset_list')


class BarcodeSetExportView(
        LoginRequiredMixin, View):
    """Exporting of BarcodeSet objects to JSON"""

    def dispatch(self, request, *args, **kwargs):
        barcode_set = get_object_or_404(
            models.BarcodeSet, pk=kwargs['pk'])
        dumper = import_export.BarcodeSetDumper()
        response = HttpResponse(dumper.run(barcode_set),
                                content_type='text/plain')
        fname = re.sub('[^a-zA-Z0-9_-]', '_', barcode_set.name)
        response['Content-Disposition'] = (
            'attachment; filename="barcode_set_{}.json"'.format(fname))
        return response


class BarcodeSetImportView(
        LoginRequiredMixin, PermissionRequiredMixin, FormView):
    """Importing of BarcodeSet objects from JSON"""

    permission_required = 'flowcells.add_barcodeset'

    #: The template with the form to render
    template_name = 'flowcells/barcodeset_import.html'

    #: The form to use for importing JSON files
    form_class = forms.BarcodeSetImportForm

    def form_valid(self, form):
        """Redirect to barcode set view if the form validated"""
        payload = self.request.FILES['json_file'].read().decode('utf-8')
        loader = import_export.BarcodeSetLoader()
        try:
            barcode_set = loader.run(payload)
        except IntegrityError:
            form.add_error(
                'json_file',
                'Problem during import. Is the barcode set name unique?')
            return self.form_invalid(form)
        return redirect(reverse('barcodeset_view',
                                kwargs={'pk': barcode_set.pk}))


# BarcodeSetEntry Views -------------------------------------------------------


class BarcodeSetEntryUpdateView(
        LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Form for updating all adapter barcode set entries of a barcode set
    """

    permission_required = 'flowcells.change_barcodeset'

    model = models.BarcodeSet

    #: Fields to allow in update form
    fields = ['name', 'short_name', 'description']

    #: Template to use for the form
    template_name = 'flowcells/barcodeset_updateentries.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()  # noqa
        barcode_set_entry_form = self._construct_formset()
        return self.render_to_response(
            self.get_context_data(self.object.id,
                                  formset=barcode_set_entry_form))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        barcode_set_entry_form = self._construct_formset(request.POST)
        if barcode_set_entry_form.is_valid():
            return self.form_valid(request, barcode_set_entry_form)
        else:
            return self.form_invalid(barcode_set_entry_form)

    def _construct_formset(self, data=None):
        barcode_set_entry_form = forms.BarcodeSetEntryFormSet(
            data=data, barcode_set=self.object)
        return barcode_set_entry_form

    def form_valid(self, request, barcode_set_entry_form, *args, **kwargs):
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
        self.object = models.BarcodeSet.objects.get(pk=pk)  # noqa
        context['object'] = self.object
        context['formset'] = kwargs['formset']
        context['helper'] = FormHelper()
        context['helper'].form_tag = False
        context['helper'].template = \
            'bootstrap4/table_inline_formset.html'
        return context


# FlowCell Views --------------------------------------------------------------


class FlowCellListView(
        LoginRequiredMixin, ListView):
    """Shows a list of flow cells, this is the index page"""

    model = models.FlowCell


class FlowCellCreateView(
        LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Show the view for creating a flow cell"""

    permission_required = 'flowcells.add_flowcell'

    #: The model type to create
    model = models.FlowCell

    #: Fields to show in the create view, the rest is auto-filled
    fields = ('name', 'description', 'num_lanes', 'status', 'operator',
              'is_paired', 'index_read_count', 'rta_version', 'read_length')

    def form_valid(self, form):
        self.object = form.save(commit=False)  # noqa
        self.object.owner = self.request.user
        self.object.save()
        return redirect(reverse(
            'flowcell_view', kwargs={'pk': self.object.pk}))


class FlowCellDetailView(
        LoginRequiredMixin, DetailView):
    """Show the view for creating a flow cell"""

    #: The model type to create
    model = models.FlowCell

    def get_context_data(self, *args, **kwargs):
        """Overwritten version for retrievin template values

        Injecting the prefill barcode set form into the template with the
        django-crispy-forms helper object.
        """
        context = super().get_context_data(*args, **kwargs)
        context['prefill_form'] = forms.LibrariesPrefillForm()
        context['helper'] = FormHelper()
        context['helper'].form_tag = False
        context['helper'].form_method = 'GET'
        return context


class FlowCellUpdateView(
        LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Show the view for updating a flow cell"""

    permission_required = 'flowcells.change_flowcell'

    #: The model type to create
    model = models.FlowCell

    #: Fields to show in the create view, the rest is auto-filled
    fields = ('name', 'description', 'num_lanes', 'status', 'operator',
              'is_paired', 'index_read_count', 'rta_version', 'read_length')


class FlowCellDeleteView(
        LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """View for deleting flow cell"""

    permission_required = 'flowcells.delete_flowcell'

    #: The model type to delete
    model = models.FlowCell

    #: URL to redirect to on success
    success_url = reverse_lazy('flowcell_list')


class FlowCellExportView(
        LoginRequiredMixin, View):
    """Exporting of FlowCell objects to JSON"""

    def dispatch(self, request, *args, **kwargs):
        flow_cell = get_object_or_404(
            models.FlowCell, pk=kwargs['pk'])
        dumper = import_export.FlowCellDumper()
        response = HttpResponse(dumper.run(flow_cell),
                                content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="flowcell_{}.json"'.format(
                flow_cell.token_vendor_id()))
        return response


class FlowCellImportView(
        LoginRequiredMixin, PermissionRequiredMixin, FormView):
    """Importing of FlowCell objects from JSON"""

    permission_required = 'flowcells.add_flowcell'

    #: The template with the form to render
    template_name = 'flowcells/flowcell_import.html'

    #: The form to use for importing JSON files
    form_class = forms.FlowCellImportForm

    def form_valid(self, form):
        """Redirect to barcode set view if the form validated"""
        payload = self.request.FILES['json_file'].read().decode('utf-8')
        loader = import_export.FlowCellLoader()
        try:
            loader.run(payload)
        except IntegrityError:
            form.add_error(
                'json_file',
                'Problem during import. Is the flow cell name unique?')
            return self.form_invalid(form)


class FlowCellSampleSheetView(
        LoginRequiredMixin, DetailView):
    """Display of flow cell as sample sheet"""

    #: The model type to create
    model = models.FlowCell

    #: The template
    template_name = 'flowcells/flowcell_sheet.html'

    def get_context_data(self, *args, **kwargs):
        gen = import_export.FlowCellSampleSheetGenerator(self.object)
        context = super().get_context_data(*args, **kwargs)
        context['csv_v1'] = gen.build_v1()
        context['csv_v2'] = gen.build_v2()
        context['yaml'] = gen.build_yaml()
        return context


# FlowCell-Message related ----------------------------------------------------


class FlowCellAddMessageView(
        LoginRequiredMixin, PermissionRequiredMixin, MessageCreateView):

    permission_required = 'flowcells.add_message'

    #: The type of the related object on which to "thread" the messages
    related_model = models.FlowCell


class FlowCellUpdateMessageView(
        LoginRequiredMixin, PermissionRequiredMixin, MessageUpdateView):

    permission_required = 'flowcells.change_message'


class FlowCellDeleteMessageView(
        LoginRequiredMixin, PermissionRequiredMixin, MessageDeleteView):

    permission_required = 'flowcells.delete_message'



# Library Views ---------------------------------------------------------------


class LibraryUpdateView(
        LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Form for updating all libraries on a flowcell
    """

    permission_required = 'flowcells.change_flowcell'

    model = models.FlowCell

    #: Base form class to use
    form_class = forms.FlowCellForm

    #: Template to use for the form
    template_name = 'flowcells/flowcell_updatelibraries.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()  # noqa
        library_form = self._construct_formset()
        return self.render_to_response(
            self.get_context_data(self.object.id,
                                  formset=library_form))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()  # noqa
        library_form = self._construct_formset(request.POST)
        if library_form.is_valid():
            return self.form_valid(request, library_form)
        else:
            return self.form_invalid(library_form)

    def _construct_formset(self, data=None):
        if self.request.GET.get('barcode1'):
            barcode_set1 = get_object_or_404(
                models.BarcodeSet, pk=self.request.GET['barcode1'])
        else:
            barcode_set1 = None
        if self.request.GET.get('barcode2'):
            barcode_set2 = get_object_or_404(
                models.BarcodeSet, pk=self.request.GET['barcode2'])
        else:
            barcode_set2 = None
        initial = {'barcode_set': barcode_set1,
                   'barcode_set2': barcode_set2}
        library_form = forms.LibraryFormSet(
            data=data, flow_cell=self.object,
            initial=[initial] * forms.EXTRA_LIBRARY_FORMS)
        return library_form

    def form_valid(self, request, library_form, *args, **kwargs):
        library_form.save()
        if request.POST.get('submit_more'):
            return redirect(request.get_full_path())
        else:
            return redirect(self.get_success_url())

    def form_invalid(self, library_form, *args, **kwargs):
        return self.render_to_response(
            self.get_context_data(self.object.id,
                                  formset=library_form))

    def get_context_data(self, pk, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object = models.FlowCell.objects.get(pk=pk)  # noqa
        context['object'] = self.object
        context['formset'] = kwargs['formset']
        context['helper'] = FormHelper()
        context['helper'].form_tag = False
        context['helper'].template = \
            'bootstrap4/table_inline_formset.html'
        return context


# Search-Related Views --------------------------------------------------------


class SearchView(LoginRequiredMixin, TemplateView):
    """Shows a list of sequencing machines"""

    template_name = 'flowcells/search.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        query = self.request.GET.get('q')
        results = []
        context['is_search'] = True
        context['results'] = models.Library.objects.filter(name__contains=query)
        context['query'] = query
        return context
