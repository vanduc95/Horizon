


# from django.http.response import HttpResponse
from docker import Client
import docker


def scale(serviceID,numReplicas,option=None):
    cli = Client(base_url="unix://var/run/docker.sock")
    service = cli.inspect_service(serviceID)
    service_name = service['Spec']['Name']
    service_index = service['Version']['Index']
    replicas = service['Spec']['Mode']['Replicated']['Replicas']
    tasktamplate = service['Spec']['TaskTemplate']
    container = tasktamplate['ContainerSpec']

    taskObj = docker.types.TaskTemplate(container)

    if (numReplicas==None):
        num = replicas
        if option=='out':
            num +=1
        else:
            num -=1
        if num >= 1:
            try:
                cli.update_service(serviceID, service_index, task_template=taskObj,name=service_name,
                               mode={'Replicated': {'Replicas': num}})
                return True
            except Exception :
                return False
    else:
        try:
            cli.update_service(serviceID, service_index, task_template=taskObj,name=service_name,
                           mode={'Replicated': {'Replicas': numReplicas}})
            return True
        except Exception :
            return False


