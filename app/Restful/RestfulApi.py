from flask import (flash, request, session, jsonify,Blueprint,g)
from werkzeug.security import check_password_hash,generate_password_hash #验证密码hash
from app.db_mysql import User,ReportLog
from app.exts import db
import glob, os,requests,ast
import paramiko, subprocess,threading,time  #远程执行命令
from apscheduler.schedulers.background import BackgroundScheduler #定时任务
import datetime,re
from flask_restful import Resource,Api  #restful api
from .Httpauth  import authtoken ,serializer,Interface_authority #Interface_authority初始化验证接口权限函数
from app.aps_scheduler import schedulerdate,Url01,Url02,except_log   #定时任务



RestfulApi = Blueprint('RestfulApi',__name__,url_prefix='/RestfulApi')
api = Api(RestfulApi) #初始化restfulapi



class test(Resource):
    decorators = [ authtoken.login_required ]
    method_decorators = [Interface_authority]
    # @Interface_authority

    def post(self):
        print('test post')
        j_data = {
            'msg':'test post',
            'code': 200
        }
        return jsonify(j_data)
    def get(self):
        print('test get')
        j_data = {
            'msg': 'test get',
            'code': 200
        }
        return jsonify(j_data)

api.add_resource(test,'/test')



#注册接口
class RegisterView(Resource):
    def get(self):

        print(request.method)
        return '注册接口!'

    def post(self):
        data = request.get_json()
        username = data['username']
        password = data['password']
        error = None
        print(username, password)

        if not username:  # 判断是否为空，是否已经注册
            error = '请输入用户名.'
        elif not password:
            error = '请输入密码.'

        elif User.query.filter_by(username=username).first() is not None:
             error = '此用户已被注册，请重新添加用户.'.format(username)

        if error is None:  # 验证成功 插入数据库新用户信息, 不直接存密码生成密码哈希存入
            user = User(username=username, password=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()

            j_data = {
                "msg": error,
                "statusCode": 200
            }
            return jsonify(j_data)
            # return redirect(url_for('auth.login'))
        flash(error)

        j_data = {
            "msg": error,
            "statusCode": 400
        }
        return jsonify(j_data)
api.add_resource(RegisterView,'/Register')




#登录接口
class LoginView(Resource):
    def get(self):
        return '登录接口!'
    def post(self):
        data = request.get_json(force=True)
        username = data['username']
        password = data['password']
        error = None
        print(username, password)

        #查询注册用户存入变量备用
        user = User.query.filter_by(username=username).first()
        role = user.role

        if user is None:
            error = '用户名不正确请重新输入.'
        elif not check_password_hash(user.password,password): #比对哈希密码值
            error = '密码不正确请重新输入.'

        # def generate_auth_token(uid, expiration=7200):
        #     serializer = Serializer(KEY_TOKEN.SECRET_KEY, expires_in=expiration)
        #     token = serializer.dumps({"uid": uid})
        #     return token
        #
        # def get_token():
        #     expiration = KEY_TOKEN.EXPIRATION
        #     token = generate_auth_token(uid, expiration)
        #     return token



        if error is None:
           session.clear()
           uid = user.id

           session['username'] = data['username']
           session['user_id'] = uid  #存入用户id
           session.permanent = True
           print(session.get('username'),session.get('user_id'))


           def make_token(us):    # 以用户名生成token
               token = serializer.dumps({'username':us})
               return token

           user = str(user).split(':')[1]  #sqlalchemy查询出的user 为User:bsk格式，需要过滤下
           g.current_user = user
           token = bytes.decode(make_token(user))

           print(g.current_user)

           j_data = {
               "msg": '登录成功',
               "statusCode": 200,
               "data" : {
                   "uid": uid,
                   "role": role,
                   # "token": get_token().decode("ascii"),
                   "token": token,
               }
           }
           return jsonify(j_data)
        flash(error)
        j_data = {
            "msg": error,
            "statusCode": 400,
        }
        return jsonify(j_data)
api.add_resource(LoginView,'/Login')




# 接token 返回用户权限
class GetPermission(Resource):
    def get(self):
        return '接token返回用户权限!'
    def post(self):
        data = request.get_json()
        token = data['token']
        if token:
            roles = ["admin"]
            msg = "获取成功"
            j_data = {
                "data":{"roles" : roles},
                "msg": msg,
                "statusCode": 200,
            }
        else:
            msg = "获取失败"
            j_data = {
                "msg": msg,
                "statusCode": 404,
            }

        return jsonify(j_data)
api.add_resource(GetPermission,'/getpermission')






#生成脚本接口
class ScriptGenerationView(Resource):
    decorators = [ authtoken.login_required ]  #引用token验证 固定格式
    method_decorators = [Interface_authority]
    def get(self):
        return '脚本生成接口!'

    def post(self):
        data = request.get_json(force=True)
        type = data['type']
        username = data['userName']
        hostip = data["hostip"]
        hostpath = data["hostpath"]
        parameter = data["parameter"]
        parameter = str(parameter)
        parameter = eval(parameter)
        parameter = str(parameter)
        #excelog = data["excete_log"]
        print(type,hostip,hostpath,parameter)


        def type_post():
            # 本机测试脚本路径
            file = glob.glob('/data/soft/Quality_Platform/scripts/template/qa-post-test.py')
            # 定义自动生成脚本函数
            for one_polling in file:
                date = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
                new_file = "/data/soft/Quality_Platform/scripts/singlescripts/{username}-qa-test-{date}.py".format(date=date,username=username)
                filename = '{username}-qa-test-{date}.py'.format(date=date,username=username)
                put_file = "/home/wenba/xz/automation/snail/scripts/" + "{username}-qa-test-{date}.py".format(date=date,username=username)
                print('脚本生成',new_file)

                f1 = open(new_file, 'w+')
                f = open(one_polling, 'r+')
                all_lines = f.readlines()
                f.seek(0)
                for line in all_lines:
                    line = line.replace('hostip', hostip)
                    line = line.replace('hostpath', hostpath)
                    line = line.replace('customcs', parameter)
                    f1.write(line)
                f.close()
                f1.close()
                cf = str(os.path.exists(new_file))
                df = os.path.getsize(new_file)
                try:
                    if (cf == 'True' and df > 0):
                        cg = "200"
                        print(cg)
                        # 上传生成脚本
                    def ssh1(ip,username,password,file):
                        try:
                            transport = paramiko.Transport((ip, 9922))
                            transport.connect(username=username, password=password)
                            sftp = paramiko.SFTPClient.from_transport(transport)
                            ssh = paramiko.SSHClient()
                            ssh._transport = transport
                            sftp.put(file,put_file)
                            stdin, stdout, stderr = ssh.exec_command(
                                "chmod a+x {put_file}".format(put_file=put_file))
                            transport.close()
                        except:
                                error = "上传脚本失败,请检查！"
                                print('上传脚本失败')
                                j_data = {
                                    "msg": error,
                                    "statusCode": 200
                                }
                                return jsonify(j_data)
                    ssh1('10.55.142.248','root','fudao@123456',new_file)

                    #操作成功日志存库
                    excelog['operation_result'] = 1
                    except_log().putlog(excelog)
                    return filename



                except:
                    print('脚本执行失败，请检查.')

                    # 操作失败日志存库
                    excelog['operation_result'] = 2
                    except_log().putlog(excelog)
                    error = '脚本生成失败,请检查!'
                    return '500'


        if type == 'POST' or 'post':  #判断请求类型执行对应的函数
           print(type)
           status = type_post()
           if status != '500':

                j_data = {
                     "msg": 'post脚本生成成功',
                     "statusCode": 200,
                     'data':{
                         "filename": status
                     }

                }

                return jsonify(j_data)
           elif status == '500':
               j_data = {
                   "msg": 'post脚本生成失败',
                   "statusCode": 500,

               }
               return jsonify(j_data)
        else:
            print(type)
            # status = type_get()
            # if status != '500':
            j_data = {
                 "msg": '请求类型不对',
                 "statusCode": 200,


            }
            return jsonify(j_data)
            # elif status == '500':
            #     j_data = {
            #         "msg": 'get脚本生成失败',
            #         "code": 500,
            #
            #     }
            #     return jsonify(j_data)



api.add_resource(ScriptGenerationView, '/ScriptGeneration')





#执行命令接口
class ImplementView(Resource):
    decorators = [ authtoken.login_required ]
    method_decorators = [ Interface_authority ]
    def get(self):
        return '脚本执行接口!'

    def post(self):
        data = request.get_json(force=True)
        Filename = data["Filename"]
        Concurrent = data['Concurrent']
        Dx = data['Dx']
        Xz = data['Xz']
        Ip = data['Ip']
        print(Filename,Concurrent,Xz,Ip)

        command = 'cd /home/wenba/xz/automation/snail' + ';' + 'python run.py' + '  -f' + ' ' + str(
            Filename) + ' -c' + ' ' + str(Concurrent) + ' ' + str(Dx) + ' ' + str(Xz) + ' -i' + ' ' + str(Ip)
        print(command)

        user_file_log = '/data/soft/Quality_Platform/logs/{filename}.log'.format(filename=Filename)


        #远程执行压测命令
        def ssh2(ip, username, password, cmd):
            try:
                transport = paramiko.Transport((ip, 9922))
                transport.connect(username=username, password=password)
                ssh = paramiko.SSHClient()
                ssh._transport = transport
                stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)  # 支持多条命令拼接
                Results_log = open(user_file_log, 'w+',encoding='utf-8')
                print(user_file_log)

                while True:
                    line = stdout.readline()
                    print(line, file=open(user_file_log, 'w+', encoding='utf-8'))
                    print(line)
                    Results_log.write(line)
                    # Results_list.append(line)
                    if not line:
                       Results_log.close()
                       global cg
                       cg = '200'
                       break

                transport.close()

            except:
                print('执行命令失败，请检查.')
                error = '脚本生成失败,请检查!'
                j_data = {
                    "msg": error,
                    "statusCode": 500,

                }
                return jsonify(j_data)


        def ssh():
            ssh2('10.55.142.248', 'root', 'fudao@123456', command)

        scheduler = BackgroundScheduler()
        scheduler.add_job(ssh, 'date')
        scheduler.start()
        print('任务加入成功.')


        j_data = {
            "msg": '脚本执行成功.',
            "statusCode": 200,
            "data": {
                'logname': user_file_log,
                'time': Xz

            }
        }


        time.sleep(3)
        return jsonify(j_data)

