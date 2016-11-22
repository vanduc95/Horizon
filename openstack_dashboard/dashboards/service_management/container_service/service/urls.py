from django.conf.urls import url

from openstack_dashboard.dashboards.service_management.container_service.service import views

urlpatterns = [
    url(r'^create/$', views.CreateService.as_view(), name='create'),
]
