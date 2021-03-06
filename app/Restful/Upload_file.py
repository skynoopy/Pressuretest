import os,time,paramiko
from flask import Flask, flash, request, redirect, url_for,render_template,send_from_directory,make_response,Blueprint,jsonify,g,session
from werkzeug.utils import secure_filename
from pypinyin import lazy_pinyin
from flask_restful import Resource,Api

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort



RestfulFile = Blueprint('RestfulFile',__name__,url_prefix='/RestfulFile')
api = Api(RestfulFile) #初始化restfulapi


ALLOWED_EXTENSIONS = {'txt','png','jpg','pptx','docx'}  #允许上传文件格式


#上传文件接口
class UploadView(Resource):
        def post(self):


            # 检查文件后缀是否在允许的格式
            def allowed_file(filename):
                return '.' in filename and \
                       filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

            try:
                file = request.files['Filename']
                filename = file.filename
                pd = filename.rsplit('.', 1)[1]
                if "\"" in pd:
                   filename = filename.strip('\"')


                if file and allowed_file(filename):

                    #对中文文件名转成拼音
                    name = filename.split('.')[0]
                    ext = filename.split('.')[1]
                    new_filename = ''.join(lazy_pinyin(name)) + '.' + ext
                    # print(new_filename)
                    basepath = '/data/soft/Quality_Platform/scripts/uploads'
                    upload_path = os.path.join(basepath, secure_filename(new_filename))
                    file.save(upload_path)
                    txt_count = len(open(upload_path, 'rU').readlines()) #统计文件行数
                    session['filename'] = filename
                    session['txt_count'] = txt_count
                    print('文件上传成功')


                    j_data = {
                        'msg':'文件上传成功',
                        'statusCode': 200

                    }
                    return jsonify(j_data)

                else:
                    print('上传文件格式不对')
                    j_data = {
                        'msg':'上传格式不支持',
                        'statusCode': 200
                    }
                    return jsonify(j_data)
            except Exception as e:
                    print(e)
                    j_data = {
                        'msg': '文件上传失败',
                        'statusCode': 500
                    }
                    return jsonify(j_data)

api.add_resource(UploadView, '/Upload')


class kkView(Resource):
    def get(self):
        print(session.get('filename'))
        # print('kk')
api.add_resource(kkView, '/kk')


#下载文件接口
class DownloadView(Resource):

    def get(self):
        path = request.base_url
        file = request.get_json()
        filename = file.get('Filename')
        print(path,filename)
        # filename = request.get_data()
        directory = '/data/soft/Quality_Platform/scripts/uploads'
        response = make_response(send_from_directory(directory, filename, as_attachment=True))
        response.headers["Content-Disposition"] = "attachment; filename={}".format(filename.encode().decode('latin-1'))
        return response

api.add_resource(DownloadView, '/Download/')