api.add_resource(ImplementView, '/Implement')






#批量执行命令

class BatchExecutionView(Resource):
        decorators = [authtoken.login_required]
        method_decorators = [Interface_authority]
        def get(self):
            print('批量执行命令接口')

        def post(self):
            #获取前端数据对象组
            print('1')
            data = request.get_json(force=True)
            Mail = data['Mail']
            data = data['data']
            def get_parameter():
                try:
                    wc = int(len(data))
                    command_list = []
                    for i in range(wc):
                        dd = data[i]
                        treename = str(dd['Treename']).replace('>','/') #格式过滤
                        command = 'cd /home/wenba/xz/automation/snail' + ';' + 'python run.py' + '  -f' + ' ' + str(
                            dd['Filename']) + ' -c' + ' ' + str(dd['Concurrent']) + ' ' + str(dd['Dx']) + ' ' + str(dd['Xz']) + ' -i' + ' ' + str(dd['Ip']) + ' -u' + ' ' + Mail \
                           + ' -a '  + str(dd['Uid']) + ' -b ' + str(dd['Tree_id']) + ' -e '  + treename
                        command_list.append(command)
                        print('查看命令',command)
                    return command_list
                except Exception as e:
                    print(e)
                    error = '500'
                    return error
            status1 = get_parameter()
            if status1 == '500':
                j_data = {'msg': '批量命令生成失败请检查参数.','statusCode': 500, 'status':200}
                return jsonify(j_data)



            #paramiko远程执行
            def ssh2(ip, username, password, cmd,filename):
                try:
                    uid = cmd.split()[14]
                    tree_id = cmd.split()[16]
                    treename = cmd.split()[18]
                    transport = paramiko.Transport((ip, 9922))
                    transport.connect(username=username, password=password)
                    ssh = paramiko.SSHClient()
                    ssh._transport = transport
                    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)  # 支持多条命令拼接
                    print('执行了')

                    #日志存放骚操作
                    batch_log = '/data/soft/Quality_Platform/logs/{Filename}.log'.format(Filename=filename)
                    Results_log = open(batch_log, 'w+', encoding='utf-8')
                    while True:
                        line = stdout.readline()
                        #line = line.replace('\x00','')
                        print(line, file=open(batch_log, 'w+', encoding='utf-8'))
                        print(line)
                        Results_log.write(line)

                        if not line:
                            Results_log.close()
                            break
                    # 操作成功并失败上传日志存库
                    operation_content = '执行脚本完毕:' + treename
                    operation_result = 1
                    except_log().putlog(tree_id, uid, operation_content, operation_result, 2)
                    print('远程命令执行完毕')
              

                except  Exception as e:
                    #操作失败并失败上传日志存库
                    operation_content = '执行脚本失败:' + treename
                    operation_result = 2
                    except_log().putlog(tree_id, uid, operation_content, operation_result, 2)
                    print('远程命令执行失败.', e)
                    error = '500'
                    print('远程命令执行失败')


                transport.close()

            #多线程调取执行
            def ssh():
                try:
                    command_list = get_parameter()
                    print(len(command_list))
                    print(command_list)

                    threadlist = []
                    for cmd in command_list:
                        if cmd:
                            filename = cmd.split()[4]
                            threadcmd = threading.Thread(target=ssh2,args=('10.55.142.248','root','fudao@123456',cmd,filename))
                            threadlist.append(threadcmd)


                    print(threadlist)
                    for t in threadlist:
                        t.setDaemon(True)
                        t.start()
                        time.sleep(2)
                    t.join()                      #阻赛主线程，等待所有子线程结束才终止主线程
                    print('多线程队列全部执行完毕')
                    global  error
                    error = 200

                except Exception as e:
                    print(e)
                    error = 500
                    j_data = {
                        'msg': '批量脚本执行失败.',
                        'statusCode': 500
                    }
                    return jsonify(j_data)


            scheduler = BackgroundScheduler()
            scheduler.add_job(ssh, 'date')
            scheduler.start()
            print('批量任务加入成功.')

            j_data = {
                'msg': '批量脚本执行成功.',
                'statusCode': 200,

            }
            time.sleep(3)
            return jsonify(j_data)


