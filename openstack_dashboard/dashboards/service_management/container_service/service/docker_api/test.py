name_service = 'test'
networkID = '80l3i3wyan0dzpk6lh8m5elpz'
containers = [{
    'name':'con7_service',
    'image':'busybox:latest',
    'command':'/bin/sleep 100',
    'evn':["con1=1","test1=1"],
    'post':[8880,],
},
             {
    'name':'con8_service',
    'image':'busybox:latest',
    'command':'/bin/sleep 100',
    'evn':["con2=2","test2=2"],
    'post':[8881,],
             },
             {
    'name':'con9_service',
    'image':'busybox:latest',
    'command':'/bin/sleep 100',
    'evn':["con3=3","test3=3"],
    'post':[8882,]
             },]


from openstack_dashboard.dashboards.service_management.container_service.service.docker_api import docker_api

cli = docker_api.connect_docker()

nets = cli.networks()

#container = cli.create_container(name='ddtest', image='busybox:latest', command='/bin/sleep 30')
#cli.start(container)

def create_service():
    networks = cli.networks(ids=[networkID,])
    network = networks[0]
    network_name = network['Name']
    print (network_name)
    network_config = cli.create_networking_config({
        network_name: cli.create_endpoint_config()
    })
    for container in containers:

        container = cli.create_container(name=container['name'],
                             command=container['command'],
                             networking_config=network_config,
                             environment=container['evn'],
                             ports=container['post'],
                             image=container['image'])
        cli.start(container)
create_service()