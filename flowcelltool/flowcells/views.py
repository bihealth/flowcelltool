from django.shortcuts import render
from django.views.generic import TemplateView

from . import models


class FlowCellListView(TemplateView):
    """Shows a list of flow cells, this is the index page"""
    template_name = 'flowcells/flowcell_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['flowcell_list'] = \
            models.FlowCell.objects.all().order_by('name')
        return context