api.add_resource(BatchExecutionView,'/BatchExecution')



#批量返回实时日志接口
class BatchRealtimeLogView(Resource):
      def post(self):
          # 获取前端数据对象组,获取脚本名称
          def get_scriptname():
              scriptsname_list = []
              data = request.get_json(force=True)
              data = data['data']
              # print(data)
              for i in data:
                  scriptname = i['scriptname']
                  # print(scritname)
                  scriptsname_list.append(scriptname)
              return scriptsname_list
          get_scriptname()

          def get_scriptlog(scriptname): #获取脚本对应的日志数据
              batch_log = '/data/soft/Quality_Platform/logs/{scriptname}.log'.format(scriptname=scriptname)
              print(batch_log)
              f = open(batch_log)
              lines = f.read().strip().replace('\00x','').strip('\u001b')
              print(lines)
              #lines = f.readlines()
              #lines = [line.strip().strip('\u001b').replace('[','') for line in lines]  # 列表生成试替换换行和其他特殊符号
              #lines = list(filter(None,lines))
              #str_lines = str(lines)
              #lines = str_lines.lstrip('[').rstrip(']').strip('\'A')
              t_lines = lines.startswith('总') #判断开头是否为指定字符
              print(lines,t_lines)
              if t_lines:  #开头为指定字符正常返回实时日志，如果开头不是指定字符则返回判断字符
                  lines =  { "logname":str(scriptname), "logconet":str(lines)}
                  return  lines

          def result_log(): #将循环结果放入列表并返回前端
              scriptsname = get_scriptname()
              result_list=[]
              for scriptname in scriptsname:
                  lines = get_scriptlog(scriptname)
                  if lines:
                     result_list.append(lines)
              print(result_list)


              if result_list:
                  j_data = {
                      'msg': '实时数据返回',
                      'statusCode': 200,
                      'data': {
                          'resultlog': result_list
                      }
                  }

                  return (j_data)
              else:

                  j_data = {
                      'msg': '实时数据返回完毕',
                      'statusCode': 200,
                      'data': {
                          'resultlog':'null',
                      }
                  }
                  return (j_data)

          j_data = result_log()
          return jsonify(j_data)



