from flask import Blueprint, request, render_template, url_for, redirect, session,flash,g,make_response,jsonify
from .db_mysql import User
from werkzeug.security import check_password_hash
from app.forms import ScriptForm, ExecuteScriptForm
import glob, time, os
import paramiko,re
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

home_page = Blueprint('home_page', __name__, url_prefix='/home_page')

#密码验证url登录
@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username = username).first()
    print(user)
    if user and check_password_hash(user.password, password):
        g.user = user
        return True
    return False

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)





#表单功能页面,
@home_page.route('/index', methods=['GET', 'POST'])
@auth.login_required
def index():
    form = ScriptForm()
    form2 = ExecuteScriptForm()
    cg = ''
    if request.method == 'POST':
        # if form2.validate_on_submit():
        if form.submit.data and form.validate_on_submit():

            hostip = form.hostip.data
            hostpath = form.hostpath.data
            parameter = form.parameter.data

            # form.hostip.data = ' '
            # form.hostpath.data = ' '
            # form.parameter.data = ' '

            print(hostip)


            # 本机测试脚本路径
            file = glob.glob('/Users/gz0101000646/Downloads/qa-test.py')
            # 定义自动生成脚本函数
            for one_polling in file:
                username = session.get('username')
                date = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
                new_file = "/Users/gz0101000646/Downloads/{username}-qa-test-{date}.py".format(date=date,username=username)
                filename = '脚本名称为:' + ' ' + '{username}-qa-test-{date}.py'.format(date=date,username=username)
                put_file = "/data/Qa_Quality/scripts/" + "{username}-qa-test-{date}.py".format(date=date,username=username)

                print(new_file)
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
                        print('连接{ip} 失败!\n'.format(ip))
                ssh1('10.10.5.169','root','fudao@123456',new_file)

                if cg == "200":
                   flash(u'生成脚本名称为:{filename}'.format(filename=filename),'info')
                return redirect(url_for('home_page.index'))

        if form2.submit2.data and form2.validate_on_submit():
            Filename = form2.Filename.data
            Concurrent = form2.Concurrent.data
            Dx = form2.Dx.data
            Xz = form2.Xz.data
            Ip  = form2.Ip.data
            print(Dx, Xz)
        # #拼接命令
            command = 'cd /home/wenba/xz/automation/snail' + ';' + 'python run.py' + '  -f' + ' ' + str(
                Filename) + ' -c' + ' ' + str(Concurrent) + ' ' +  str(Dx) + ' ' + str(Xz) + ' -i' + ' ' + str(Ip)
            print(command)


        # #远程执行压测命令
            def ssh2(ip,username,password,cmd):
                try:
                    transport = paramiko.Transport((ip, 9922))
                    transport.connect(username=username, password=password)
                    ssh = paramiko.SSHClient()
                    ssh._transport = transport
                    stdin, stdout, stderr = ssh.exec_command(command,get_pty=True) #支持多条命令拼接
                    # result = stdout.read(),stderr.read()
                    # for line in result:
                    #     print(line.decode())
                    uu = session.get('username')
                    Results_log = open('/Users/gz0101000646/Downloads/{username}.log'.format(username=uu),'w+')
                    Results_list = []
                    while True:  #实时输出
                        line = stdout.readline()
                        Results_list.append(line)
                        if not line:
                            break
                        # print(line)
                        print (Results_list)
                        Results_log.write(line)

                        if re.match('logpath:',line) is not None:
                            logpath = line.split(' ',1)[1]
                            print(logpath)
                    transport.close()

                except:
                    print('脚本执行失败.')
                    print('{ip} ERROR\n'.format(ip))
            ssh2('10.10.5.169','root','fudao@123456',command)

            flash(u'恭喜你哦，脚本执行完成了！','error')  #消息类别 可随意选择 ‘success’、‘info’、‘warning’、‘danger’
            return redirect(url_for('home_page.index'))


    return render_template('home_page/index.html', form=form, form2=form2, cg=cg)