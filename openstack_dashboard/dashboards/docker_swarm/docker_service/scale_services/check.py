# import requests
# import json
#
# from docker import Client
#
# cli = Client(base_url='tcp://127.0.0.1:2376')
# list_container = cli.containers()
# list_container_of_service = []
# for container in list_container:
#     if container['Labels'] and container['Labels']['com.docker.swarm.service.name']=='desperate_dubinsky':
#         list_container_of_service.append(container['Id'])
#
# response = requests.get('http://127.0.0.1:8080/api/v1.2/docker/')
# containers = response.json()
# result={}
# for container in containers:
#     if containers[container]['id'] in list_container_of_service:
#         stats = []
#         for status in containers[container]['stats']:
#             element_stats = {}
#             element_stats['timestamp'] =status['timestamp'][:19]
#             element_stats['cpu'] = status['cpu']
#             element_stats['ram'] = status['memory']
#             stats.append(element_stats)
#         result[containers[container]['id']]=stats