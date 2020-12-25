import os,time,re
from flask import jsonify,session
from flask_restful import Resource,Api
import requests,subprocess
from flask import (
    Blueprint, request
)
from app.aps_scheduler import get_host,monitor_cmd_script001,monitor_cmd_script002,monitor_tmp_script001,monitor_tmp_script002
from .Httpauth  import authtoken ,serializer,Interface_authority #Interface_authority初始化验证接口权限函数
from apscheduler.schedulers.background import BackgroundScheduler#定时任务
from app.aps_scheduler import schedulerdate, Url01,Url02

Pressure_monitor = Blueprint('Pressure_monitor',__name__,url_prefix='/Pressure_monitor')
api = Api(Pressure_monitor) #初始化restfulapi


#获取项目对应的机器列表，并根据ip获取premethus监控值

class GetiplistView(Resource):
    def post(self):
        data = request.get_json(force=True)
        project_type = data.get('project_type')
        env_type = data.get('env_type')

        def get_ip():
            url = get_host
            data = {'serviceName':project_type,'env':env_type}
            valuelist = requests.get(url,params=data).json()['data']
            print(valuelist)
            ipdict = {}
            for i in valuelist:
                ip = i.get('ip')
                hostname = i.get('machineName')
                # iphost = hostname + ':' + ip
                ipdict[hostname] = ip
            print(ipdict)
            return ipdict
        getip = get_ip() #执行获取ip列表字典

        j_data = {'msg': '获取主机列表成功', 'statusCode': 200, 'data':getip}
        return jsonify(j_data)

api.add_resource(GetiplistView, '/Getiplist')


#根据ip列表获取对应的监控指标
class GetmonitorvalueView(Resource):
    def post(self):
        data = request.get_json(force=True)
        project_type = data.get('project_type')
        env_type = data.get('env_type')
        def get_ip():
            url = get_host
            data = {'serviceName':project_type,'env':env_type}
            valuelist = requests.get(url,params=data).json()['data']
            iplist = []

            for i in valuelist:
                ip = i.get('ip')
                iplist.append(ip)
            print(iplist)
            return iplist

        def get_monitor_value():
            iplist = get_ip()
            cpuvalue = []
            for ip in iplist:
                url01 = 'http://10.55.144.29:9090/api/v1/query'
                data01 = {'query':"""(100 - (avg by(instance) (irate(node_cpu_seconds_total{instance="%s:9100", mode="idle"}[5m])) * 100)) * on(instance) group_right(address) (node_uname_info)""" % ip}
                value = requests.get(url01, params=data01)
                result = round(float(value.json().get('data').get('result')[0].get('value')[1]))   #获取过滤cpu使用值和转化使用率，四舍五入
                print(result)
                cpuvalue.append(result)
            return cpuvalue

        j_data = {'msg': '获取主机cpu使用值成功', 'statusCode': 200, 'data':get_monitor_value()}
        return jsonify(j_data)

api.add_resource(GetmonitorvalueView, '/Getmonitorvalue')


#执行压测命令 web服务器执行

