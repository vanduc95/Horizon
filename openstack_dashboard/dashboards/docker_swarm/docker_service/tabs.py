from docker import Client
import time
from horizon import tabs
from openstack_dashboard.dashboards.docker_swarm.docker_service.services import tables as tbl_service
from openstack_dashboard.dashboards.docker_swarm.docker_service.service_monitor import \
    tables as tbl_service_monitor


class Service:
    def __init__(self, serviceID, name, replicate):
        self.id = serviceID
        self.name = name
        self.replicate = replicate

class Container:
    def __init__(self, containerId, image, command, created, state, name, host_ip):
        self.id = containerId
        self.image = image
        self.command = command
        self.created = created
        self.state = state
        self.name = name
        self.host_ip = host_ip


class ServiceTab(tabs.TableTab):
    name = tbl_service.DockerServiceTable.Meta.verbose_name
    slug = tbl_service.DockerServiceTable.Meta.name
    table_classes = (tbl_service.DockerServiceTable,)
    template_name = ("horizon/common/_detail_table.html")

    def get_docker_service_data(self):
        cli = Client(base_url='unix://var/run/docker.sock')
        services = []
        for service in cli.services():
            id = service['ID']
            name = service['Spec']['Name']
            replicate = service['Spec']['Mode']['Replicated']['Replicas']
            services.append(Service(id, name, replicate))
        return services


class ServiceMonitorTab(tabs.TableTab):
    name = tbl_service_monitor.ContainerInServiceTable.Meta.verbose_name
    slug = tbl_service_monitor.ContainerInServiceTable.Meta.name
    table_classes = (tbl_service_monitor.ContainerInServiceTable,)
    # template_name = ("horizon/common/_detail_table.html")
    template_name = ("docker_swarm/docker_service/service_monitor/detail_service_monitor.html")

    def get_container_in_service_data(self):
        host_ip = ['0.0.0.0','192.168.2.129','192.168.2.128']
        cli = Client(base_url='unix://var/run/docker.sock')
        services = []
        for service in cli.services():
            name = service['Spec']['Name']
            services.append(name)
        containers = []
        if self.request.method == 'GET' and 'service' in self.request.GET \
                and self.request.GET['service'] != '-1' and self.request.GET['service'] in services:
            # dict_container = cli.containers(filters={'name': self.request.GET['service']})
            # for ct in dict_container:
            #     # convert data
            #     created = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ct['Created']))
            #     name = ct['Names'][0][1:]
            #     containers.append(
            #         Container(ct['Id'][:12], ct['Image'], ct['Command'], created, ct['State'], name))
            # return containers
            for ip in host_ip:
                try:
                    cli = Client(base_url='tcp://' + ip + ':2376')
                    dict_container = cli.containers(filters={'name': self.request.GET['service']})
                    for ct in dict_container:
                        # convert data
                        created = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ct['Created']))
                        name = ct['Names'][0][1:]
                        containers.append(
                            Container(ct['Id'][:12], ct['Image'], ct['Command'], created, ct['State'], name, ip))
                except:
                    print 'Cant connect', ip

            return containers
        else:
            return containers


    def get_context_data(self, request, **kwargs):
        context = super(ServiceMonitorTab, self).get_context_data(request, **kwargs)

        cli = Client(base_url='unix://var/run/docker.sock')
        services = []
        for service in cli.services():
            name = service['Spec']['Name']
            services.append(name)

        context['services'] = services

        if self.request.method == 'GET' and 'service' in self.request.GET :
            # and self.request.GET['service'] in context['services']
            context['selected'] = self.request.GET['service']
        else:
            context['selected'] = '-1'
        return context


class DockerServiceTabs(tabs.TabGroup):
    slug = "docker_tabs"
    tabs = (ServiceTab, ServiceMonitorTab,)
    sticky = True