#生成脚本接口
class UploadScriptGenerationView(Resource):

    def get(self):
        return '上传脚本生成接口!'

    def post(self):
        data = request.get_json(force=True)
        type = data['type']
        typeid = data['typeid']  #判断是否上传文件标识
        hostip = data["hostip"]
        hostpath = data["hostpath"]
        parameter = session.get('filename')
        count_parameter = str(session.get('txt_count'))
        print(type,hostip,hostpath,parameter,count_parameter)


        #获取用户名
        username = session.get('username')
        username = str(username)
        username = username.split('@')[0]  # 去除邮箱后缀

        if '.' in username:
            username = username.replace('.', '')  # 匹配有.的用户名
        print('check',username)




        #文件生成
        date = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        file = open('/data/soft/Quality_Platform/scripts/template/upload_implement_template.py','r').read()      #执行脚本模版
        filename = '{username}-upload-implement-{date}.py'.format(date=date, username=username)
        implement_new_file = '/data/soft/Quality_Platform/scripts/fulllinkscripts/' + filename #新生成的执行脚本名称
        nf = open(implement_new_file,'w+')

        change_file = file.replace('hostip',hostip).replace('hostpath',hostpath).replace('filenum',count_parameter) \
            .replace('filename',parameter).replace('typeid',typeid)
        nf.write(change_file)
        nf.close()


        # 上传生成脚本和参数文件到压测机
        upload_file = '/data/soft/Quality_Platform/scripts/fulllinkscripts/{upload_filename}'.format(upload_filename = parameter)  #用户上传的参数文件，本地文件路径
        put_upload_file = '/data/Qa_Quality/upload_file/{upload_filename}'.format(upload_filename = parameter) #要上传到压测服务器的参数文件,压测机的文件路径
        put_file = "/data/Qa_Quality/scripts/" + filename #要上传到压测服务器的执行文件


        def ssh1(ip,username,password):
            try:
                transport = paramiko.Transport((ip, 9922))
                transport.connect(username=username, password=password)
                sftp = paramiko.SFTPClient.from_transport(transport)
                ssh = paramiko.SSHClient()
                ssh._transport = transport
                sftp.put(upload_file,put_upload_file)   #上传参数文件
                sftp.put(implement_new_file, put_file)            #上传执行文件
                stdin, stdout, stderr = ssh.exec_command(
                    "chmod a+x {put_file}".format(put_file=put_file))
                print('2')
                transport.close()
            except Exception as e:
                    error = "上传脚本失败,请检查！"
                    print('上传脚本失败',e)
                    j_data = {
                        "msg": error,
                        "statusCode": 500
                    }
                    return jsonify(j_data)
        ssh1('10.55.142.248','root','fudao@123456')

        j_data = {
            "msg": '脚本上传成功',
            "statusCode": 200,
            'data': {
                "filename": filename
            }

        }
        return jsonify(j_data)
api.add_resource(UploadScriptGenerationView, '/UploadScriptGeneration')


#全链路生成脚本接口，用户输入前半部分内容不包括代码输入部分，生成半成品脚本返回前端
class ScriptGenerationView(Resource):
    def get(self):
        return '全链路脚本生成接口!'

    def post(self):
        #获取传入参数
        data = request.get_json(force=True)
        typeid = data.get('typeid')
        uploadid = data.get('uploadid') #是否上传文件
        txtcount = str(data.get('txt_count')) #上传文件行数
        uploadfilename = data.get('uploadfilename') #上传文件名
        login_data = str(data.get('login_data'))
        login_url = data.get('login_url')
        statusCode = data.get('statusCode')
        statusCode_value = data.get('statusCode_value')


        sclist = data.get('sclist')
        sclist = "{sclist}".format(sclist = sclist)
        takeparameters = data.get('takeparameters')
        inputparameter = data.get('inputparameter')

        print(takeparameters)


        def make_scripts():
            #获取用户名
            username = session.get('username')
            username = str(username)
            username = username.split('@')[0]  # 去除邮箱后缀

            if '.' in username:
                username = username.replace('.', '')  # 匹配有.的用户名
            print(username)

            # 文件生成并替换脚本相关内容
            date = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
            file = open('/data/soft/Quality_Platform/scripts/template/upload_script_temple.py', 'r').read()  # 执行脚本模版
            filename = '{username}-fulllinkscripts-implement-{date}.py'.format(date=date, username=username)
            fulllink_implement_new_file = '/data/soft/Quality_Platform/scripts/fulllinkscripts/' + filename  # 新生成的执行脚本名称
            nf = open(fulllink_implement_new_file, 'w+')
            #以typeid判断是否点击登录按钮，分别对应不同的内容替换方案

            if typeid == '1': #没有点击登录按钮
                print('没点登录的')
                change_file = file.replace('typeid', typeid).replace('parametersclist',sclist).replace('uploadid','1') \
                .replace('statusCode',statusCode).replace('statusvalue',statusCode_value)
                nf.write(change_file)  # 将替换完的内容写入文件
                nf.close()
                

            if typeid == '2': #点击登录按钮
                print('点击登录了')
            
                if uploadid == '2': #如果点击登录接口，并且已经上传文件
                   print('点击登录并上传')
                   change_file1 = file.replace('typeid', typeid).replace('parametersclist',sclist) \
                   .replace('logindata',login_data).replace('loginurl',login_url).replace('uploadid','2').replace('txtcount',txtcount)\
                   .replace('uploadfilename',uploadfilename).replace('statusCode',statusCode) \
                        .replace('statusvalue',statusCode_value)
                   nf.write(change_file1)  #将替换完的内容写入文件
                   nf.close()
                   
                   
                #点击登录了，但是没上传
                if uploadid == '1':
                     print('点击登录但没上传')
                     change_file2 = file.replace('typeid', typeid).replace('parametersclist', sclist) \
                     .replace('logindata', login_data).replace('loginurl', login_url).replace('uploadid','1') \
                        .replace('statusCode', statusCode).replace('statusvalue', statusCode_value)

                     nf.write(change_file2)  #将替换完的内容写入文件
                     nf.close()

            with open(fulllink_implement_new_file,'r') as f:
                 fread = f.readlines()
            #os.remove(fulllink_implement_new_file)
            error = "OK"
            return error,fread  # 上传成功，把文件名也返回

        status = make_scripts()    #根据函数返回判断执行成功或失败，成功即把文件名也返回

        #判断是否成功分别返回前端数据
        if status[0] == 'OK':
            j_data = { "msg": '脚本生成成功', "statusCode": 200,'data': {"fileconnect":status[1]}}
            return jsonify(j_data)

