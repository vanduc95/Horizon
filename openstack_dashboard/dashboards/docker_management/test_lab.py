from docker import Client
cli = Client(base_url='unix://var/run/docker.sock')
images= cli.images()
for image in images:
    pass