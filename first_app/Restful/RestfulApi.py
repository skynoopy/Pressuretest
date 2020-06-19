from flask import (flash, request, session, jsonify,Blueprint,g)
from werkzeug.security import check_password_hash,generate_password_hash #验证密码hash
from first_app.db_mysql import User
from first_app.exts import db
import glob, os,requests
import paramiko, subprocess,threading,time  #远程执行命令
from apscheduler.schedulers.background import BackgroundScheduler #定时任务
from flask_restful import Resource,Api  #restful api
from .Httpauth  import authtoken ,serializer,Interface_authority #Interface_authority初始化验证接口权限函数


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
                "code": 200
            }
            return jsonify(j_data)
            # return redirect(url_for('auth.login'))
        flash(error)

        j_data = {
            "msg": error,
            "code": 400
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
               "code": 200,
               "data" : {
                   "uid": uid,
                   # "token": get_token().decode("ascii"),
                   "token": token,
               }
           }
           return jsonify(j_data)
        flash(error)
        j_data = {
            "msg": error,
            "code": 400,
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
                "code": 200,
            }
        else:
            msg = "获取失败"
            j_data = {
                "msg": msg,
                "code": 404,
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
        hostip = data["hostip"]
        hostpath = data["hostpath"]
        parameter = data["parameter"]
        parameter = str(parameter)
        parameter = eval(parameter)
        parameter = str(parameter)

        print(type,hostip,hostpath,parameter)

        kk  = session.get('username')
        print(kk)

        def type_post():
            # 本机测试脚本路径
            file = glob.glob('/Users/gz0101000646/Downloads/qa-post-test.py')
            # 定义自动生成脚本函数
            for one_polling in file:
                username = session.get('username')
                username = str(username)
                username = username.split('@')[0] #去除邮箱后缀

                if '.' in username:
                    username = username.replace('.','') #匹配有.的用户名
                print(username)
                date = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
                new_file = "/Users/gz0101000646/Downloads/{username}-qa-test-{date}.py".format(date=date,username=username)
                filename = '{username}-qa-test-{date}.py'.format(date=date,username=username)
                put_file = "/data/Qa_Quality/scripts/" + "{username}-qa-test-{date}.py".format(date=date,username=username)



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
                                    "code": "200"
                                }
                                return jsonify(j_data)
                    ssh1('10.10.5.169','root','fudao@123456',new_file)
                    return filename




                except:
                    print('脚本执行失败，请检查.')
                    error = '脚本生成失败,请检查!'
                    return '500'


        if type == 'POST' or 'post':  #判断请求类型执行对应的函数
           print(type)
           status = type_post()
           if status != '500':

                j_data = {
                     "msg": 'post脚本生成成功',
                     "code": 200,
                     'data':{
                         "filename": status
                     }

                }

                return jsonify(j_data)
           elif status == '500':
               j_data = {
                   "msg": 'post脚本生成失败',
                   "code": 500,

               }
               return jsonify(j_data)
        else:
            print(type)
            # status = type_get()
            # if status != '500':
            j_data = {
                 "msg": '请求类型不对',
                 "code": 200,


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

        user_file_log = '/Users/gz0101000646/Downloads/{filename}.log'.format(filename=Filename)


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
                    "code": 500,

                }
                return jsonify(j_data)


        def ssh():
            ssh2('10.10.5.169', 'root', 'fudao@123456', command)

        scheduler = BackgroundScheduler()
        scheduler.add_job(ssh, 'date')
        scheduler.start()
        print('任务加入成功.')


        j_data = {
            "msg": '脚本执行成功.',
            "code": 200,
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
        def post(self):
            #获取前端数据对象组
            data = request.get_json(force=True)
            data = data['data']
            def get_parameter():
                try:
                    wc = int(len(data))
                    command_list = []
                    for i in range(wc):
                        dd = data[i]
                        command = 'cd /home/wenba/xz/automation/snail' + ';' + 'python run.py' + '  -f' + ' ' + str(
                            dd['Filename']) + ' -c' + ' ' + str(dd['Concurrent']) + ' ' + str(dd['Dx']) + ' ' + str(dd['Xz']) + ' -i' + ' ' + str(dd['Ip'])
                        command_list.append(command)
                    return command_list
                except Exception as e:
                    print(e)
                    j_data = {
                        'msg': '命令拼接失败.',
                        'code': 500
                    }
                    return jsonify(j_data)


            #paramiko远程执行
            def ssh2(ip, username, password, cmd,filename):
                try:
                    transport = paramiko.Transport((ip, 9922))
                    transport.connect(username=username, password=password)
                    ssh = paramiko.SSHClient()
                    ssh._transport = transport
                    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)  # 支持多条命令拼接
                    print('执行了')

                    #日志存放骚操作
                    try:
                        batch_log = '/Users/gz0101000646/Downloads/{Filename}.log'.format(Filename=filename)
                        Results_log = open(batch_log, 'w+', encoding='utf-8')
                        while True:
                            line = stdout.readline()
                            print(line, file=open(batch_log, 'w+', encoding='utf-8'))
                            print(line)
                            Results_log.write(line)

                            if not line:
                                Results_log.close()
                                break
                    except Exception as e:
                        print(e)
                        return

                except  Exception as e:
                    print('远程命令执行失败.', e)

                    j_data = {
                        'msg': '批量脚本执行失败.',
                        'code': 500,

                    }


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
                            threadcmd = threading.Thread(target=ssh2,args=('10.10.5.169','root','fudao@123456',cmd,filename))
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
                        'code': 500
                    }
                    return jsonify(j_data)


            scheduler = BackgroundScheduler()
            scheduler.add_job(ssh, 'date')
            scheduler.start()
            print('批量任务加入成功.')

            j_data = {
                'msg': '批量脚本执行成功.',
                'code': 200,

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
              batch_log = '/Users/gz0101000646/Downloads/{scriptname}.log'.format(scriptname=scriptname)
              print(batch_log)
              f = open(batch_log)
              lines = f.readlines()
              lines = [line.strip().strip('\u001b').replace('[','') for line in lines]  # 列表生成试替换换行和其他特殊符号
              lines = list(filter(None,lines))
              str_lines = str(lines)
              lines = str_lines.lstrip('[').rstrip(']')
              t_lines = lines.startswith('\'Atransactions:') #判断开头是否为指定字符
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
                      'code': 200,
                      'data': {
                          'resultlog': result_list
                      }
                  }

                  return (j_data)
              else:

                  j_data = {
                      'msg': '实时数据返回完毕',
                      'code': 200,
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
              scriptname = data[0]['scriptname']
              print(scriptname)
              return scriptname
          get_scriptname()

          def get_scriptlog(scriptname):
              batch_log = '/Users/gz0101000646/Downloads/{scriptname}.log'.format(scriptname=scriptname)
              print(batch_log)
              f = open(batch_log)
              lines = f.readlines()
              lines = [line.strip().strip('\u001b') for line in lines]  # 列表生成试替换换行和其他特殊符号
              lines = list(filter(None, lines)) #去空
              print(lines)
              return lines



          scriptname = get_scriptname()
          lines = get_scriptlog(scriptname)

          j_data={
              'msg':'请求日记成功',
              'code':200,
              'data':{
                  'logname': scriptname,
                  'resultlog':lines
              }
          }
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
            batch_log = '/Users/gz0101000646/Downloads/{scriptname}.log'.format(scriptname=scriptname)
            print(batch_log)
            f = open(batch_log)
            lines = f.readlines()
            lines = [line.strip().strip('\u001b').replace('[', '') for line in lines]  # 列表生成试替换换行和其他特殊符号
            lines = list(filter(None, lines))
            str_lines = str(lines)
            lines = str_lines.lstrip('[').rstrip(']')
            t_lines = lines.startswith('\'Atransactions:')  # 判断开头是否为指定字符
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
                    'code': 200,
                    'data': {
                        'resultlog': result_list
                    }
                }

                return (j_data)
            else:
                j_data = {
                    'msg': '实时数据返回完毕',
                    'code': 200,
                    'data': {
                        'resultlog': 'null',
                    }
                }
                return (j_data)

        j_data = result_log()
        return jsonify(j_data)