api.add_resource(BatchRealtimeLogView, '/BatchRealtimeLog')



#批量返回日志结果接口
class BatchLogView(Resource):
      def post(self):
          # 获取前端数据对象组,获取脚本名称
          def get_scriptname():
              data = request.get_json(force=True)
              data = data['data']
              scriptname = []
              for i in data:
                  i = i['scriptname']
                  scriptname.append(i)
              print('scriptname',scriptname)
              return scriptname
          #get_scriptname()

          def get_scriptlog(scriptname): #拿脚本名称查询日志结果
              batch_log = '/data/soft/Quality_Platform/logs/{scriptname}.log'.format(scriptname=scriptname)
              print(batch_log)
              f = open(batch_log)
              lines = f.readlines()
              lines = [line.strip().strip('\u001b') for line in lines]  # 列表生成试替换换行和其他特殊符号
              lines = list(filter(None, lines)) #去空
              lines = lines[-8:]
             
              #reportlog = ReportLog(tree_id=9, tree_name='updatetree', report_name='relosg',report_info=str(lines),uid=3)
              #db.session.add(reportlog)
              #db.session.commit()
              
              print(lines)
              return lines



          scriptname = get_scriptname() #获取脚本名称
          print(scriptname)
          
          data_list = []
          for sname in  scriptname: #循环脚本名称去获取 日志结果
              lines = get_scriptlog(sname)
              data = {
                  'logname': sname,
                  'resultlog': lines
              }
              print(data)
              data_list.append(data)
          j_data = {'msg':'请求日记成功','statusCode':200, 'data': data_list }
          return jsonify(j_data)