api.add_resource(ScriptGenerationView, '/ScriptGeneration')



#前端返回用户输入代码，写入脚本文件，生成最终执行文件
class UploadScriptView(Resource):
    def post(self):
        data = request.get_json(force=True)

        #获取用户名
        username = data.get('username')
        
        if '.' in username:
            username = username.replace('.', '')  # 匹配有.的用户名
        print(username)
        date = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        scriptsname = '{username}-fulllinkscripts-implement-{date}.py'.format(username=username,date=date)
        filename = '/data/soft/Quality_Platform/scripts/fulllinkscripts/{scriptsname}'.format(scriptsname=scriptsname)
        scriptslog = '/mnt/fulllinklogs/datalogs/test_environmen/datalogs-' + scriptsname +'.log'
        put_file = "/data/Qa_Quality/scripts/{scriptsname}".format(scriptsname=scriptsname) # 要上传到压测服务器的指定路径
        filecontent = data.get('filecontent')
        with open(filename, 'w') as f:
            f.writelines(filecontent)


        # 上传生成脚本和参数文件到压测机

        # 上传服务器
        def ssh1(ip, username, password):
            try:
                transport = paramiko.Transport((ip, 9922))
                transport.connect(username=username, password=password)
                sftp = paramiko.SFTPClient.from_transport(transport)
                ssh = paramiko.SSHClient()
                ssh._transport = transport
                print(filename,put_file)
                sftp.put(filename, put_file)  # 上传生成文件到服务器指定目录
                stdin, stdout, stderr = ssh.exec_command(
                    "chmod a+x {put_file}".format(put_file=put_file))
                transport.close()
                msg = "ok"
                return msg

            except  Exception as e:
                msg = "error"
                print('上传脚本失败', e)
                return msg

        status = ssh1('10.55.142.248', 'root', 'fudao@123456')
        print(status)
        if status == 'error':
            j_data = {'msg': '执行脚本上传失败', 'statusCode': 500}
            return jsonify(j_data)
        if status == 'ok':
            j_data = {'msg':'执行脚本上传成功','data': {"scriptsname":scriptsname,'scriptslog':scriptslog}, 'statusCode': 200}
            return jsonify(j_data)

api.add_resource(UploadScriptView, '/UploadScript')


#获取zabbix监控性能监控

