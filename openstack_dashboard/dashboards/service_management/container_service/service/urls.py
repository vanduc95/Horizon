from django.conf.urls import url

from openstack_dashboard.dashboards.service_management.container_service.service import views

urlpatterns = [
    url(r'^create/$', views.CreateService.as_view(), name='create'),
    url(r'^image_docker', views.ImageDockerRequest.as_view(), name='image_docker'),
    url(r'^network_detail', views.NetworkDetailRequest.as_view(), name='network_detail'),
    url(r'^container_list',views.ListContainerInServiceRequest.as_view(),name='container_list'),

]
