from docker import Client
import docker

def scale(serviceID,numReplicas):
    cli = Client(base_url="unix://var/run/docker.sock")
    service = cli.inspect_service(serviceID)
    service_index = service['Version']['Index']
    replicas = service['Spec']['Mode']['Replicated']['Replicas']
    tasktamplate = service['Spec']['TaskTemplate']
    container = tasktamplate['ContainerSpec']

    taskObj = docker.types.TaskTemplate(container)

    if (numReplicas==None):
        try:
            cli.update_service(serviceID, service_index, task_template=taskObj,
                           mode={'Replicated': {'Replicas': replicas+1}})
            return True
        except Exception :
            return False
    else:
        try:
            cli.update_service(serviceID, service_index, task_template=taskObj,
                           mode={'Replicated': {'Replicas': numReplicas}})
            return True
        except Exception :
            return False


scale('2zqwp165g0vind77ij8hzg1jy',5)