api.add_resource(BatchLogView,'/BatchLog')

#实时日志返回接口
class RealtimeLog(Resource):
    def post(self):
        # 获取前端数据对象组,获取脚本名称
        def get_scriptname():
            scriptsname_list = []
            data = request.get_json(force=True)
            data = data['data']
            # print(data)
            for i in data:
                scriptname = i['scriptname']
                # print(scritname)
                scriptsname_list.append(scriptname)
            return scriptsname_list

        get_scriptname()

        def get_scriptlog(scriptname):  # 获取脚本对应的日志数据
            batch_log = '/data/soft/Quality_Platform/logs/{scriptname}.log'.format(scriptname=scriptname)
            print(batch_log)
            f = open(batch_log)
            lines = f.readlines()
            lines = [line.strip().strip('\u001b').replace('[', '') for line in lines]  # 列表生成试替换换行和其他特殊符号
            lines = list(filter(None, lines))
            str_lines = str(lines)
            lines = str_lines.lstrip('[').rstrip(']').strip('\'A')
            t_lines = lines.startswith('总')  # 判断开头是否为指定字符
            print(lines, t_lines)
            if t_lines:  # 开头为指定字符正常返回实时日志，如果开头不是指定字符则返回判断字符
                lines = {"logname": str(scriptname), "logconet": str(lines)}
                return lines


        def result_log():  # 将循环结果放入列表并返回前端
            scriptsname = get_scriptname()
            result_list = []
            for scriptname in scriptsname:
                lines = get_scriptlog(scriptname)
                if lines:
                    result_list.append(lines)
            print(result_list)

            if result_list:
                #     print(result_list)
                #     kvlist = []
                #     for data in result_list:
                #         for key,value in data.items():
                #             print(key,value)
                #             kvlist.extend([key,value])
                #
                #
                #         print(kvlist)
                j_data = {
                    'msg': '实时数据返回',
                    'statusCode': 200,
                    'data': {
                        'resultlog': result_list
                    }
                }

                return (j_data)
            else:
                j_data = {
                    'msg': '实时数据返回完毕',
                    'statusCode': 200,
                    'data': {
                        'resultlog': 'null',
                    }
                }
                return (j_data)

        j_data = result_log()
        return jsonify(j_data)
api.add_resource(RealtimeLog,'/RealtimeLog')


