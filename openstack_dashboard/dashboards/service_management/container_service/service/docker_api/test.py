
from openstack_dashboard.dashboards.service_management.container_service.service.docker_api import docker_api

cli = docker_api.connect_docker()

nets = cli.networks()
print nets
