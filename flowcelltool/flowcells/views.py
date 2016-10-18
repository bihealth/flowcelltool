import logging

import re

from django.db import transaction
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
from crispy_forms.layout import Layout, Field
from rules.contrib.views import PermissionRequiredMixin
from formtools.wizard.views import SessionWizardView

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
        LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Shows a list of sequencing machines"""

    permission_required = 'flowcells.list_sequencingmachine'

    queryset = models.SequencingMachine.objects.order_by('vendor_id')


class SequencingMachineCreateView(
        LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """View for creating sequencing machine"""

    permission_required = 'flowcells.add_sequencingmachine'

    model = models.SequencingMachine

    fields = ['vendor_id', 'label', 'description', 'machine_model',
              'slot_count', 'dual_index_workflow']


class SequencingMachineDetailView(
        LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """View detail of sequencing machine"""

    permission_required = 'flowcells.view_sequencingmachine'

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
        LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Shows a list of sequencing machines"""

    permission_required = 'flowcells.list_barcodeset'

    queryset = models.BarcodeSet.objects.order_by('name')


class BarcodeSetCreateView(
        LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """View for creating sequencing machine"""

    permission_required = 'flowcells.add_barcodeset'

    model = models.BarcodeSet

    #: Fields to show in creation form
    fields = ['name', 'short_name', 'description']


class BarcodeSetDetailView(
        LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """View detail of sequencing machine"""

    permission_required = 'flowcells.view_barcodeset'

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
        LoginRequiredMixin, PermissionRequiredMixin, View):
    """Exporting of BarcodeSet objects to JSON"""

    permission_required = 'flowcells.view_barcodeset'

    def get(self, request, *args, **kwargs):
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
        except ValueError:
            form.add_error(
                'json_file',
                'Problem during import. Is the JSON file valid?')
            return self.form_invalid(form)
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
        self.object = self.get_object()  # noqa
        barcode_set_entry_form = self._construct_formset(request.POST)
        if barcode_set_entry_form.is_valid():
            return self.form_valid(request, barcode_set_entry_form)
        else:
            return self.form_invalid(barcode_set_entry_form)

    def _construct_formset(self, data=None):
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
        LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Shows a list of flow cells, this is the index page"""

    permission_required = 'flowcells.list_flowcell'

    queryset = models.FlowCell.objects.order_by('name')


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
        LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """Show the view for creating a flow cell"""

    permission_required = 'flowcells.view_flowcell'

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
        LoginRequiredMixin, PermissionRequiredMixin, View):
    """Exporting of FlowCell objects to JSON"""

    permission_required = 'flowcells.view_flowcell'

    def get(self, request, *args, **kwargs):
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
            flow_cell = loader.run(payload)
            return redirect(flow_cell.get_absolute_url())
        except IntegrityError:
            form.add_error(
                'json_file',
                'Problem during import. Is the flow cell name unique?')
            return self.form_invalid(form)


class FlowCellSampleSheetView(
        LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """Display of flow cell as sample sheet"""

    permission_required = 'flowcells.view_flowcell'

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

    permission_required = 'threads.add_message'

    #: The type of the related object on which to "thread" the messages
    related_model = models.FlowCell


class FlowCellUpdateMessageView(
        LoginRequiredMixin, PermissionRequiredMixin, MessageUpdateView):

    permission_required = 'threads.change_message'


class FlowCellDeleteMessageView(
        LoginRequiredMixin, PermissionRequiredMixin, MessageDeleteView):

    permission_required = 'threads.delete_message'


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

    def form_valid(self, request, library_form):
        library_form.save()
        if request.POST.get('submit_more'):
            return redirect(request.get_full_path())
        else:
            return redirect(self.get_success_url())

    def form_invalid(self, library_form):
        return self.render_to_response(
            self.get_context_data(self.object.id,
                                  formset=library_form))

    def get_context_data(self, pk, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object = models.FlowCell.objects.get(pk=pk)  # noqa
        context['object'] = self.object
        context['formset'] = kwargs['formset']
        context['helper'] = FormHelper()
        context['helper'].layout = Layout(
            Field('name', css_class='form-control-sm'),
            Field('reference', css_class='form-control-sm'),
            Field('barcode_set',
                  css_class='barcode-set-field form-control-sm'),
            Field('barcode', css_class='barcode-field form-control-sm'),
            Field('barcode_set2',
                  css_class='barcode-set-field2 form-control-sm'),
            Field('barcode2', css_class='barcode-field2 form-control-sm'),
            Field('lane_numbers', css_class='form-control-sm'),
        )
        context['helper'].form_tag = False
        context['helper'].template = \
            'bootstrap4/table_inline_formset.html'
        return context


class FlowCellExtractLibrariesView(
        LoginRequiredMixin, PermissionRequiredMixin, SessionWizardView):
    """Display of flow cell as sample sheet"""

    permission_required = 'flowcells.change_flowcell'

    FORMS = (
        ('paste_tsv', forms.PasteTSVForm),
        ('pick_columns', forms.PickColumnsForm),
        ('confirm', forms.ConfirmExtractionForm),
    )

    TEMPLATES = {
        'paste_tsv': 'flowcells/flowcell_extractlibraries.html',
        'pick_columns': 'flowcells/flowcell_extractlibraries_pick.html',
        'confirm': 'flowcells/flowcell_extractlibraries_confirm.html',
    }

    #: Initial values for the forms in the individual steps
    initial_dict = {
        'pick_columns': {
            'reference': models.REFERENCE_HUMAN,
            'sample_column': 1,
            'barcode_column': 2,
            'first_row': 1,
            'lane_numbers_column': 3,
        }
    }

    def get_template_names(self):
        """Return name of current template"""
        return self.TEMPLATES[self.steps.current]

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['object'] = get_object_or_404(
            models.FlowCell, pk=self.kwargs['pk'])
        context['helper'] = FormHelper()
        context['helper'].form_tag = False
        context['helper'].template_pack = 'bootstrap4'
        if self.steps.current == 'pick_columns':
            table_rows, table_ncols = self._extract_payload(
                self.get_cleaned_data_for_step('paste_tsv')['payload'])
            context['table_rows'] = table_rows
            context['table_cols'] = table_ncols
        elif self.steps.current == 'confirm':
            context['libraries'] = self._build_libraries()
        return context

    def done(self, *args, **kwargs):
        flow_cell = get_object_or_404(models.FlowCell, pk=self.kwargs['pk'])
        with transaction.atomic():
            for library in self._build_libraries():
                library.save()
            return redirect(reverse(
                'flowcell_view', kwargs={'pk': flow_cell.pk}))

    def _build_libraries(self):
        """Build library objects from result of paste_tsv and pick_columns
        steps
        """
        flow_cell = get_object_or_404(models.FlowCell, pk=self.kwargs['pk'])
        table_rows, _ = self._extract_payload(
            self.get_cleaned_data_for_step('paste_tsv')['payload'])
        pick_results = self.get_cleaned_data_for_step('pick_columns')
        result = []
        for row in table_rows[pick_results['first_row'] - 1:]:
            barcode = self._select_barcode(
                row, pick_results['barcode_set'],
                pick_results['barcode_column'])
            barcode2 = self._select_barcode(
                row, pick_results['barcode_set2'],
                pick_results['barcode2_column'])
            lane_numbers = self._get_lane_numbers(
                row, pick_results['lane_numbers_column'])
            library = models.Library(
                flow_cell=flow_cell,
                name=row[pick_results['sample_column'] - 1],
                reference=pick_results['reference'],
                barcode_set=pick_results['barcode_set'],
                barcode=barcode,
                barcode_set2=pick_results['barcode_set2'],
                barcode2=barcode2,
                lane_numbers=lane_numbers)
            result.append(library)
        return result

    def _get_lane_numbers(self, row, lane_numbers_column):
        """Return list of integer lane numbers
        """
        return list(map(int, row[lane_numbers_column - 1].split(',')))

    def _select_barcode(self, row, barcode_set, barcode_column):
        """Select barcode from barcode_set with "best" match

        The heuristic used for a "best" match is as follows:

        - suffix has to be a suffix of the barcode name
        - count the number of preceding digits [1-9] before the suffix
        - the first one with fewest number of digits [1-9] wins

        Effectively this breaks the tie of "1" against "01" and "11" in
        favour of "01", against "1" and "11" in favour of "1" and so on.
        """
        if not barcode_column:
            return None
        else:
            suffix = row[barcode_column - 1]
        candidates = []
        for entry in barcode_set.entries.all():
            if not entry.name.endswith(suffix):
                continue  # ignore
            m = re.match(r'([1-9]+)$', entry.name[:-(len(suffix))])
            l = 0 if not m else len(m.groups(1))
            candidates.append((l, entry))
        if not candidates:
            return None
        else:
            return list(sorted(candidates, key=lambda x: x[0]))[0][1]

    @classmethod
    def _extract_payload(self, payload):
        """Convert payload TSV to array of arrays with same dimension"""
        table = []
        rows = payload.replace('\r\n', '\n').split('\n')
        for row in rows:
            if any(f.strip() for f in row):
                table.append(row.split('\t'))
        max_cols = max(len(row) for row in table)
        for i, row in enumerate(table):
            if len(row) != max_cols:
                table[i] += ([''] * (max_cols - len(row)))
        table_ncols = list(range(max_cols))
        return table, table_ncols


# Search-Related Views --------------------------------------------------------


class SearchView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """Shows a list of sequencing machines"""

    permission_required = 'flowcells.search'

    template_name = 'flowcells/search.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        query = self.request.GET.get('q', '')
        context['is_search'] = True
        if query:
            context['results'] = models.Library.objects.filter(
                name__contains=query)
        else:
            context['results'] = []
        context['query'] = query
        return context