class CommandexecutionView(Resource):
    def post(self):
        data = request.get_json(force=True)
        project_type = data.get('project_type')
        env_type = data.get('env_type')
        iphone = data.get('iphone')
        sjml = data.get('sjml')
        scriptname = str(data.get('scriptname'))
        scripttype = str(data.get('scripttype')) #判断执行类型 命令不一样的

        class Commandexecution:
            def __init__(self,project_type,env_type):
                self.project_type = project_type
                self.env_type = env_type

               

            def get_ip(self):
                url = get_host
                if self.env_type == '0':
                   self.env_type = 'test'
                   data = {'serviceName': self.project_type, 'env': self.env_type}
                   valuelist = requests.get(url, params=data).json()['data']
                   print(valuelist)
                   return valuelist
                if self.env_type == '1':
                    self.env_type = 'pre'
                    data = {'serviceName': self.project_type, 'env': self.env_type}
                    valuelist = requests.get(url, params=data).json()['data']
                    print(valuelist)
                    return valuelist
                if self.env_type == '2':
                    self.env_type = 'prod'
                    data = {'serviceName': self.project_type, 'env': self.env_type}
                    valuelist = requests.get(url, params=data).json()['data']
                    print(valuelist)
                    return valuelist
                

            #执行服务逻辑脚本
            def cmdexecut001(self):
                iplist = self.get_ip()
                print(iplist)
                try:
                    for i in iplist:
                        ip = i.get('ip')
                        hostname = i.get('machineName')
                        scriptnames = scriptname
                        command = 'python3 ' + str(scriptnames) + '  -n ' + str(project_type) + ' -i ' + str(ip) + ' -e ' + str(iphone) \
                                  + ' -s ' + str(sjml)  + ' -m ' + str(hostname)
                        print(command)
                        cmd= subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
                        out = cmd.stdout.readlines()
                        print(out)
                        return 'ok'
                except Exception as e:
                    print('有错误',e)
                    return '{e}'.format(e = e)
            #执行业务业务逻辑脚本
            def cmdexecut002(self):
                iplist = self.get_ip()
                print(iplist)
                try:
                    for i in iplist:
                        ip = i.get('ip')
    
                        hostname = i.get('machineName')
                        scriptnames = scriptname
                    
                        command = 'python3 ' + str(scriptnames) + '  -n ' + str(project_type)  + ' -e ' + str(iphone) \
                                  + ' -s ' + str(sjml)
                        cmd= subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
                        out = cmd.stdout.readlines()
                        print(out)
                        return 'ok'
                except Exception as e:
                    print('有错误哦',e)
                    return '{e}'.format(e = e)
        #判断服务脚本是否执行成功并返回前端
        if scripttype == '8':
            getiplist = Commandexecution(project_type,env_type).cmdexecut001()
            if getiplist == 'ok':
                j_data = {'msg': '业务脚本执行成功', 'statusCode': 200}
                return jsonify(j_data)
            else:
                j_data = {'msg': '业务脚本执行失败', 'statusCode': 500,'error':getiplist}
                return jsonify(j_data)

        elif scripttype == '9':
            getiplist = Commandexecution(project_type,env_type).cmdexecut002()
            if getiplist == 'ok':
               j_data = {'msg': '逻辑脚本执行成功', 'statusCode': 200}
               return jsonify(j_data)
            else:
               j_data = {'msg': '业务脚本执行失败', 'statusCode': 500, 'error': getiplist}
               return jsonify(j_data)



api.add_resource(CommandexecutionView, '/Commandexecution')


#根据脚本进程判断脚本是否执行完毕，0为完毕，非0为执行中

class CheckcompleteView(Resource):
    def post(self):
        #获取前端传入脚本名称
        data = request.get_json(force=True)
        scriptname = data.get('scriptname')
        print('d',scriptname)
        #拼接检查进程是否存在的命令

        cmd = "ps -ef|grep {processname}|grep -v grep|wc -l".format(processname=scriptname)
        command = os.system(cmd)
        print(type(command),command)
        if command == 0:
           status = '0'
           j_data = {'msg': '进程状态', 'statusCode': 200, 'status': status}
           return jsonify(j_data)
        else:
            status = '1'
            j_data = {'msg': '进程状态', 'statusCode': 200, 'status': status}
            return jsonify(j_data)
api.add_resource(CheckcompleteView, '/Checkcomplete')

#监控管理项目生成脚本

