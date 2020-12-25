# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify, current_app,session
from app.exts import db
from app import db_mysql
from app.api_status.response_code import RET
from sqlalchemy.exc import IntegrityError
import requests
from .Httpauth import authtoken ,serializer,Interface_authority #Interface_authority初始化验证接口权限函数
from flask_restful import Resource, Api

# 操作树：OperationTree

Unattended = Blueprint('Unattended',__name__,url_prefix='/Unattended')
api = Api(Unattended)

# 定时任务 增 删 改
class TimingTask(Resource):

    def get(self):

        return jsonify(ok = "ok")

    # 定时任务的新增
    def post(self):
        # 获取请求的json数据，返回字典
        req_dict = request.get_json()

        treename = req_dict.get("treename")  # 树名字
        pointtime = req_dict.get("pointtime")  # 首次执行时间
        username = req_dict.get("username")  # 用户名
        taskid = req_dict.get("taskid")  # 任务id
        tasktype = req_dict.get("tasktype")  # 任务类型

        # 判断树名字是否传值或者为空
        if treename is None:
            return jsonify(statusCode=RET.PARAMERR, msg="树名字为必填项")
        elif treename == "":
            return jsonify(statusCode=RET.PARAMERR, msg="树名字不能为空")
        # 判断执行时间是否传值或者为空
        if pointtime is None:
            return jsonify(statusCode=RET.PARAMERR, msg="执行时间为必填项")
        elif pointtime == "":
            return jsonify(statusCode=RET.PARAMERR, msg="执行时间不能为空")
        # 判断文件名是否传值或者为空
        if username is None:
            return jsonify(statusCode=RET.PARAMERR, msg="文件名字为必填项")
        elif username == "":
            return jsonify(statusCode=RET.PARAMERR, msg="文件名字不能为空")

        # 判断文件名是否传值或者为空
        if taskid is None:
            return jsonify(statusCode=RET.PARAMERR, msg="任务id为必填项")
        elif taskid == "":
            return jsonify(statusCode=RET.PARAMERR, msg="任务id不能为空")

        # 判断文件名是否传值或者为空
        if tasktype is None:
            return jsonify(statusCode=RET.PARAMERR, msg="任务类型为必填项")
        elif tasktype == "":
            return jsonify(statusCode=RET.PARAMERR, msg="任务类型不能为空")


        try:
            try:
                ttdata = db_mysql.Timingtask(
                    treename=treename,
                    pointtime=pointtime,
                    username=username,
                    taskid = taskid,
                    tasktype = tasktype

                )
                db.session.add(ttdata)
                db.session.flush()
                db.session.commit()

            finally:
                db.session.close()

        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            db.session.close()
            return jsonify(statusCode=RET.DATAERR, msg="数据创建失败")
        db.session.close()

        # print(zzid)
        return jsonify(statusCode = RET.OK,msg = "创建成功")

    # 定时任务的删除
    def delete(self):

        # 获取请求的json数据，返回字典
        req_dict = request.get_json()
        taskid = req_dict.get("taskid")  # 任务id

        # 判断任务id是否传值或者为空
        if taskid is None:
            return jsonify(statusCode=RET.PARAMERR, msg="任务id为必填项")
        elif taskid == "":
            return jsonify(statusCode=RET.PARAMERR, msg="任务id不能为空")

        try:
            db.session.query(db_mysql.Timingtask).filter(db_mysql.Timingtask.taskid == taskid).delete()
            db.session.commit()
        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            db.session.close()
            return jsonify(statusCode=RET.DATAERR, msg="删除失败")
        db.session.close()

        return jsonify(statusCode=RET.OK, msg="删除成功")

    def put(self):
        # 获取请求的json数据，返回字典
        req_dict = request.get_json()

        id = req_dict.get("id")  # 任务id
        treename = req_dict.get("treename")  # 树名字
        taskname = req_dict.get("taskname")  # 任务名字
        pointtime = req_dict.get("pointtime")  # 执行时间
        cycletype = req_dict.get("cycletype")  # 周期类型
        username = req_dict.get("username")  # 用户名

        # 判断任务id是否传值或者为空
        if id is None:
            return jsonify(statusCode=RET.PARAMERR, msg="任务id为必填项")
        elif id == "":
            return jsonify(statusCode=RET.PARAMERR, msg="任务id不能为空")

        data={
            "treename": treename,
            "taskname": taskname,
            "pointtime": pointtime,
            "cycletype": cycletype,
            "username": username
        }
        try:
            try:
                db.session.query(db_mysql.Timingtask).filter(db_mysql.Timingtask.id == id).update(data)
                db.session.commit()
            finally:
                db.session.close()
        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            db.session.close()
            return jsonify(statusCode=RET.DATAERR, msg="修改失败")

        return jsonify(statusCode=RET.OK, msg="修改成功")
api.add_resource(TimingTask,'/TimingTask')


# 定时任务 查
class TimingTaskCheck(Resource):

    def get(self):
        return jsonify(ok="ok")
    def post(self):
        # 获取请求的json数据，返回字典
        try:
            tfdata = request.get_json()
            taskidlist = tfdata.get("taskidlist")  # uid.

        except Exception as e:
            return jsonify(statusCode=RET.PARAMERR, msg="请查看是否传入json格式的参数")

        check_list = []
        try:

            # user_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.uid == uid)
            user_list = db.session.query(db_mysql.Timingtask).filter(db_mysql.Timingtask.taskid.in_(taskidlist))
            db.session.commit()

        except IntegrityError as e:

            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            db.session.close()
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")
        db.session.close()

        for raw in user_list:
            check_dic = {}
            check_dic["id"] = raw.id
            check_dic["treename"] = raw.treename
            check_dic["taskid"] = raw.taskid
            check_dic["pointtime"] = raw.pointtime
            check_dic["tasktype"] = raw.tasktype
            check_dic["username"] = raw.username
            check_list.append(check_dic)

        return jsonify(date=check_list, statusCode=RET.OK, msg="查询成功")


api.add_resource(TimingTaskCheck, '/TimingTaskCheck')




class test(Resource):
    # decorators = [ authtoken.login_required ]
    # method_decorators = [Interface_authority]
    def post(self):
        print('test post111111')
        j_data = {
            'msg':'test post',
            'code': 200
        }
        return jsonify(j_data)

api.add_resource(test,'/test')





