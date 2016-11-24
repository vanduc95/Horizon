from docker import Client


def connect_docker():
    cli = Client(base_url='unix://var/run/docker.sock')
    return cli


def create_service(service_config):
    containers = service_config['containers']
    cli = connect_docker()
    networks = cli.networks(ids=[service_config['networkID'], ])
    network = networks[0]
    network_name = network['Name']
    network_config = cli.create_networking_config({
        network_name: cli.create_endpoint_config()
    })
    for container in containers:
        container = cli.create_container(name=container['name'],
                                         command=container['command'],
                                         networking_config=network_config,
                                         environment=container['environment'],
                                         ports=container['port'],
                                         image=container['image'])
        cli.start(container)

