from django.conf.urls import url

from openstack_dashboard.dashboards.docker_compose.deploy_compose.services import views

urlpatterns = [
    url(r'^create/$', views.CreateService.as_view(), name='create'),
]