class GeneratingscriptsView(Resource):
    def post(self):
        data = request.get_json(force=True)
        username = str(data.get('username')) #获取用户名
        type_id = str(data.get('type_id')) #判断生成那种脚本
        login_id = str(data.get('loginid')) #判断登陆接口是否点击

        project_type = data.get('project_type')
        env_type = data.get('env_type')

        one_node = str(data.get('one_node'))
        two_node = str(data.get('two_node'))
        three_node = str(data.get('three_node'))
        four_node = str(data.get('four_node'))
        sjml = str(data.get('sjml'))


        sclist = data.get('sclist')
        sclist_str = "{sclist}".format(sclist = sclist)
        takeparameters = data.get('takeparameters')

        login_data = str(data.get('login_data'))
        login_url = str(data.get('login_url'))
        statusCode = str(data.get('statusCode'))
        statusCode_value = str(data.get('statusCode_value'))
        
        #获取黑框参数
        def check_hc(k):
            if '\n' in k:
                k = k.replace('\n', '\n' + ' '*4)
            return k
        takeparameters_list = []
        for i in sclist:
            kk1 =  i.get('takeparameters')
            k = check_hc(kk1)
            kk2 = i.get('takeparameters01')
            k2 = check_hc(kk2)
            kk3 = i.get('takeparameters02')
            k3 = check_hc(kk3)
            takeparameters_list.append(k)
            takeparameters_list.append(k2)
            takeparameters_list.append(k3)
        takeparameters = takeparameters_list[0]
        takeparameters01 = takeparameters_list[1]
        takeparameters02 = takeparameters_list[2]
        
        print(takeparameters_list)


       #获取用户名
        #username = session.get('username')
        #username = str(username)
        username = username.split('@')[0]  # 去除邮箱后缀

        if '.' in username:
            username = username.replace('.', '')  # 匹配有.的用户名
        print(username)
        
        class Script_generated:
            def __init__(self):
                # 文件生成并替换脚本相关内容
                date = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
                self.file001 = open(monitor_tmp_script001,'r').read()  # 业务脚本模版
                self.file002 = open(monitor_tmp_script002,'r').read()  # 逻辑脚本模版
                self.filename = monitor_cmd_script001.format(date=date, username=username)
                self.nf = open(self.filename, 'w+')

            #根据模版生成业务脚本
            def scritp001(self):
                #替换模版内容
                change_file = self.file001.replace('onenode', one_node).replace('twonode',two_node) \
                    .replace('threenode',three_node).replace('fournode',four_node) \
                    .replace('parametersclist', sclist_str) \
                    .replace('loginid',login_id) \
                    .replace('logindata', login_data).replace('urllogin', login_url) \
                    .replace('statusCode', statusCode).replace('Codevalue', statusCode_value) \
                    .replace('takeparameters1', takeparameters).replace('takeparameters2',takeparameters01).replace('takeparameters3',takeparameters02)
                self.nf.write(change_file)
                self.nf.close()
                return self.filename


            #根据模版生成逻辑脚本
            def scritp002(self):
                # 根据模版生成业务脚本
                    change_file = self.file002.replace('onenode', one_node).replace('twonode', two_node) \
                        .replace('threenode', three_node).replace('fournode', four_node) \
                        .replace('sjml',sjml) \
                        .replace('parametersclist', sclist_str) \
                        .replace('loginid', login_id) \
                        .replace('logindata', login_data).replace('urllogin', login_url) \
                        .replace('statusCode', statusCode).replace('Codevalue', statusCode_value) \
                        .replace('takeparameters1', takeparameters).replace('takeparameters2',takeparameters01).replace('takeparameters3',takeparameters02)
                    self.nf.write(change_file)
                    self.nf.close()
                    return self.filename


        if type_id == '8':
            script001 = Script_generated().scritp001()
            j_data = {"msg": '业务脚本生成成功', "statusCode": 200, 'data': {"filename": script001}}
            return jsonify(j_data)
        elif type_id == '9':
            script002 = Script_generated().scritp002()

            j_data = {"msg": '逻辑脚本生成成功', "statusCode": 200, 'data': {"filename": script002}}
            return jsonify(j_data)


api.add_resource(GeneratingscriptsView, '/Generatingscripts')



#监控项目前段传入黑框框内容后，生成最终执行脚本
class Generatingscripts01View(Resource):
    def post(self):
        data = request.get_json(force=True)

        username = data.get('username')
        if '.' in username:
            username = username.replace('.', '')  # 匹配有.的用户名
        print(username)
        
        date = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())

        filename = monitor_cmd_script002.format(username=username,date=date)
        scriptslog = '/mnt/datalogs/datalogs-{username}-monitorscripts-implement-{date}.py.log'.format(username=username,date=date)
        filecontent = data.get('fileconnect')
        print(filecontent)

        with open(filename, 'w') as f:
            f.writelines(filecontent)
        j_data = {"msg": '执行脚本最终生成成功', "statusCode": 200}
        return jsonify(j_data)


