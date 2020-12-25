import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from flask_restful import Resource, Api
from flask import Blueprint,request,jsonify, current_app
from .Httpauth import authtoken #Interface_authority初始化验证接口权限函数
from app.api_status.response_code import RET
import csv
import os
from collections import Counter
import requests
from app import db_mysql
from app.exts import db
from sqlalchemy.exc import IntegrityError
from app.aps_scheduler import schedulerdate, Url01, Url02, except_log


AuxiliaryFunction = Blueprint('AuxiliaryFunction',__name__,url_prefix='/AuxiliaryFunction')
api = Api(AuxiliaryFunction)

# 压测结果邮件发送
class ResultEmail(Resource):
    # decorators = [authtoken.login_required]
    # method_decorators = [Interface_authority]
    def post(self):
        # 获取请求的json数据，返回字典
        req_dict = request.get_json()
        useremail = req_dict.get("useremail")  # 用户邮箱
        datamsg = req_dict.get("datamsg")  # 发送内容

        # 判断用户邮箱是否传值或者为空
        if useremail is None:
            return jsonify(statusCode=RET.PARAMERR, msg="用户邮箱为必填项")
        elif useremail == "":
            return jsonify(statusCode=RET.PARAMERR, msg="用户邮箱不能为空")

        # 判断发送内容是否传值或者为空
        if datamsg is None:
            return jsonify(statusCode=RET.PARAMERR, msg="发送内容为必填项")
        elif datamsg == "":
            return jsonify(statusCode=RET.PARAMERR, msg="发送内容不能为空")

        my_sender = 'ou.wang@wenba100.com'  # 发件人邮箱账号
        my_pass = 'o@iax#iisq0r4pt!'  # 发件人邮箱密码
        # my_user = 'ou.wang@wenba100.com'  # 收件人邮箱账号，我这边发送给自己
        ret = True
        try:
            msgtext = ("压测报告：\n\n%s"%(datamsg))
            msg = MIMEText(msgtext, 'plain', 'utf-8')
            msg['From'] = formataddr(["QA系统",my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['To'] = formataddr(["%s"%useremail,useremail])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['Subject'] = "压测报告"  # 邮件的主题，也可以说是标题

            server = smtplib.SMTP_SSL("smtp.exmail.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是25
            server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
            server.sendmail(my_sender, [useremail, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.quit()  # 关闭连接
            print("发送成功")
        except Exception:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
            print("发送失败")
        return jsonify(statusCode=RET.OK, msg="发送成功")

api.add_resource(ResultEmail,'/ResultEmail')

# 压测报告接口
class PressureMeasurement(Resource):
    def get(self):
        print("压测报告接口")

    def post(self):

        # params_file = request.files['file_name']
        # dst = os.path.join(os.path.dirname(__file__), params_file.name)
        # params_file.save(dst)

        req_dict = request.get_json()
        dst = req_dict.get("file_name")  #文件名称 所在绝对路径

        # 判断发送内容是否传值或者为空
        if dst is None:
            return jsonify(statusCode=RET.PARAMERR, msg="文件名字为必填项，请检查脚本是否正确")
        elif dst == "":
            return jsonify(statusCode=RET.PARAMERR, msg="文件名字不能为空，请检查脚本是否正确")

        collect_list = []
        # print(dst)
        for i in dst:

            # 文件是否存在
            if os.path.exists(i):
                # 把.csv中数据按每行为一个元素插入到列表rows中（每行中的每列为一个元素组成行列表）

                with open(i) as csvfile:
                    readCSV = csv.reader(csvfile, delimiter=',')
                    rows = [row for row in readCSV]

                port_name = []  # 定义接口名称空列表
                # 把所有接口取出来存到port_name列表中
                for i in rows:
                    port_name.append(i[2])
                # 去重接口名称
                port_name = sorted(set(port_name), key=port_name.index)

                requcon = rows[0][0]  # 并发数
                # print("并发数是：%s" % requcon)

                # 定义一个空列表，用于存放数据
                data_list = []

                for x in port_name:  # 遍历接口名字

                    requissu = []  # 是否请求成功
                    requtime = []  # 请求时间
                    requcode = []  # 状态吗
                    errmsg = []  # 错误信息
                    errcodmsg = []
                    for i in rows:
                        if i[2] == x:  # 判断与接口名字一致的行，把所需数据插入到列表
                            requissu.append(i[1])
                            requtime.append(i[3])
                            requcode.append(i[4])
                            errmsg.append(i[5])
                            if i[1] == "False":
                                errcodmsg.append("状态码："+i[4]+",返回信息："+i[5])

                    # 打印接口名字
                    scpath = x.strip()
                    # print(scpath)

                    # 总请求量
                    total = len(requtime)
                    # print("总请求量：%d" % total)

                    # 最大响应时间
                    maxtime = max(requtime)
                    # print("最大响应时间:%0.3f" % float(max(requtime)))
                    # 最小响应时间
                    # print("最小响应时间:%0.3f" % float(min(requtime)))
                    # 平均响应时间
                    sum_num = 0
                    for a in requtime:
                        sum_num = sum_num + float(a)
                    avgtime = sum_num / len(requtime)
                    # print("平均响应时间:%0.3f" % avgtime)
                    # qps 并发数 /平均响应时间
                    # print(avgtime)
                    throught = int(requcon) / float(avgtime)

                    # throught = 3

                    # print("qps：%0.3f" % throught)
                    # 大于1秒个数
                    count = 0
                    for b in requtime:
                        if float(b) >= 1:
                            count = count + 1
                    # print("大于1秒个数：%d" % count)

                    # 错误率
                    error_set = []
                    for c in requissu:
                        if c != "True":
                            error_set.append(c)

                    Error = len(error_set) / len(requtime) * 100
                    # print("错误率：%0.3f %%" % Error)

                    error_num = len(error_set)
                    error_set = sorted(set(error_set), key=error_set.index)
                    errornone = []
                    if error_set != errornone:
                        pass
                        # print("错误个数:%d" % error_num)
                    #	print(error_set)

                    # 响应时间在90%以内
                    requtime = sorted(requtime)
                    subscript = int(len(requtime) * 0.9)
                    assign_time = float(requtime[subscript])

                    result1 = Counter(errcodmsg)

                    # print("90%%响应时间在%0.3f秒以内完成\n" % assign_time)
                    #
                    # print(scpath) # 打印接口名字
                    # print("并发数是：%s" % requcon)
                    # print("总请求量：%d" % total)
                    # print("最大响应时间:%0.3f" % float(max(requtime)))
                    # print("最小响应时间:%0.3f" % float(min(requtime)))
                    # print("平均响应时间:%0.3f" % avgtime)
                    # print("qps：%0.3f" % throught)
                    # print("大于1秒个数：%d" % count)
                    # print("错误率：%0.3f %%" % Error)
                    # print("错误个数:%d" % error_num)
                    # print("90%%响应时间在%0.3f秒以内完成\n" % assign_time)

                    premea = (
                        "接口：%s" % scpath,
                        "并发数是：%s" % requcon,
                        "总请求量：%d" % total,
                        "平均响应时间:%0.3f" % avgtime,
                        "qps：%0.3f" % throught,
                        "最大响应时间:%0.3f" % float(max(requtime)),
                        "最小响应时间:%0.3f" % float(min(requtime)),
                        "大于1秒个数：%d" % count,
                        "错误个数:%d" % error_num,
                        "错误率：%0.3f %%" % Error,
                        "错误信息:%s"% result1,
                        "90%%响应时间在%0.3f秒以内完成" % assign_time
                              )
                    data_list.append(premea)

                data = {
                    "requcon" : ("并发数是：%s" % requcon),
                    "data_list" : data_list
                }
                collect_list.append(data)
            else:
                return jsonify(statusCode=RET.FILENOTFOUNDERR, msg="文件没有找到，请检查脚本是否运行成功")
        return jsonify(statusCode=RET.OK, msg="分析完成",data=collect_list)
            # return jsonify(statusCode=RET.OK, msg="分析完成")

api.add_resource(PressureMeasurement,'/PressureMeasurement')


# 压测报告接口
class PressureMeasurementErro(Resource):
    def get(self):
        print("压测报告接口")

    def post(self):
        req_dict = request.get_json()
        dst = req_dict.get("file_name")  #文件名称 所在绝对路径
        erro_num = req_dict.get("erro_num") # 错误数

        # 判断发送内容是否传值或者为空
        if dst is None:
            return jsonify(statusCode=RET.PARAMERR, msg="文件名字为必填项，请检查脚本是否正确")
        elif dst == "":
            return jsonify(statusCode=RET.PARAMERR, msg="文件名字不能为空，请检查脚本是否正确")

        # 文件是否存在
        if os.path.exists(dst):
            # 把.csv中数据按每行为一个元素插入到列表rows中（每行中的每列为一个元素组成行列表）

            with open(dst) as csvfile:
                readCSV = csv.reader(csvfile, delimiter=',')
                rows = [row for row in readCSV]
            errmsg = []  # 定义接口名称空列表
            # 把所有接口取出来存到port_name列表中
            for i in rows:
                errmsg.append(i[1])
            result1 = Counter(errmsg)
            if result1["False"] >= erro_num and erro_num != 0:
                kill_url = "http://quality-test.xueba100.com/RestfulApi/KillAllProcess"
                kill_r = requests.get(url=kill_url)
                print(kill_r.json())
                return jsonify(statusCode=RET.DATAERR, msg="数据出错，请停止压测")
            else:
                return jsonify(statusCode=RET.OK, msg=" 请继续压测")
        else:
            return jsonify(statusCode=RET.FILENOTFOUNDERR, msg="文件没有找到，请检查脚本是否运行成功")
api.add_resource(PressureMeasurementErro, '/PressureMeasurementErro')

# 脑图报告接口
class BrainFigureReport(Resource):

    def get(self):
        print("脑图报告接口")
    # 插入数据库
    def post(self):
        # 获取请求的json数据，返回字典
        try:
            tfdata = request.get_json()
            tree_id =tfdata.get("tree_id")
            uid = tfdata.get("uid")
            test_result = tfdata.get("test_result")

            # project_type = tfdata.get("project_type")
            operation_content = tfdata.get("operation_content")
            operation_content = "脑图报告:%s" % operation_content


        except Exception as e:
            return jsonify(statusCode=RET.PARAMERR, msg="请查看是否传入json格式的参数")


        # 判断tree_id是否传值或者为空
        if tree_id is None:
            except_log().putlog(tree_id, uid, operation_content, 2, 3)
            return jsonify(statusCode=RET.PARAMERR, msg="tree_id为必填项")
        elif tree_id == "":
            except_log().putlog(tree_id, uid, operation_content, 2, 3)
            return jsonify(statusCode=RET.PARAMERR, msg="tree_id不能为空")

        # 判断uid是否传值或者为空
        if uid is None:
            except_log().putlog(tree_id, uid, operation_content, 2, 3)
            return jsonify(statusCode=RET.PARAMERR, msg="uid为必填项")
        elif uid == "":
            except_log().putlog(tree_id, uid, operation_content, 2, 3)
            return jsonify(statusCode=RET.PARAMERR, msg="uid不能为空")

        # 判断type是否传值或者为空
        if type is None:
            except_log().putlog(tree_id, uid, operation_content, 2, 3)
            return jsonify(statusCode=RET.PARAMERR, msg="type为必填项")
        elif type == "":
            except_log().putlog(tree_id, uid, operation_content, 2, 3)
            return jsonify(statusCode=RET.PARAMERR, msg="type不能为空")

        try:
            try:
                # user_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.uid == uid)
                user_list = db.session.query(db_mysql.Brainmap).filter(db_mysql.Brainmap.tree_id == tree_id)
                db.session.commit()
            finally:
                db.session.close()
        except IntegrityError as e:

            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            db.session.close()
            except_log().putlog(tree_id, uid, operation_content, 2, 3)
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")

        check_list = []
        for raw in user_list:
            # check_dic = {}
            # check_dic["children"] = []
            # check_dic["id"] = raw.id
            # check_dic["pid"] = raw.pid
            # check_dic["brainmapname"] = raw.brainmapname
            # check_dic["rdstatus"] = raw.rdstatus
            # check_dic["qastatus"] = raw.qastatus
            # check_dic["tree_id"] = raw.tree_id
            # check_dic["uid"] = raw.uid
            check_list.append(raw.qastatus)

        # 用例条数
        case_number = 0
        # 用例通过数
        case_pass = 0
        # 不通过用例数
        case_fail = 0
        # 阻碍用例数
        case_block = 0
        # 为提测用例数
        no_test = 0
        # 测试轮次
        test_rounds = 1

        for i in check_list:
            if i != None:
                case_number += 1
                if int(i) == 1:
                    case_pass += 1
                elif int(i) == 2:
                    case_fail += 1
                elif int(i) == 3:
                    case_block += 1
            elif i == None:
                no_test += 1
        try:
            try:
                re_list = db.session.query(db_mysql.TestReport).filter(db_mysql.TestReport.case_id == tree_id)
                db.session.commit()
            finally:
                db.session.close()
        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            db.session.close()
            except_log().putlog(tree_id, uid, operation_content, 2, 3)
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")

        if re_list:
            roli = []
            # 循环list 轮次+1
            for a in re_list:
                roli.append(a.test_rounds)
            if roli:
                test_rounds = max(roli) +1
        try:
            try:
                db.session.add(db_mysql.TestReport(
                        case_id = tree_id,
                        test_rounds = test_rounds,
                        case_number = case_number,
                        case_pass = case_pass,
                        case_fail = case_fail,
                        case_block = case_block,
                        no_test = no_test,
                        uid = uid,
                        test_result = test_result
                    ))
                db.session.commit()
            finally:
                db.session.close()
        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            db.session.close()
            except_log().putlog(tree_id, uid, operation_content, 2, 3)
            return jsonify(statusCode=RET.DATAERR, msg="添加失败")
        except_log().putlog(tree_id, uid, operation_content, 1, 3)
        return jsonify(statusCode=RET.OK, msg="添加成功")

api.add_resource(BrainFigureReport, '/BrainFigureReport')