#定时任务， 采用APScheduler模块，支持类型date(特定时间仅运行一次作业时使用)，interval(固定的时间间隔运行作业时使用), cron(在一天的特定时间定期运行作业时使用)
class ScheduledTasksView(Resource):
    # decorators = [authtoken.login_required]
    method_decorators = [Interface_authority]
    def post(self):
        request_data = request.get_json(force=True)
        Timingtype =  request_data['Timingtype']  # 定时的三种类型分别传入不同值


        def command_aggre(): #返回命令列表
            Mail = request_data['Mail']
            count = len(data)
            command_list = []
            for loop in range(count):
                parameter = data[loop]  #data[0]
                print('dd',parameter)
                Filename = parameter['Filename']
                Concurrent = parameter['Concurrent']
                Dx = parameter['Dx']
                Xz = parameter['Xz']
                Ip = parameter['Ip']
                Treename = parameter['Treename']
                command = 'cd /home/wenba/xz/automation/snail' + ';' + 'python run.py' + '  -f' + ' ' + str(
                    Filename) + ' -c' + ' ' + str(Concurrent) + ' ' + str(Dx) + ' ' + str(Xz) + ' -i' + ' ' + str(Ip) + ' -u' + ' ' + str(Mail) + ':' + str(Treename)
                command_list.append(command)  #生成的命令存入列表
            print(command_list)
            return (command_list)



        def ssh2(ip, username, password, cmd,filename):
            try:
                transport = paramiko.Transport((ip, 9922))
                transport.connect(username=username, password=password)
                ssh = paramiko.SSHClient()
                ssh._transport = transport
                stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)  # 支持多条命令拼接
                print('执行了')

                scheduled_log = '/mnt/fulllinklogs/scheduledlogs/scheduled_{filename}.log'.format(filename=filename)
                Results_log = open(scheduled_log, 'w+', encoding='utf-8')

                while True:
                    line = stdout.readline()
                    print(line, file=open(scheduled_log, 'w+', encoding='utf-8'))
                    print(line)
                    Results_log.write(line)

                    if not line:
                        Results_log.close()
                        break

            except  Exception as e:
                print('命令执行失败.',e)
            transport.close()

        def ssh(cmd):
            ssh2('10.55.142.248', 'root', 'fudao@123456', cmd, cmd[4])

        # def ssh():
        #     ssh2('10.55.142.248', 'root', 'fudao@123456', command)
        #
        # def myjob():
        #     print('myjob:', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

        #定义日期类job

        #if schedulerdate.state == 0: schedulerdate.start()

        class Timing_date: #date 类型的定时任务


            def add_job_date(self,Datetime,job_id,cmd): #新增job
                    schedulerdate.add_job(ssh, 'date', run_date=Datetime, id=job_id,args=[cmd])
                    get_jobs = schedulerdate.get_jobs()
                    print(get_jobs)

            def add_job_interval(self,Intervaltime,job_id,cmd):
                schedulerdate.add_job(ssh, 'interval', seconds=Intervaltime, id=job_id,args=[cmd])
                get_jobs = schedulerdate.get_jobs()
                print(get_jobs)


            def get_jobs(self): #获取job列表
                jobs = schedulerdate.get_jobs()
                print('get_jobs',jobs)
                return (jobs)

            def remove_job(self,jobid): # 删除指定job
                schedulerdate.remove_job(jobid)

            def remove_all_jobs(self): #删除所有job
                schedulerdate.remove_all_jobs()

        if Timingtype == 'add_date':
            data = request_data['data']
            Datetime = request_data['Datetime']  # date类型传入的时间参数值
            Username = request_data['Username']

            Job_id = []
            for cmd in command_aggre(): #循环命令执行添加job过程
                Treename = cmd.split(':')[1]
                command = str(cmd.split(':')[0])
                job_id_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
                job_cmd = Timing_date().add_job_date(Datetime,job_id_time,command)
                print(job_id_time)
                Job_id.append(job_id_time)
                data = {
                          "treename":Treename,
                          "pointtime":Datetime,
                          "cycletype":1,
                          "taskid":job_id_time,
                          "tasktype":"date",
                          "username":Username
                        }
                r = requests.post(Url01,json=data)
                print('jj',r.text)
                time.sleep(3)
            print('date 类型计划任务')
            j_date = {'msg':'date类任务已添加','statusCode':200, 'Jobid':Job_id}
            return jsonify(j_date)


        elif Timingtype == 'add_interval':
            data = request_data['data']
            Intervaltime = int(request_data['Intervaltime'])  # interval 类型传入的时间参数值, 当前支持s
            Username = request_data['Username']
            Job_id = []
            for cmd in command_aggre(): #循环命令执行添加job过程
                print('com',cmd)
                Treename = cmd.split(':')[1]
                command = str(cmd.split(':')[0])
                job_id_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
                job_cmd = Timing_date().add_job_interval(Intervaltime, job_id_time,command)
                Job_id.append(job_id_time)
                
                data = {
                          "treename":Treename,
                          "pointtime":Intervaltime,
                          "cycletype":1,
                          "taskid":job_id_time,
                          "tasktype":"Interval",
                          "username":Username
                        }
                r = requests.post(Url01,json=data)
                print('jj',r.text)
                time.sleep(3)

            print('interval类型计划任务')
            j_date = {'msg':'interval类任务已添加','statusCode':200, 'Jobid':Job_id}
            return jsonify(j_date)

        elif Timingtype == 'remove_job':
            Jobid= request_data['Jobid']
            try:
                Timing_date().remove_job(Jobid)
                j_date = {'msg': 'job已删除', 'statusCode': 200}
                return jsonify(j_date)
            except Exception  as e:
                j_date =  {'msg': '删除失败', 'statusCode': 200, 'error':e }
                return jsonify(j_date)

        elif Timingtype == 'remove_all':
            Timing_date().remove_all_jobs()
            j_date = {'msg': 'job已清空', 'statusCode': 200}
            return jsonify(j_date)
        elif Timingtype == 'get_jobs':
            get_jobs = Timing_date().get_jobs()
            len_get_jobs = len(get_jobs)
            if len_get_jobs == 0: #如果对列为空则返回状态给前端
                print('JOB为空')
                j_data = {'msg': 'job队列为空', 'statusCode': 200,}
                return jsonify(j_data)
                
            strgetjobs = str(get_jobs).strip('\"[').strip(']').replace('\'[','').replace(']\'','').split(',')
            all_jobsid = []
            for i in strgetjobs:
                i = str(re.findall(r'\d{4}-\d{1,2}-\d{1,2}-\d{1,2}-\d{1,2}-\d{1,2}',i)).strip("[").strip("]")
                i = i.strip("'")
                print(i)
                all_jobsid.append(i)
            print(all_jobsid)
           # all_jobsid = ['2020-09-16-14-55-54','2020-09-16-14-55-51']

            data = {
                "taskidlist": all_jobsid
            }

            r = requests.post(Url02, json=data)
            rdate = r.json()["date"]
            print('jk', rdate)


            j_date = {'msg': '返回任务id', 'statusCode': 200,'jobsid':rdate}
            return jsonify(j_date)
        else:
            j_date = {'msg': '参数异常', 'statusCode': 200}
            return jsonify(j_date)
            