api.add_resource(RealtimeLog,'/RealtimeLog')


#定时任务 采用APScheduler模块
class ScheduledTasksView(Resource):
    def post(self):
        data = request.get_json(force=True)

        Filename = data['Filename']
        Concurrent = data['Concurrent']
        Dx = data['Dx']
        Xz = data['Xz']
        Ip = data['Ip']
        Exceptime = data['Exceptime']
        print(Filename,Concurrent,Dx,Xz,Ip,Exceptime)


        command = 'cd /home/wenba/xz/automation/snail' + ';' + 'python run.py' + '  -f' + ' ' + str(
        Filename) + ' -c' + ' ' + str(Concurrent) + ' ' + str(Dx) + ' ' + str(Xz) + ' -i' + ' ' + str(Ip)

        print(command)
        def ssh2(ip, username, password, cmd):
            try:
                transport = paramiko.Transport((ip, 9922))
                transport.connect(username=username, password=password)
                ssh = paramiko.SSHClient()
                ssh._transport = transport
                stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)  # 支持多条命令拼接
                print('执行了')

                try:
                    scheduled_log = '/Users/gz0101000646/Downloads/scheduled_{Filename}.log'.format(Filename=Filename)
                    Results_log = open(scheduled_log, 'w+', encoding='utf-8')

                    while True:
                        line = stdout.readline()
                        print(line)
                        print(line, file=open(scheduled_log, 'w+', encoding='utf-8'))
                        print(line)
                        Results_log.write(line)

                        if not line:
                            Results_log.close()
                            break
                except Exception as e:
                    print(e)


            except  Exception as e:
                print('命令执行失败.',e)
            transport.close()

        def ssh():
            ssh2('10.10.5.169', 'root', 'fudao@123456', command)


        def myjob():
            print('myjob:', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        try:

            scheduler = BackgroundScheduler()
            scheduler.add_job(myjob,'date',run_date=Exceptime)
            scheduler.add_job(ssh, 'date', run_date=Exceptime)
            scheduler.start()
            print('任务加入成功.')


            j_date = {
                'msg':'定时任务加入成功.',
                'code':200
            }

            return jsonify(j_date)
        except Exception as e:
            print(e)
            j_date = {
                'msg': '定时任务执行失败',
                'code': 500,
                'data': {
                    'error': e
                }

            }
api.add_resource(ScheduledTasksView,'/ScheduledTasks')

#压测机监控接口
class MonitorView(Resource):
    def get(self):
        monitor = subprocess.Popen(['curl', '-s', 'http://10.10.5.169:5003/monitor'], stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)
        out = monitor.stdout.readlines()
        outlist = []
        [outlist.append(k) for k in out]
        cpu = str(outlist[1]).strip('b').split()[2].strip(',')
        mem = str(outlist[2]).strip('b').split()[2].strip(',')

        print(cpu,mem)
        j_data = {
            'msg': '性能数据获取成功',
            'code': 200,
            'data':{
                'cpu': cpu,
                'mem': mem
            }
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

        ssh('10.10.5.169', 'root', 'fudao@123456', cmd)
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
        ssh('10.10.5.169', 'root', 'fudao@123456', cmd)
        j_data = {
            'msg':'终止所有压测脚本成功',
            'code': 200
        }
        return jsonify(j_data)

api.add_resource(KillAllProcessView, '/KillAllProcess')




