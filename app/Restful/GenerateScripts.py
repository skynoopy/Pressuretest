import re
from _datetime import datetime
from flask import (Blueprint, request, current_app, jsonify)
from flask_restful import Resource, Api
import requests, json, os, time
from app.api_status.response_code import RET
from werkzeug.utils import secure_filename


GenerateScripts = Blueprint('GenerateScripts', __name__, url_prefix='/GenerateScripts')
api = Api(GenerateScripts)


class Generate(Resource):
    def post(self):

        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        file_name = req_dict.get("filename")  # 文件绝对路径
        pid = req_dict.get("pid")   # 父id为0的tree_id
        tree_pid = req_dict.get("tree_pid")   # 节点的上一级节点id
        selectHttp = req_dict.get("selectHttp")   #http协议
        hostip = req_dict.get("hostip")  # 项目ip
        envip = "http://quality.xueba100.com"   # 环境ip
        test_env = req_dict.get("test_env")    # 压测环境
        project_id = req_dict.get("project_id")

        # 验证file_name是否为空
        if file_name is None:
            return jsonify(statusCode=RET.PARAMERR, msg="请输入文件路径")
        elif file_name == "":
            return jsonify(statusCode=RET.PARAMERR, msg="请输入文件路径")
        # 验证pid是否为空
        if pid is None:
            return jsonify(statusCode=RET.PARAMERR, msg="请输入项目父id")
        elif pid == "":
            return jsonify(statusCode=RET.PARAMERR, msg="请输入项目父id")
        # 验证tree_pid是否为空
        if tree_pid is None:
            return jsonify(statusCode=RET.PARAMERR, msg="请输入节点父id")
        elif tree_pid == "":
            return jsonify(statusCode=RET.PARAMERR, msg="请输入节点父id")
        # 验证selectHttp是否为空
        if selectHttp is None:
            return jsonify(statusCode=RET.PARAMERR, msg="请输入http协议")
        elif selectHttp == "":
            return jsonify(statusCode=RET.PARAMERR, msg="请输入http协议")
        # 验证hostip是否为空
        if hostip is None:
            return jsonify(statusCode=RET.PARAMERR, msg="请输入项目域名")
        elif hostip == "":
            return jsonify(statusCode=RET.PARAMERR, msg="请输入项目域名")
        # 验证test_env是否为空
        if test_env is None:
            return jsonify(statusCode=RET.PARAMERR, msg="请选择压测环境")
        elif test_env == "":
            return jsonify(statusCode=RET.PARAMERR, msg="请选择压测环境")
        # 验证project_id是否为空
        if project_id is None:
            return jsonify(statusCode=RET.PARAMERR, msg="请输入项目工程id")
        elif project_id == "":
            return jsonify(statusCode=RET.PARAMERR, msg="请输入项目工程id")

        # 登录session
        # user_session = requests.Session()  # 定义一个全局session
        user_data = {"username": "tengfei.ma@wenba100.com", "password": "123456"}
        user_url = envip + "/RestfulApi/Login"
        user_obj = requests.post(user_url, json=user_data)
        user_val = user_obj.json()
        user_token = user_val.get("data").get("token")
        token = "xbj" + " " + user_token

        # 打开文件
        obj = open(file_name)
        while True:
            line = obj.readline()
            if not line:
                break
            else:
                result = eval(line)

                # 取出接口名称
                route_val = result["hostpath"]
                # 去掉接口里的'/'
                route_name = route_val.split('/')
                # 创建tree脚本,请求参数
                tree_data = {"Permission_parameters": {"type": project_id, "tree_id": pid, "uid": 10},
                             "filename": route_name[-1],
                             "pid": tree_pid,
                             "file_type": 2,
                             "uid": 10,
                             "project_type": 2}
                # headers数据
                tree_headers = {"Authorization": token}
                # 接口的url
                tree_url = envip + '/OperationTree/PerformanceTree'
                tree_obj = requests.post(tree_url, json=tree_data, headers=tree_headers)
                tree_val = tree_obj.json()

                # 如果创建tree成功，执行生成脚本
                if tree_val.get("statusCode") == 200:
                    # 调用生成脚本
                    script_data = {"Permission_parameters": {"type": project_id, "tree_id": pid, "uid": 10},
                                   "type": result["request"],
                                   "hostip": hostip,
                                   "hostpath": result["hostpath"],
                                   "userName": "tengfei.ma@wenba100.com",
                                   "parameter": result["parameter"]}

                    # headers数据
                    script_headers = {"Authorization": token}

                    script_url = envip + '/RestfulApi/ScriptGeneration'
                    script_obj = requests.post(script_url, json=script_data, headers=script_headers)
                    script_val = script_obj.json()

                else:
                    return jsonify(msg="创建tree出错", data=tree_val, route=result["hostpath"])

                # 如果生成脚本生成，执行更新tree
                if script_val.get("statusCode") == 200:
                    # 更新tree脚本
                    t_data = {"Permission_parameters": {"type": project_id, "tree_id": pid, "uid": 10},
                              "id": tree_val.get("zzid"),
                              "filename": route_name[-1],
                              "file_type": 2,
                              "meth": result["request"],
                              "sc_name": script_val.get("data").get("filename"),
                              "link_parameters": {
                                  "comfaceArr": [{
                                      "selectHttp": selectHttp,
                                      "hostip": hostip,
                                      "test_env": test_env,
                                      "type": result["request"],
                                      "hostpath": result["hostpath"],
                                      "parameter": result["parameter"]}],
                                  "filename": script_val.get("data").get("filename"),
                                  "scriptslog": "/mnt/fulllinklogs/datalogs/test_environmen/datalogs-tengfeima@wenba100com.log"},
                              "test_env": 1}
                    # headers数据
                    t_headers = {"Authorization": token}
                    # 接口的url
                    t_url = envip + '/OperationTree/PerformanceTree'
                    t_obj = requests.put(t_url, json=t_data, headers=t_headers)
                    t_val = t_obj.json()
                else:
                    return jsonify(msg="生成脚本出错", data=script_val, route=result["hostpath"])

                # 如果更新tree不成功
                if t_val.get("statusCode") != 200:
                    return jsonify(msg="更新tree出错", data=t_val, route=result["hostpath"])

        return jsonify(statusCode=RET.OK, msg="运行完成")

class Upload(Resource):
    def post(self):

        # 获取上传文件
        file = request.files.get("filename")
        filename = (file.filename).strip('"')
        # 获取当前时间戳
        t = str(time.time()).split('.')
        new_name = filename + t[0]
        # 存储路径
        base_path = '/mnt/uploads/production_environment/nginx_logs'
        # 储存文件
        file.save(os.path.join(base_path, secure_filename(new_name)))
        log_path = base_path + '/' + new_name

        return jsonify(data=log_path, statusCode=RET.OK, msg="上传成功")


# 生成脚本接口
api.add_resource(Generate, '/generate')
# 上传接口
api.add_resource(Upload, '/upload')