api.add_resource(ScheduledTasksView,'/ScheduledTasks')

#压测机监控接口
class MonitorView(Resource):
    def get(self):
        monitor = subprocess.Popen(['curl', '-s', 'http://10.55.142.248:5003/monitor'], stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)

        # monitor = subprocess.Popen(['curl', '-s', 'http://0.0.0.0:5003/monitor'], stdout=subprocess.PIPE,
        #                            stderr=subprocess.STDOUT)
        out = monitor.stdout.readlines()
        outlist = []
        for k in out:
            k = k.decode("utf-8").strip(' ').strip('"').strip('\n", ').strip('\\n')
            outlist.append(k)
        outlist = outlist[2:-2]
        abc = []
        for x in outlist:
            x = ast.literal_eval(x)
            abc.append(x)
        j_data = {
            'msg': '性能数据获取成功',
            'code': 200,
            'data': abc
        }
        return (j_data)

api.add_resource(MonitorView,'/Monitor')


#终止单个压测脚本

class KillProcessView(Resource):
    def post(self):
        def get_processname():
            data = request.get_json(force=True)
            data = data['data']
            processname = data[0].get('processname')
            print(processname)
            return processname
        processname = get_processname() #获取要杀掉的进程名称，即脚本名称
        cmd = '/usr/bin/python3.7 /data/soft/Qa_quality/scripts/killprocess.py {processname}'.format(processname=processname)
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
api.add_resource(KillProcessView, '/KillProcess')



#终止所有压测脚本接口

class KillAllProcessView(Resource):
    def get(self):
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

        #操作日志存放
        date = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        operation_content = username + '/终止所有进程/' + date
        print(operation_content)
        except_log().putlog(1, 1, operation_content, 1, 2)
        
        j_data = {
            'msg':'终止所有压测脚本成功',
            'statusCode': 200
        }
        return jsonify(j_data)

api.add_resource(KillAllProcessView, '/KillAllProcess')