api.add_resource(Generatingscripts01View, '/Generatingscripts01')



#定时任务， 采用APScheduler模块，支持类型date(特定时间仅运行一次作业时使用)，interval(固定的时间间隔运行作业时使用), cron(在一天的特定时间定期运行作业时使用)
class ScheduledTasksView(Resource):
    # decorators = [authtoken.login_required]
    # method_decorators = [Interface_authority]
    def post(self):
        request_data = request.get_json(force=True)
        Timingtype =  request_data['Timingtype']  # 定时的三种类型分别传入不同值

        scriptname = request_data['scriptname']
        project_type = request_data['project_type']
        env_type_one = request_data['env_type']
        iphone = request_data['iphone']
        sjml = request_data['sjml']
        scripttype = request_data['scripttype']
        print('envtype',env_type_one)
        #转化env_type
        def get_env_type(env_type):
            if env_type == '0':
                env_type = 'test'
                return env_type
            if env_type == '1':
                env_type = 'pre'
                return env_type
            if env_type == '2':
                env_type = 'prod'
                return env_type
        #获去本次env值
        env_type = get_env_type(env_type_one)
        #env_type = 'prod'
        print('kk',env_type)

        class get_cmdscripts:
            def __init__(self,project_type,env_type,scriptname,iphone,sjml):
                self.project_type = project_type
                self.env_type = env_type
                self.scriptname = scriptname
                self.iphone = iphone
                self.sjml = sjml

            def get_ip(self):  # 根据项目名称获取对应ip列表
                url = get_host
                data = {'serviceName': self.project_type, 'env': self.env_type}
                valuelist = requests.get(url, params=data).json()['data']
                print(valuelist)
                return valuelist

            #获取业务逻辑脚本执行命令行
            def cmdexecut001(self):
                iplist = self.get_ip()
                print(iplist)
                cmd = []
                for i in iplist:
                    ip = i.get('ip')
                    hostname = i.get('machineName')

                    command = 'python3 ' + str(self.scriptname) + '  -n ' + str(self.project_type) + ' -i ' + str(ip) + ' -e ' + str(self.iphone) \
                              + ' -s ' + str(self.sjml)  + ' -m ' + str(hostname)
                    print(command)
                    cmd.append(command)
                return cmd

            #获取服务逻辑脚本执行命令
            def cmdexcut002(self):
                iplist = self.get_ip()
                cmd = []
                for i in iplist:
                    ip = i.get('ip')
                    command = 'python3 ' + str(self.scriptname) + '  -n ' + str(self.project_type) +  ' -e ' + str(self.iphone) \
                              + ' -s ' + str(self.sjml)
                    print(command)
                    cmd.append(command)
                return cmd


        def ssh(command):
            cmd = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            out = cmd.stdout.readlines()
            print(out)


        #定义定时任务类
        class Timing_date: #date 类型的定时任务
            def add_job_date(self,Datetime,job_id,cmd): #新增job
                    schedulerdate.add_job(ssh, 'date', run_date=Datetime, id=job_id,args=[cmd])
                    get_jobs = schedulerdate.get_jobs()
                    print('addgetjobs',get_jobs)

            def add_job_interval(self,Intervaltime,job_id,cmd):
                schedulerdate.add_job(ssh, 'interval', seconds=Intervaltime, id=job_id,args=[cmd])
                get_jobs = schedulerdate.get_jobs()
                print(get_jobs)

            def get_jobs(self): #获取job列表
                jobs = schedulerdate.get_jobs()
                return (jobs)


            def remove_job(self,jobid): # 删除指定job
                schedulerdate.remove_job(jobid)

            def remove_all_jobs(self): #删除所有job
                schedulerdate.remove_all_jobs()


        #根据服务逻辑的脚本添加定时任务
        if scripttype == '8' and Timingtype == 'add_date':
            #获取执行命令行
            print('看看',project_type,env_type,scriptname,iphone,sjml)

            cmdlist = get_cmdscripts(project_type,env_type,scriptname,iphone,sjml).cmdexecut001()
            cmd = cmdlist[0]

            Datetime = request_data['Datetime']  # date类型传入的时间参数值
            s = schedulerdate.state
            job_id = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time())) #已时间为jobid
            job_cmd = Timing_date().add_job_date(Datetime,job_id,cmd) #添加队列
            time.sleep(3)
            s = schedulerdate.state
            if s  == 0: schedulerdate.start()
            print('date 类型计划任务')
            j_date = {'msg':'date类任务已添加','statusCode':200}
            return jsonify(j_date)

        if scripttype == '8' and Timingtype == 'add_interval':
            cmdlist = get_cmdscripts(project_type, env_type, scriptname, iphone, sjml).cmdexecut001()
            cmd = cmdlist[0]

            Intervaltime = int(request_data['Intervaltime'])
            job_id = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
            job_cmd = Timing_date().add_job_interval(Intervaltime, job_id, cmd)

            print('interval类型计划任务')
            j_date = {'msg':'interval类任务已添加','statusCode':200, 'Jobid':job_id}
            return jsonify(j_date)



        #根据业务逻辑的脚本添加定时任务
        if scripttype == '9' and Timingtype == 'add_date':
            #获取执行命令行
            cmdlist = get_cmdscripts(project_type, env_type, scriptname, iphone, sjml).cmdexcut002()
            cmd = cmdlist[0]

            Datetime = request_data['Datetime']  # date类型传入的时间参数值
            s = schedulerdate.state
            job_id = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time())) #已时间为jobid
            job_cmd = Timing_date().add_job_date(Datetime,job_id,cmd) #添加队列
            time.sleep(3)
            s = schedulerdate.state
            if s  == 0: schedulerdate.start()
            print('date 类型计划任务')
            j_date = {'msg':'date类任务已添加','statusCode':200}
            return jsonify(j_date)

        if scripttype == '9' and Timingtype == 'add_interval':
            cmdlist = get_cmdscripts(project_type, env_type, scriptname, iphone, sjml).cmdexcut002()
            cmd = cmdlist[0]

            Intervaltime = int(request_data['Intervaltime'])
            job_id = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
            job_cmd = Timing_date().add_job_interval(Intervaltime, job_id, cmd)

            print('interval类型计划任务')
            j_date = {'msg':'interval类任务已添加','statusCode':200, 'Jobid':job_id}
            return jsonify(j_date)



        #删除定时队列
        if  Timingtype == 'remove_job':
            Jobid = request_data['Jobid']
            Timing_date().remove_job(Jobid)
            j_date = {'msg': 'job已删除', 'statusCode': 200}
            return jsonify(j_date)
        #删除所有定时
        if  Timingtype == 'remove_all':
            Timing_date().remove_all_jobs()
            j_date = {'msg': 'job已清空', 'statusCode': 200}
            return jsonify(j_date)
        #获取任务id
        if  Timingtype == 'get_jobs':
            s = schedulerdate.state
            get_jobs = Timing_date().get_jobs()
            len_get_jobs = len(get_jobs)
            print(type(get_jobs),'type')
            if len_get_jobs == 0:
                print('JOB为空')
                j_data = {'msg': 'job队列为空', 'statusCode': 200,}
                return jsonify(j_data)

            strgetjobs = str(get_jobs).strip('\"[').strip(']').replace('\'[','').replace(']\'','').split(',')
            all_jobsid = []
            for i in strgetjobs:
                i = str(re.findall(r'\d{4}-\d{1,2}-\d{1,2}-\d{1,2}-\d{1,2}-\d{1,2}',i)).strip("[").strip("]")
                i = i.strip("'")
                all_jobsid.append(i)
            print(all_jobsid)

            data = {
                "taskidlist": all_jobsid
            }

            print(data)
            r = requests.post(Url02, json=data)
            rdate = r.json()
            j_date = {'msg': '返回任务id', 'statusCode': 200,'jobsid':rdate}
            return jsonify(j_date)
        else:
            print('参数异常')

api.add_resource(ScheduledTasksView,'/ScheduledTasks')
