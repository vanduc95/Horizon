import os
from django.core.files import File
from openstack_dashboard.dashboards.log_management.log_views.log_file.log_obj import LogObj
from os import walk
from datetime import datetime


def handleFile(project,level,timeStart,timeEnd):
    context =[]
    if (timeStart=='' and timeEnd ==''):
        checkTime = False
        date_to = datetime.now()
        date_from = datetime.now()
    else:
        checkTime = True
        date_from = convertDatetimeObj(timeStart)
        date_to = convertDatetimeObj(timeEnd)
    project = project.lower()
    files = findFile()
    files_found = []
    for file in files:
        if (file.find(project)>=0):
            files_found.append(file)
    for file in files_found:
        context += readFile(checkTime,project,file,level,date_from,date_to)
    return context

def convertDatetimeObj(time_string):
    datetimeObj = datetime.strptime(time_string,'%Y-%m-%d %H:%M:%S')
    return datetimeObj


def findFile():
    filePath = os.path.dirname(os.path.abspath(__file__))
    files = None
    for filenames in walk(filePath+'/file_txt'):
        files = filenames[2]
    return files


def readFile(checkTime,project,file,level,date_from,date_to):
    context = []
    print(file)
    fileHandler = openFile(file,'r')
    if fileHandler['opened']:
        file = File(fileHandler['handler'])
        count =1
        for line in file:
            log_obj = createLogObj(checkTime,project,count,line,file,level,date_from,date_to)
            if (log_obj != None):
                context.append(log_obj)
            count +=1
        file.close()
    return context


def openFile(file,mode):
    file_name = '/file_txt/'+file
    filePath = os.path.dirname(os.path.abspath(__file__))
    try:
        fileHandler = open(filePath+file_name,mode)
        return {'opened':True,
                'handler':fileHandler}
    except Exception:
        return {'opened':False,
                'handler':None}


def createLogObj(checkTime,project,count,line,file,level,date_from,date_to):
    arr = line.split( )
    if (project!='keystone'):
        id = str(count) +':'+file.name
        project_temp = project.upper()
        level_temp = arr[3]
        if ((level_temp ==level)or(level == 'ALL')):
            dateTime = arr[0] + ' ' + arr[1][:8]
            datetimeObj = convertDatetimeObj(dateTime)
            if ((checkTime ==False) or ((datetimeObj >= date_from) and (datetimeObj <= date_to))):
                resource = arr[4]
                index_start_message = len(arr[0]) + len(arr[1]) + len(arr[2]) + len(arr[3]) + len(arr[4]) + 4
                message = line[index_start_message:]
                index = message.find('- - -]')
                if (index != -1):
                    message = message[(index+7):]
                log_obj = LogObj(id,dateTime,project_temp,level_temp,resource,message)
                return log_obj
            else:
                return None
        else:
            return None
    else:
        id = str(count) + ':' + file.name
        project_temp = project.upper()
        level_temp = arr[5]
        if ((level_temp == level) or (level == 'ALL')):
            dateTime = arr[0] + ' ' + arr[1][:8]
            datetimeObj = convertDatetimeObj(dateTime)
            if ((checkTime == False) or ((datetimeObj >= date_from) and (datetimeObj <= date_to))):
                resource = arr[6]
                index_start_message = len(arr[0]) + len(arr[1]) + len(arr[2]) + len(arr[3]) + len(arr[4]) + len(arr[5]) + len(arr[6]) + 6
                message = line[index_start_message:]
                index = message.find(']')
                if (index != -1):
                    message = message[(index + 2):]
                log_obj = LogObj(id, dateTime, project_temp, level_temp, resource, message)
                return log_obj
            else:
                return None
        else:
            return None

def removeLine(index,filePath):
    filePath = os.path.join(filePath)
    line_index = index
    print(filePath)
    print(line_index)
    file = open(filePath, "r")
    lines = file.readlines()
    file.close()

    file_reopen = open(filePath, "w")
    count = 1
    for line in lines:
        if (count != line_index):
            file_reopen.write(line)
        count += 1
    file_reopen.close()

# removeLine(1,'/home/huynhduc/Github/OLP-Horizon/openstack_dashboard/dashboards/log_management/log_views/log_file/file_txt/neutron-server.txt')
