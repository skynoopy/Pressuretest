# -*- coding: utf-8 -*-
import re, time, os
from flask import (Blueprint, request, current_app, jsonify)
from flask_restful import Resource, Api
from collections import Counter, OrderedDict
import requests, json, ast, sqlalchemy.exc
from werkzeug.utils import secure_filename
from datetime import datetime
from app.api_status.response_code import RET
from urllib.parse import unquote


AnalysisLog = Blueprint('AnalysisLog', __name__, url_prefix='/AnalysisLog')
api = Api(AnalysisLog)

# crm日志结构
crm = re.compile(
            r'(?P<ip>.*?) - - \[(?P<time>.*?)\] "(?P<request>.*?) (?P<route>.*?) (?P<protocols>.*?)" '
            r'(?P<status>.*?) (?P<bytes>.*?) (?P<body>.*?) "(?P<referer>.*?)" "(?P<ua>.*?)"')
# console日志结构
console = re.compile(
            r'(?P<ip>.*?) -  \[(?P<time>.*?)\] "(?P<request>.*?) (?P<route>.*?) (?P<protocols>.*?)" '
            r'(?P<status>.*?) (?P<bytes>.*?) (?P<body>.*?) "(?P<referer>.*?)" "(?P<ua>.*?)"')
# other日志结构
other = re.compile(
            r'(?P<ip>.*?) -  \[(?P<time>.*?)\] "(?P<request>.*?) (?P<route>.*?) (?P<protocols>.*?)" '
            r'(?P<status>.*?) (?P<bytes>.*?) (?P<body>.*?) "(?P<referer>.*?)" "(?P<ua>.*?)"')

class StatisticsLog(Resource):

    # 读取Nginx日志内容，统计接口请求次数
    def post(self):

        # 获取请求的json数据, 返回字典
        req_dict = request.form.to_dict()
        project = req_dict.get("project")
        type = req_dict.get("type")   # 1、不过滤，2、过滤带请求参数的
        file = request.files.get("filename")
        filename = (file.filename).strip('"')

        # 验证project是否为空
        if project is None:
            return jsonify(statusCode=RET.PARAMERR, msg="请输入项目名")
        elif project == "":
            return jsonify(statusCode=RET.PARAMERR, msg="请输入项目名")
        # 验证type是否为空
        if type is None:
            return jsonify(statusCode=RET.PARAMERR, msg="请选择类型")
        elif type == "":
            return jsonify(statusCode=RET.PARAMERR, msg="请选择类型")
        # 验证file是否为空
        if file is None:
            return jsonify(statusCode=RET.PARAMERR, msg="请上传文件")
        elif file == "":
            return jsonify(statusCode=RET.PARAMERR, msg="请上传文件")

        log_list = []
  
        t = str(time.time()).split('.')

        # 取出文件名
        name = filename.split('.')[0]
        ext = filename.split('.')[1]
        new_filename = ''.join(name) + t[0] + '.' + ext

        # 储存文件
        base_path = '/mnt/uploads/production_environment/nginx_logs'
        file.save(os.path.join(base_path, secure_filename(new_filename)))
        nginx_log = base_path + '/' + new_filename

        # 打开文件
        log_file = open(nginx_log)
        while True:
            try:
                # 读取文件每行内容
                line = log_file.readline()
                # 如果没有数据，跳出循环
                if not line:
                    break
                else:
                    # # 讲字符串转换为字典
                    # line = eval(line)
                    #
                    # if type == 1:
                    #     log_list.append(line["url"])
                    #
                    # elif type == 2:
                    #     body = line["request_body"]
                    #     if body == "" or body == {}:
                    #         log_list.append(line["url"])

                    if project == 'crm':
                        # 解析单行nginx日志
                        result = crm.search(line)

                        # 不过滤，跑所有内容
                        if int(type) == 1:
                            # 把取出来的路由存入log_list
                            log_list.append(result.group('route'))

                        # 过滤带请求参数的请求
                        elif int(type) == 2:

                            body = result.group("body")
                            if body == "{}":

                                # 把不带请求参数的路由存入log_list
                                log_list.append(result.group('route'))

                    elif project == 'console':
                        # 解析单行nginx日志
                        result = console.search(line)

                        # 不过滤，跑所有内容
                        if int(type) == 1:
                            # 去掉接口后方的时间戳
                            route_obj = result.group("route").split("?")
                            # 把取出来的路由存入log_list
                            log_list.append(route_obj[0])

                        # 过滤带请求参数的请求
                        elif int(type) == 2:

                            body = result.group("body")
                            if body == "":

                                # 把不带请求参数的路由存入log_list
                                log_list.append(result.group('route'))

                    elif project == 'other':

                        # 解析单行nginx日志
                        result = other.search(line)

                        # 不过滤，跑所有内容
                        if int(type) == 1:

                            # 把取出来的路由存入log_list
                            log_list.append(result.group('route'))

                        # 过滤带请求参数的请求
                        elif int(type) == 2:

                            body = result.group("body")
                            if body == "":

                                # 把不带请求参数的路由存入log_list
                                log_list.append(result.group('route'))

            except (UnicodeDecodeError, AttributeError):
                pass
            continue
        log_file.close()

        data = Counter(log_list).most_common()
        data_list = []
        for i in data:
            data_dic = {}
            data_dic["port"] = i[0],
            data_dic["number"] = i[1]
            data_list.append(data_dic)
        return jsonify(data=data_list, statusCode=RET.OK, msg="运行成功")


