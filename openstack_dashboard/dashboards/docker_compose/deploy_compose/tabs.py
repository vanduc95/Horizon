import time
from openstack_dashboard.dashboards.docker_compose.deploy_compose.docker_api import api as api_docker
from horizon import tabs
from openstack_dashboard.dashboards.docker_compose.deploy_compose.containers import tables as tbl_containers
from openstack_dashboard.dashboards.docker_compose.deploy_compose.services import tables as tbl_services


class Service:
    def __init__(self, serviceID, image, name, replicate):
        self.id = serviceID
        self.image = image
        self.name = name
        self.replicate = replicate



class Container:
    def __init__(self, containerId, image, command, created, state, name):
        self.id = containerId
        self.image = image
        self.command = command
        self.created = created
        self.state = state
        self.name = name
        # self.host_ip = host_ip


class ServiceTab(tabs.TableTab):
    name = tbl_services.ServiceTable.Meta.verbose_name
    slug = tbl_services.ServiceTable.Meta.name
    table_classes = (tbl_services.ServiceTable,)
    template_name = ("horizon/common/_detail_table.html")

    def get_services_data(self):
        # cli = Client(base_url='unix://var/run/docker.sock')
        # services = []
        # for service in cli.services():
        #     id = service['ID']
        #     image = service['Spec']['TaskTemplate']['ContainerSpec']['Image']
        #     name = service['Spec']['Name']
        #     replicate = service['Spec']['Mode']['Replicated']['Replicas']
        #     services.append(Service(id, image, name, replicate))
        # return services
        services = []
        return services


class ContainerTab(tabs.TableTab):
    name = tbl_containers.ContainersTable.Meta.verbose_name
    slug = tbl_containers.ContainersTable.Meta.name
    table_classes = (tbl_containers.ContainersTable,)
    template_name = ("horizon/common/_detail_table.html")

    # template_name = ("docker_swarm/docker_service/service_monitor/detail_service_monitor.html")
    # check_form = False

    def get_containers_data(self):
        containers = []

        dict_container = api_docker.getContainers()
        for ct in dict_container:
            # convert data
            created = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ct['Created']))
            name = ct['Names'][0][1:]
            containers.append(
                Container(ct['Id'][:12], ct['Image'], ct['Command'], created, ct['State'], name))
        return containers


class DeployComposeTabs(tabs.TabGroup):
    slug = "deploy_compose_tabs"
    tabs = (ServiceTab, ContainerTab,)
    sticky = True