class PerformancemonitoringView(Resource):
    def post(self):
        data = request.get_json(force=True)
        hostip = data.get('hostip')
        io = ('/usr/bin/zabbix_get' + ' ' + '-s' + ' {hostip} ' + ' -k ' + '\"system.cpu.load[percpu,avg1]\"').format(hostip = hostip)
        mem  = ('/usr/bin/zabbix_get' + ' ' + '-s' + ' {hostip} ' + ' -k ' + '\"vm.memory.size[pused]\"').format(
            hostip=hostip)
        command = io + ';' +mem

        print(command)
        #zabbix服务区执行监控命令
        def ssh1(ip,username,password):
            try:
                transport = paramiko.Transport((ip, 9922))
                transport.connect(username=username, password=password)
                sftp = paramiko.SFTPClient.from_transport(transport)
                ssh = paramiko.SSHClient()
                ssh._transport = transport
                stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)  # 支持多条命令拼接

                # line = stdout.readlines()
                linelist = []
                for line in stdout:
                     print(line)

                     linelist.append(line)

                transport.close()
                zio = linelist[0].strip()
                zmem = linelist[1].strip()
                print(zio,zmem)

                return zio,zmem



            except  Exception as e:
                    error = "error"
                    print('上传脚本失败',e)
                    return error

                    # j_data = {
                    #     "msg": error,
                    #     "statusCode": 200
                    # }
                    # return jsonify(j_data)
        k = ssh1('192.168.2.33','zabbixmonitor','fudao@123456')
        zio = int(float(k[0]))
        zmem = int(float(k[1]))



        j_data = {"msg": "返回性能监控指标", "statusCode": 200, "data": {"io": zio, "mem": zmem}}
        print(j_data)
        return jsonify(j_data)


api.add_resource(PerformancemonitoringView, '/Performancemonitoring')




#根据负载杀进程
class killprocessView(Resource):
    def post(self):
        data = request.get_json(force=True)
        # hostip = data.get('hostip')
        hosturl = data.get('hosturl')
        prt = '\'{print $2}\''
        cmd = 'nslookup {hosturl}|grep Address|tail -n1|awk {print}'.format(hosturl = hosturl,print = prt) #url转义成ip地址
        hostip  = os.popen(cmd).read()
        print(hostip)









        io = ('/usr/bin/zabbix_get' + ' ' + '-s' + ' {hostip} ' + ' -k ' + '\"system.cpu.load[percpu,avg1]\"').format(hostip = hostip)
        mem  = ('/usr/bin/zabbix_get' + ' ' + '-s' + ' {hostip} ' + ' -k ' + '\"vm.memory.size[pused]\"').format(
            hostip=hostip)
        command = io + ';' +mem

        print(command)
        #zabbix服务区执行监控命令
        def ssh1(ip,username,password):
            try:
                transport = paramiko.Transport((ip, 9922))
                transport.connect(username=username, password=password)
                sftp = paramiko.SFTPClient.from_transport(transport)
                ssh = paramiko.SSHClient()
                ssh._transport = transport
                stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)  # 支持多条命令拼接

                # line = stdout.readlines()
                linelist = []
                for line in stdout:
                     print(line)

                     linelist.append(line)

                transport.close()
                zio = linelist[0].strip()
                zmem = linelist[1].strip()
                print(zio,zmem)

                return zio,zmem

            except  Exception as e:
                    error = "error"
                    print('上传脚本失败',e)
                    return error

                    # j_data = {
                    #     "msg": error,
                    #     "statusCode": 200
                    # }
                    # return jsonify(j_data)
        k = ssh1('192.168.2.33','zabbixmonitor','fudao@123456')
        zio = int(float(k[0]))
        zmem = int(float(k[1]))


        if zio or zmem >= 80:   #判断被压测主机负载是否过高，将把压测命令杀掉
            print('进入查杀阶段')
            try:
                cmd = '/usr/bin/python3.7 /data/soft/Qa_quality/scripts/killallprocess.py'
                print(cmd)

                def ssh(ip, username, password, cmd):
                    try:
                        transport = paramiko.Transport((ip, 9922))
                        transport.connect(username=username, password=password)
                        ssh = paramiko.SSHClient()
                        ssh._transport = transport
                        stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)  # 支持多条命令拼接
                        print('执行了')

                        line = stdout.readline()
                        print(line)
                    except Exception as e:
                        print(e)

                ssh('10.55.142.248', 'root', 'fudao@123456', cmd)
            except Exception as e:
                print('查杀进程失败')

                j_data = {'msg':'进程查杀失败','statusCode': 500}
                return jsonify(j_data)

            j_data = {'msg': '进程查杀成功', 'statusCode': 200}
            return jsonify(j_data)

        j_data = {'msg': '没有达到查杀阈值', 'statusCode': 200}
        return jsonify(j_data)


