from django.conf.urls import include, url
from rest_framework.routers import SimpleRouter

from . import views

# API
urlpatterns = [
    url(r'auth/', include('knox.urls')),
]

router = SimpleRouter()
router.register(r'flowcell', views.FlowCellViewSet, base_name='flowcell')
router.register(r'barcodeset', views.BarcodeSetViewSet, base_name='barcodeset')
router.register(r'sequencingmachine', views.SequencingMachineViewSet, base_name='sequencingmachine')
router.register(r'message', views.FlowCellMessageViewSet, base_name='message')

urlpatterns += router.urls

# Add special views from view sets

urlpatterns += [
    url(
        regex=r'^flowcell/by_vendor_id/(?P<vendor_id>.+)/$',
        view=views.FlowCellViewSet.as_view({'get': 'by_vendor_id'}),
        name='flowcell_by_vendor_id',
    ),
]

# Add special updating views

urlpatterns += [
    # Update adapter, quality scores, and status fields
    url(
        regex=r'^flowcell/(?P<uuid>[^/.]+)/update/$',
        view=views.FlowCellUpdateView.as_view(),
        name='flowcell_update',
    ),
]
