
from docker import Client

def connect_docker():
    cli = Client(base_url='unix://var/run/docker.sock')
    return cli