api.add_resource(killprocessView, '/killprocess')







class DescribeulbView(Resource):
    def post(self):

        import hashlib
        import urllib
        from urllib.parse import urlparse
        from urllib.parse import urlencode
        import requests
        import threading
        import sqlite3
        import json

        def _verfy_ac(param, publickey, private):
            pp = dict(param, **publickey)
            # print(pp)
            items = list(pp.items())
            items.sort()
            # # 将参数串排序
            params_data = "";
            httpurl = "";
            transfered = "";
            transfer = "";
            # header = 'https://api.ucloud.cn/?'
            for key, value in items:
                params_data = params_data + str(key) + str(value)
                # print(params_data)
                if str(key) == 'PublicKey':
                    transfer = {str(key): str(value)}
                    # print(transfer)

                    continue
                else:
                    transfered = urlencode(transfer)
                    httpurl = httpurl + str(key) + '=' + str(value) + '&'

            params_data = params_data + private

            sign = hashlib.sha1()
            sign.update(params_data.encode("utf8"))
            signature = sign.hexdigest()
            # print(signature)
            # httpurl = header + httpurl + transfered +  '&Signature=' + signature
            httpurl = httpurl + transfered + '&Signature=' + signature
            # print (signature)
            # print(httpurl)
            return httpurl


        requestulb = {
            "Action": "DescribeULB",
            "ProjectId": "org-sjdken",
            "Region": "cn-bj2",
            # "Limit": 2,
            # "Offset": 0

        }

        # 公钥
        publickey = {'PublicKey': 'd+OjKD0rgaqxZWwaa9Nev4pQeAlhsiht4B9EgYDBGn5IbmvN'}
        # #私钥
        private = 'd186ba62dad44a55ee8e4da1a873c51aee64737e'
        http_url = 'https://api.ucloud.cn/?'
        ulb_url = _verfy_ac(requestulb, publickey, private)



        r = requests.get(url=http_url, params=ulb_url)
        rt = dict(r.json())
        rdata = rt.get('DataSet')
        # print(rdata)

        #获取前端传入参数
        data = request.get_json(force=True)
        hosturl = data.get('hosturl')
        prt = '\'{print $2}\''
        cmd = 'nslookup {hosturl}|grep Address|tail -n1|awk {print}'.format(hosturl=hosturl, print=prt)  # url转义成ip地址
        domainip = os.popen(cmd).read().strip()  #获取域名解析后的ip


        ipdic = {}  #定义空字典
        for i in rdata:
            iplist = []
            ip1 = i.get('PrivateIP') #ulb地址
            ipdic[ip1] = iplist            #ip1为字典key值，空列表为value值

            for ii in i.get('VServerSet'):
                BackendSet = ii.get('BackendSet')
                for iii in BackendSet:
                    ip2 = iii.get('PrivateIP') #ulb绑定的实际ip地址
                    iplist.append(ip2)   #赋予value具体值，在此处为ulb挂在的实际ip地址


        ipkeys = ipdic.keys()
        def iplist(): #如果解析的域名ip在ulb列表中,获取绑定的serverip
            if domainip in ipkeys:
                # print('ok', ipdic.get(ip))
                serversip = ipdic.get(domainip)
                return serversip
        hosts = iplist()
        ulbhost = list(set(hosts))
        print(ulbhost)

        linelist = []  # servers监控值都会放到此列表
        for hostip in ulbhost:
            print(hostip)
            io = ('/usr/bin/zabbix_get' + ' ' + '-s' + ' {hostip} ' + ' -k ' + '\"system.cpu.load[percpu,avg1]\"').format(hostip=hostip) #cpu 1分钟负载
            mem = ('/usr/bin/zabbix_get' + ' ' + '-s' + ' {hostip} ' + ' -k ' + '\"vm.memory.size[pavailable]\"').format(hostip=hostip) #可用内存
            command = io + ';' + mem

            # zabbix服务区执行监控命令
            def ssh1(ip, username, password):
                try:
                    transport = paramiko.Transport((ip, 9922))
                    transport.connect(username=username, password=password)
                    sftp = paramiko.SFTPClient.from_transport(transport)
                    ssh = paramiko.SSHClient()
                    ssh._transport = transport
                    stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)  # 支持多条命令拼接

                    # line = stdout.readlines()
                    for line in stdout:  #获取监控之输出结果
                        print(line.strip())
                        line = int(float(line.strip()))
                        linelist.append(line)


                    transport.close()
                    # global zio,zmem
                    # zio = int(float(linelist[0].strip()))
                    # zmem = int(float(linelist[1].strip()))
                    # print('cpu:',zio, '内存:',zmem)

                    # return zio, zmem
                except  Exception as e:
                    error = "error"
                    print('上传脚本失败', e)
                    return error

            ssh1('192.168.2.33', 'zabbixmonitor', 'fudao@123456')

            print(linelist)
            value_status = len([*filter(lambda x: x >=80,linelist)]) > 0   #判断列表中是否有大于50的元素
            print(value_status)




            #查杀阶段
            if value_status:  # 判断被压测主机负载是否超过50%，将把压测命令杀掉
                    print('进入查杀阶段')

                    try:
                        cmd = '/usr/bin/python3.7 /data/soft/Qa_quality/scripts/killallprocess.py'
                        print(cmd)
                        def ssh(ip, username, password, cmd):
                            try:
                                transport = paramiko.Transport((ip, 9922))
                                transport.connect(username=username, password=password)
                                ssh = paramiko.SSHClient()
                                ssh._transport = transport
                                stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)  # 支持多条命令拼接
                                print('执行了')

                                line = stdout.readline()
                                print(line)
                            except Exception as e:
                                print(e)

                        ssh('10.55.142.248', 'root', 'fudao@123456', cmd)
                    except Exception as e:
                        print('查杀进程失败')

                        j_data = {'msg': '进程查杀失败', 'statusCode': 500}
                        return jsonify(j_data)

                    j_data = {'msg': '进程查杀成功', 'statusCode': 200}
                    return jsonify(j_data)

            j_data = {'msg': '没有达到查杀阈值', 'statusCode': 200}
            return jsonify(j_data)









        # j_data = {'msg':ipdic}
        # return jsonify(j_data)

        # conn = sqlite3.connect('/Users/gz0101000646/flaskk/instance/pages.db')
        # c = conn.cursor()
        #
        #
        # def create_uhost():
        #     for i in range(1, 2):
        #         r = requests.get(url=http_url, params=ulb_url)
        #         #
        #         r_tag = json.loads(r.text)
        #         #r_tag = {"RetCode":0,"Action":"CreateUHostInstanceResponse","UHostIds":["uhost-m0cbnaaq"],"IPs":["192.168.11.46"]}
        #
        #         print (type(r_tag))
        #
        #         r_tag_value = r_tag['RetCode']
        #         print(r_tag_value)
        #
        #         #提交api返回值入库
        #         stus = c.execute(
        #
        #             "insert  into create_host  (r_tag_value) values ('%d')" %(r_tag_value)
        #         )
        #         conn.commit()
        #
        # kk = create_uhost()
        #
        #
        # def creat_uhost_num(num):  #多线程创建主机
        #
        #     threads = []
        #     for i in range(1, num + 1):
        #         t1 = threading.Thread(target=create_uhost())
        #         threads.append(t1)
        #
        #     for t in threads:
        #         t.start()
        #
        #
        # @bp.route('/create_effective/', methods=['POST','GET'])
        # def create_effective():
        #
        #
        #
        #     recv_data = request.get_data()
        #     print(recv_data)
        #
        #     #传递需要创建主机数量 默认创建一台
        #     creat_uhost_num(1)
        #
        #     #获取api 值
        #     tag_value = c.execute(
        #
        #         'select r_tag_value from create_host order by id desc limit 1'
        #     ).fetchone()[0]
        #     print(tag_value)
        #
        #
        #
        # #     #获取Api返回值，如果返回0 则将返回成功信息给js，否则异然
        #     if tag_value != 0:
        #        tag = 1
        #        tag_s = json.dumps(tag)
        #        return  tag_s
        #     else:
        #        tag = 0
        #        tag_s = json.dumps(tag)
        #        return tag_s
        #
        #
        #
        #
        #
        #
        #
        #


