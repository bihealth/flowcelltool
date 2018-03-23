from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from . import views

# API
urlpatterns = [
    url(r'auth/', include('knox.urls')),
]

# Add special views from view sets

urlpatterns += [
    url(
        regex=r'^flowcell/resolve/(?P<instrument_id>.+)/(?P<run_no>.+)/(?P<flowcell_id>.+)/$',
        view=views.FlowCellViewSet.as_view({'get': 'resolve'}),
        name='flowcell-resolve',
    ),
    url(
        regex=r'^sequencingmachine/by_vendor_id/(?P<vendor_id>.+)/$',
        view=views.SequencingMachineViewSet.as_view({'get': 'by_vendor_id'}),
        name='sequencing_machine-by-vendor-id',
    ),
]

router = DefaultRouter()
router.register(r'flowcell', views.FlowCellViewSet, base_name='flowcell')
router.register(r'barcodeset', views.BarcodeSetViewSet, base_name='barcodeset')
router.register(r'sequencingmachine', views.SequencingMachineViewSet, base_name='sequencingmachine')
router.register(r'message', views.FlowCellMessageViewSet, base_name='message')

urlpatterns += router.urls
