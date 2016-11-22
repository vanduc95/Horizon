/**
 * Created by huynhduc on 07/11/2016.
 */

var config = {
    minCPU: 0,
    maxCPU: 0,
    minRAM: 0,
    maxRAM: 0
};
var serviceID = '';
var currentStatus ={
    minCPU: 0,
    maxCPU: 0,
    minRAM: 0,
    maxRAM: 0
};
var scaleMode = {
    status: '',
    resource:''
};

var getDataInterval = {
    handle: undefined,
    isRunning: false
};

var delayInterval = {
    handle: undefined,
    isRunnig: false
};

function delayIntervalHandle(){
    delayInterval.isRunning = false;
    // clearInterval(delayInterval);
    delayInterval.handle = undefined;
    getDataInterval.isRunning = true;
    console.log('intervalling');
    getDataInterval.handle = setInterval(intervalHandleData,10000);
}

function intervalHandleData(){
    getDataCadvisor();
}

function requestScale(option){
    getDataInterval.isRunning = false;
    clearInterval(getDataInterval.handle);
    getDataInterval.handle = undefined;

    delayInterval.isRunnig = true;
    console.log('timeouting');
    delayInterval.handle = setTimeout(delayIntervalHandle,180000);

    url = $('.scale_container').data('request-scale-container-url')+'?option='+option+'&service_id='+serviceID;
    $.ajax({
            url: url,
            success: function (data) {
                if(data['result']==true){
                    console.log('scale success');
                }else if(data['result']==false){
                    console.log('scale error');
                }
            },
            error: function (e) {

            }
    });
}


var count =0;
function getDataCadvisor() {
    var url = $('.scale_container').data('usage-container-url')+'?service_id='+serviceID;
    var result = undefined;
    $.ajax({
        url: url,
        success: function (data) {
            var keys = [];
            console.log(data);
            for(var k in data) keys.push(k);
            var isBreak = false;
            for (var key=0;key<keys.length; key++){
                var content_container = data[keys[key]];
                // console.log(content_container);
                var time =content_container[0]['timestamp'];
                var firtTime = new Date(time);
                var firtCPUUsage = content_container[0].cpu;
                var firtRAMUsage = content_container[0].ram;
                for(var i=1;i<content_container.length;i++){
                    count +=1;
                    time =content_container[i]['timestamp'];
                    // console.log(content_container[i]);
                    var lastTime = new Date(time);
                    var lastCPUUsage = content_container[i].cpu;
                    var lastRAMUsage = content_container[i].ram;
                    var nanoInterval = 1000000*(lastTime - firtTime);
                    var cpuUsage = 100000*(lastCPUUsage - firtCPUUsage)/nanoInterval;
                    var ramUsage = 100000*(lastRAMUsage - firtRAMUsage)/nanoInterval;
                    firtTime = lastTime;
                    firtCPUUsage = lastCPUUsage;
                    firtRAMUsage = lastRAMUsage;
                    console.log(time+': cpu= '+cpuUsage+' ram='+ramUsage);
                    var check = checkScale(cpuUsage,ramUsage);
                    if (check){
                        isBreak = true;
                        console.log('111111111');
                        return;
                    }
                }
                if(isBreak){
                    console.log('222222222');
                    // return 0;
                }
            }
        },
        error: function (e) {
            $('#xxx').text('request is error');
        }
    });
}

function checkScale(cpu,ram) {
    if(scaleMode.status=='auto'){
        if(scaleMode.resource=='cpu'){
            if (config.maxCPU<cpu){
                requestScale('out');
                return true;
            }else if (config.minCPU>cpu){
                requestScale('in');
                return true;
            }
        }else if(scaleMode.resource=='ram'){
            if (config.maxRAM<ram){
                requestScale('out');
                return true;
            }else if (config.minRAM>ram){
                requestScale('in');
                return true;
            }
        }
    }
    return false;
}


function getCheckAutoScaling(){
    var url = $('.scale_container').data('mode-scale-container-url')+'?service_id='+ serviceID;
    $.ajax({
        url: url,
        success: function(data){
            console.log(data);
            if ("result" in data){

            }else{
                scaleMode.status = data['MODE'];
                scaleMode.resource = data['RESOURCE'];
                config.minCPU=data['CPU']['minCPU'];
                config.maxCPU=data['CPU']['maxCPU'];
                config.minRAM=data['RAM']['minRAM'];
                config.maxRAM=data['RAM']['maxRAM'];
                console.log(scaleMode.status+' '+scaleMode.resource);
                if (scaleMode.status == 'auto') {
                    console.log('vao day khong');
                    getDataInterval.isRunning = true;
                    getDataInterval.handle = setInterval(intervalHandleData, 10000);
                }
            }
        },
        error: function(){

        }
    })
}

// getCheckAutoScaling();

function clear(){
    config = {
        minCPU: 0,
        maxCPU: 0,
        minRAM: 0,
        maxRAM: 0
    };
    currentStatus ={
        minCPU: 0,
        maxCPU: 0,
        minRAM: 0,
        maxRAM: 0
    };
    scaleMode = {
        status: '',
        resource:''
    };
    if (delayInterval.isRunning === true){
        clearInterval(delayInterval.handle);
    }
    if (getDataInterval.isRunning === true){
        clearInterval(getDataInterval.handle);
    }
}

function init(){
    clear();
    serviceID = $('.scale_container').data('service-now');
    console.log(serviceID);
    if (serviceID !='-1') {
        getCheckAutoScaling();
    }
}
init();