class ReadLog(Resource):

    # 读取Nginx日志内容
    def post(self):

        # 获取请求的json数据, 返回字典
        req_dict = request.form.to_dict()
        project = req_dict.get("project")
        type = req_dict.get("type")   # 1、不过滤，2、过滤带请求参数的
        req_url = req_dict.get("req_url")   # 请求域名
        file = request.files.get("filename")
        filename = (file.filename).strip('"')

        # 验证project是否为空
        if project is None:
            return jsonify(statusCode=RET.PARAMERR, msg="请输入项目名")
        elif project == "":
            return jsonify(statusCode=RET.PARAMERR, msg="请输入项目名")
        # 验证type是否为空
        if type is None:
            return jsonify(statusCode=RET.PARAMERR, msg="请选择类型")
        elif type == "":
            return jsonify(statusCode=RET.PARAMERR, msg="请选择类型")
        # 验证file是否为空
        if file is None:
            return jsonify(statusCode=RET.PARAMERR, msg="请上传文件")
        elif file == "":
            return jsonify(statusCode=RET.PARAMERR, msg="请上传文件")
        # 验证req_url是否为空
        if req_url is None:
            return jsonify(statusCode=RET.PARAMERR, msg="请输入项目名")
        elif req_url == "":
            return jsonify(statusCode=RET.PARAMERR, msg="请输入项目名")

        # crm登录session
        crm_session = requests.Session()  # 定义一个全局session
        crm_data = {"user_name": "tengfeizhuanyong", "passwd": "afdd0b4ad2ec172c586e2150770fbf9e"}
        crm_url = req_url + "/admin/login"
        crm_log = crm_session.post(crm_url, json=crm_data)

        # console登录session
        console_session = requests.Session()  # 定义一个全局session
        console_data = {"user_name": "mtf", "passwd": "111111"}
        console_url = req_url + "/admin/login"
        console_log = console_session.post(console_url, json=console_data)

        # 获取当前时间戳
        t = str(time.time()).split('.')

        # 取出文件名
        name = filename.split('.')[0]
        ext = filename.split('.')[1]
        new_filename = ''.join(name) + t[0] + '.' + ext

        # 上传路径
        base_path = '/mnt/uploads/production_environment/nginx_logs'

        # 储存文件
        file.save(os.path.join(base_path, secure_filename(new_filename)))
        nginx_log = base_path + '/' + new_filename

        log_list = []
        log_file = open(nginx_log)
        while True:
            try:
                line = log_file.readline()

                if not line:
                    break
                else:
                    # # 字符串转换成字典
                    # line = eval(line)
                    #
                    # # 不过滤，跑所有内容
                    # if type == 1:
                    #     body = line["request_body"]
                    #     if "=" in body:
                    #         # 将非json格式的请求参数，转换成json格式
                    #         body_str = str(body).replace('=', '":"').replace('&', '","')
                    #         body_dic = eval('{"' + body_str + '"}')
                    #
                    #         # 存入字典
                    #         dic = {}
                    #         dic["request"] = line["method"]
                    #         dic["hostpath"] = line["url"]
                    #         dic["parameter"] = body_dic
                    #
                    #         # 把取出来的路由存入log_list
                    #         log_list.append(dic)
                    #     else:
                    #         # 存入字典
                    #         dic = {}
                    #         dic["request"] = line["method"]
                    #         dic["hostpath"] = line["url"]
                    #         dic["parameter"] = line["request_body"]
                    #
                    #         # 把取出来的路由存入log_list
                    #         log_list.append(dic)
                    #
                    # # 过滤选出不带请求参数的接口
                    # elif type == 2:
                    #     body = line["request_body"]
                    #     if body == "" or body == {}:
                    #         # 存入字典
                    #         dic = {}
                    #         dic["request"] = line["method"]
                    #         dic["hostpath"] = line["url"]
                    #         dic["parameter"] = line["request_body"]
                    #
                    #         # 把取出来的路由存入log_list
                    #         log_list.append(dic)

                    if project == 'crm':
                        # 解析单行nginx日志
                        result = crm.search(line)

                        # 不过滤，跑所有内容
                        if int(type) == 1:
                            # 过滤.js、.ico、.png的请求
                            if '.js' not in result.group('route') and '.png' not in result.group('route') \
                                    and '.ico' not in result.group('route') and result.group('referer') != '-' \
                                    and result.group('route') != '/':

                                # 存入字典
                                dic = {}
                                # dic["ip"] = result.group("ip")
                                # dic["time"] = result.group("time")
                                dic["request"] = result.group("request")
                                dic["hostpath"] = result.group("route")
                                if result.group("body") == "":
                                    dic["parameter"] = '{}'
                                elif result.group("body") == "null":
                                    dic["parameter"] = '{}'
                                else:
                                    dic["parameter"] = result.group("body")
                                # dic["hostip"] = result.group("referer")

                                # 把取出来的路由存入log_list
                                log_list.append(dic)

                        # 过滤带请求参数的请求
                        elif int(type) == 2:

                            body = result.group("body")
                            if body == "{}":

                                # 存入字典
                                dic = {}
                                # dic["ip"] = result.group("ip")
                                # dic["time"] = result.group("time")
                                dic["request"] = result.group("request")
                                dic["hostpath"] = result.group("route")
                                dic["parameter"] = result.group("body")
                                # dic["hostip"] = result.group("referer")
                                # print(result.groupdict())
                                # print(dic)

                                # 把不带请求参数的路由存入log_list
                                log_list.append(dic)

                    elif project == 'console':
                        # 解析单行nginx日志
                        result = console.search(line)

                        # 不过滤，跑所有内容
                        if int(type) == 1:
                            # 过滤.js、.ico、.png的请求
                            if '.js' not in result.group('route') and '.png' not in result.group('route') \
                                    and '.ico' not in result.group('route') and result.group('referer') != '-' \
                                    and result.group('route') != '/':

                                # 解决get接口里带参数被当时间戳过滤掉问题
                                if "=" and "&" in result.group("route"):

                                    # 过滤body数据，把非json格式转换成json
                                    body = result.group("body")
                                    if "=" in body and "{" not in body:
                                        # 将非json格式的请求参数，转换成json格式
                                        body_str = str(body).replace('=', '":"').replace('&', '","')
                                        body_val = '{"' + body_str + '"}'

                                        # 存入字典
                                        dic = {}
                                        # dic["ip"] = result.group("ip")
                                        # dic["time"] = result.group("time")
                                        dic["request"] = result.group("request")
                                        dic["hostpath"] = result.group("route")
                                        dic["parameter"] = body_val
                                        # dic["hostip"] = result.group("referer")

                                        # 把取出来的路由存入log_list
                                        log_list.append(dic)

                                    else:
                                        # 存入字典
                                        dic = {}
                                        # dic["ip"] = result.group("ip")
                                        # dic["time"] = result.group("time")
                                        dic["request"] = result.group("request")
                                        dic["hostpath"] = result.group("route")
                                        if body == "":
                                            dic["parameter"] = '{}'
                                        elif body == "null":
                                            dic["parameter"] = '{}'
                                        else:
                                            dic["parameter"] = body.replace('\\', '')
                                        # dic["hostip"] = result.group("referer")

                                        # 把取出来的路由存入log_list
                                        log_list.append(dic)

                                else:
                                    # 去掉接口里的时间戳
                                    route_obj = result.group("route").split("?")

                                    # 过滤body数据，把非json格式转换成json
                                    body = result.group("body")
                                    if "=" in body and "{" not in body:
                                        # 将非json格式的请求参数，转换成json格式
                                        body_str = str(body).replace('=', '":"').replace('&', '","')
                                        body_val = '{"' + body_str + '"}'

                                        # 存入字典
                                        dic = {}
                                        # dic["ip"] = result.group("ip")
                                        # dic["time"] = result.group("time")
                                        dic["request"] = result.group("request")
                                        dic["hostpath"] = route_obj[0]
                                        dic["parameter"] = body_val
                                        # dic["hostip"] = result.group("referer")

                                        # 把取出来的路由存入log_list
                                        log_list.append(dic)

                                    else:
                                        # 存入字典
                                        dic = {}
                                        # dic["ip"] = result.group("ip")
                                        # dic["time"] = result.group("time")
                                        dic["request"] = result.group("request")
                                        dic["hostpath"] = route_obj[0]
                                        if body == "":
                                            dic["parameter"] = '{}'
                                        elif body == "null":
                                            dic["parameter"] = '{}'
                                        else:
                                            dic["parameter"] = body.replace('\\', '')
                                        # dic["hostip"] = result.group("referer")

                                        # 把取出来的路由存入log_list
                                        log_list.append(dic)

                        # 过滤带请求参数的请求
                        elif int(type) == 2:

                            body = result.group("body")
                            if body == "" or body == {} or body == "null":
                                # 去掉接口里的时间戳
                                route_obj = result.group("route").split("?")

                                # 存入字典
                                dic = {}
                                # dic["ip"] = result.group("ip")
                                # dic["time"] = result.group("time")
                                dic["request"] = result.group("request")
                                dic["hostpath"] = route_obj[0]
                                dic["parameter"] = result.group("body")
                                # dic["hostip"] = result.group("referer")
                                # print(result.groupdict())
                                # print(dic)

                                # 把不带请求参数的路由存入log_list
                                log_list.append(dic)

                    elif project == 'other':
                        # 解析单行nginx日志
                        result = other.search(line)

                        # 不过滤，跑所有内容
                        if int(type) == 1:
                            # 过滤.js、.ico、.png的请求
                            if '.js' not in result.group('route') and '.png' not in result.group('route') \
                                    and '.ico' not in result.group('route') and result.group('referer') != '-' \
                                    and result.group('route') != '/':

                                # 过滤body数据，把非json格式转换成json
                                body = result.group("body")
                                if "=" in body and "{" not in body:
                                    # 将非json格式的请求参数，转换成json格式
                                    body_str = str(body).replace('=', '":"').replace('&', '","')
                                    body_val = '{"' + body_str + '"}'

                                    # 存入字典
                                    dic = {}
                                    # dic["ip"] = result.group("ip")
                                    # dic["time"] = result.group("time")
                                    dic["request"] = result.group("request")
                                    dic["hostpath"] = result.group("route")
                                    dic["parameter"] = body_val
                                    # dic["hostip"] = result.group("referer")

                                    # 把取出来的路由存入log_list
                                    log_list.append(dic)

                                else:
                                    # 存入字典
                                    dic = {}
                                    # dic["ip"] = result.group("ip")
                                    # dic["time"] = result.group("time")
                                    dic["request"] = result.group("request")
                                    dic["hostpath"] = result.group("route")
                                    if body == "":
                                        dic["parameter"] = '{}'
                                    elif body == "null":
                                        dic["parameter"] = '{}'
                                    else:
                                        dic["parameter"] = result.group("body").replace('\\', '')
                                    # dic["hostip"] = result.group("referer")

                                    # 把取出来的路由存入log_list
                                    log_list.append(dic)

                        # 过滤带请求参数的请求
                        elif int(type) == 2:

                            body = result.group("body")
                            if body == "":
                                # 存入字典
                                dic = {}
                                # dic["ip"] = result.group("ip")
                                # dic["time"] = result.group("time")
                                dic["request"] = result.group("request")
                                dic["hostpath"] = result.group("route")
                                dic["parameter"] = result.group("body")
                                # dic["hostip"] = result.group("referer")
                                # print(result.groupdict())
                                # print(dic)

                                # 把不带请求参数的路由存入log_list
                                log_list.append(dic)

            except (UnicodeDecodeError,):
                pass
            # continue
        log_file.close()
        # return log_list

        # 根据hostpath去重
        data = OrderedDict()
        for i in log_list:
            data.setdefault(i['hostpath'], {**i})
        data = list(data.values())
        # return data

        # 验证接口是否可以请求通
        right_list = []
        err_list = []
        for obj in data:
            if project == 'crm':
                try:
                    # 校验请求是否可以请求通
                    url_crm = req_url + obj.get("hostpath")
                    # post请求
                    if obj.get("request") == "POST":
                        post_crm = crm_session.post(url_crm, json=json.loads(obj.get("parameter")))
                        val = post_crm.json()

                        if val.get("statusCode") == 0:
                            right_list.append(obj)
                        else:
                            err_list.append(obj)
                            err_list.append(val.get("statusCode"))
                    # get请求
                    elif obj.get("request") == "GET":
                        get_crm = requests.get(url_crm)
                        val = get_crm.json()
                        if val.get("statusCode") == 0:
                            right_list.append(obj)
                        else:
                            err_list.append(obj)
                            err_list.append(val.get("statusCode"))

                except json.decoder.JSONDecodeError:
                    pass

            elif project == 'console':
                try:
                    # 校验请求是否可以请求通
                    url_console = req_url + obj.get("hostpath")

                    # post请求
                    if obj.get("request") == "POST":
                        post_console = console_session.post(url_console, json=json.loads(obj.get("parameter")))
                        post_val = post_console.json()
                        if post_val.get("statusCode") == 0:
                            right_list.append(obj)
                        else:
                            err_list.append(obj)
                            err_list.append(post_val.get("statusCode"))
                    # get请求
                    elif obj.get("request") == "GET":
                        get_console = console_session.get(url_console)
                        get_val = get_console.json()
                        if get_val.get("statusCode") == 0:
                            right_list.append(obj)
                        else:
                            err_list.append(obj)
                            err_list.append(get_val.get("statusCode"))

                except (UnicodeEncodeError, json.decoder.JSONDecodeError):
                    pass

            elif project == 'other':
                try:
                    # 校验请求是否可以请求通
                    url_other = req_url + obj.get("hostpath")

                    # post请求
                    if obj.get("request") == "POST":
                        # 过滤带%5B编码的参数
                        if "%5B" in obj.get("parameter"):
                            # 按照urlencoded格式输出
                            requestJSON = unquote(obj.get("parameter")).replace('"', '')\
                                .replace('{', '').replace('}', '').replace(',', '\n')
                            # requestdata = requestJSON.encode("utf-8")
                            head = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", 'Connection': 'close'}
                            jsondata = requests.post(url_other, data=requestJSON, headers=head)
                            responsedata = jsondata.json()
            
                            if responsedata.get("statusCode") == 0:
                                right_list.append(obj)
                            else:
                                err_list.append(obj)
                                err_list.append(responsedata.get("statusCode"))

                        # 处理请求参数里的时间格式不符合xx-xx-xx xx:xx:xx格式
                        elif "+" in obj.get("parameter") and "%3A" in obj.get("parameter"):
                            req = str(obj.get("parameter")).replace('+', '').replace("%3A", ':')
                            post_other = requests.post(url_other, json=json.loads(req))
                            val_other = post_other.json()
                            if val_other.get("statusCode") == 0:
                                right_list.append(obj)
                            else:
                                err_list.append(obj)
                                err_list.append(val_other.get("statusCode"))

                        else:
                            post_other = requests.post(url_other, json=json.loads(obj.get("parameter")))
                            val_other = post_other.json()
                            if val_other.get("statusCode") == 0:
                                right_list.append(obj)
                            else:
                                err_list.append(obj)
                                err_list.append(val_other.get("statusCode"))
                    # get请求
                    elif obj.get("request") == "GET":
                        get_other = requests.get(url_other)
                        val = get_other.json()
                        if val.get("statusCode") == 0:
                            right_list.append(obj)
                        else:
                            err_list.append(obj)
                            err_list.append(val.get("statusCode"))

                except (UnicodeEncodeError, json.decoder.JSONDecodeError):
                    pass

        # 获取当前时间
        # t = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        t = str(time.time()).split('.')

        # 存储路径
        result_path = '/mnt/uploads/production_environment/nginx_scripts'

        # 存储能跑通的接口
        right_name = "right_obj" + t[0]
        right_log = result_path + '/' + right_name
        # file = open('/Users/matengfei/Downloads/log/right_obj{t}'.format(t=t[0]), 'a')
        file = open(right_log, 'a')
        for r in range(len(right_list)):
            s = str(right_list[r]) + '\n'  # 去除[],这两行按数据不同，可以选择
            # s = s.replace("'", '') + '\n'  # 去除单引号，逗号，每行末尾追加换行符
            file.write(s)
        file.close()

        # 存储不能跑通的接口
        err_name = "error_obj" + t[0]
        err_log = result_path + '/' + err_name
        file = open(err_log, 'a')
        for e in range(len(err_list)):
            s = str(err_list[e]) + '\n'  # 去除[],这两行按数据不同，可以选择
            # s = s.replace("'", '') + '\n'  # 去除单引号，逗号，每行末尾追加换行符
            file.write(s)
        file.close()
        # print("保存文件成功")
        result_log = []
        result_log.append(right_log)
        result_log.append(err_log)
        return jsonify(data=result_log, statusCode=RET.OK, msg="运行成功")
        

# 统计log路由的请求次数
api.add_resource(StatisticsLog, '/statisticslog')
# 读取log输出生成脚本所需参数接口
api.add_resource(ReadLog, '/readlog')