api.add_resource(DescribeulbView, '/describeulb')


#根据脚本进程判断脚本是否执行完毕，0为完毕，非0为执行中

class CheckcompleteView(Resource):
    def post(self):
        #获取前端传入脚本名称
        data = request.get_json(force=True)
        scriptname = data.get('scriptname')
        print(scriptname)

        #拼接检查进程是否存在的命令

        statuslist=[]
        for namescript in  scriptname:
            command = 'python  /data/soft/Qa_quality/scripts/judgment_process.py' + ' ' + '{namescript}'.format(namescript=namescript)

            def ssh(ip, username, password):
                try:
                    transport = paramiko.Transport((ip, 9922))
                    transport.connect(username=username, password=password)
                    ssh = paramiko.SSHClient()
                    ssh._transport = transport
                    stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)  # 支持多条命令拼接
                    print('检查进程')
                    line = stdout.readline()
                    line = int(line.strip())
                    statuslist.append(line)
                    return line
                except Exception as e:
                    print(e)
            cmd = ssh('10.55.142.248', 'root', 'fudao@123456')
        print(statuslist)
        if any(statuslist) == False:
           status = '0'
           j_data = {'msg': '进程状态', 'statusCode': 200, 'status': status}
           return jsonify(j_data)
        else:
            status = '1'
            j_data = {'msg': '进程状态', 'statusCode': 200, 'status': status}
            return jsonify(j_data)

        


api.add_resource(CheckcompleteView, '/Checkcomplete')








# 全链路分析日志检测是否存在，如存在则备份
class ChecklogexsitsView(Resource):
    def post(self):
        data = request.get_json(force=True)
        username = data.get('username')
        print(username)
        log_file = '/mnt/fulllinklogs/datalogs/test_environmen/datalogs-' + username + '.log'

        try:
            status = os.path.isfile(log_file)
            print(status)
            if status == False:
                j_data = {'msg': '无日志文件，无需重命名！', 'statusCode': 200}
                return jsonify(j_data)
            if status == True:
                date = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
                new_log_file = '/mnt/fulllinklogs/datalogs/test_environmen/datalogs-' + username + '-' + date + '.log'
                os.rename(log_file, new_log_file)
                j_data = {'msg': '日志文件已经重命名', 'statusCode': 200}
                return jsonify(j_data)

        except Exception as e:
            print(e)
            j_data = {'msg': '日志文件检测失败', 'statusCode': 200}
            return jsonify(j_data)


api.add_resource(ChecklogexsitsView, '/Checklogexsits')
