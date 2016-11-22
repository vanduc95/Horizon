from docker import Client


def init(ip='local'):
    if ip == 'local':
        return Client(base_url='unix://var/run/docker.sock')
    else:
        return Client(base_url='tcp://' + ip + ':2376')


def getContainers(ip='local'):
    cli = init(ip)
    try:
        return cli.containers(all=True)
    except:
        print 'Error!'

