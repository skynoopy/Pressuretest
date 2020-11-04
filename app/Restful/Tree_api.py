from flask import Blueprint, request, jsonify, current_app,session
from app.exts import db
from app import db_mysql
from app.api_status.response_code import RET
from sqlalchemy.exc import IntegrityError
import requests
from .Httpauth import authtoken ,serializer,Interface_authority #Interface_authority初始化验证接口权限函数
from flask_restful import Resource, Api

# 操作树：OperationTree
OperationTree = Blueprint('OperationTree',__name__,url_prefix='/OperationTree')
api = Api(OperationTree)
# 性能树 ：PerformanceTree
# 对性能树的 增删改
class PerformanceTree(Resource):
    decorators = [authtoken.login_required]
    method_decorators = [Interface_authority]

    def get(self):
        return '对性能树增删改操作'
    # 对性能树的新增
    def post(self):

        # 获取请求的json数据，返回字典
        req_dict = request.get_json()
        filename = req_dict.get("filename")  # 文件名
        pid = req_dict.get("pid")  # 父id
        file_type = req_dict.get("file_type")  # 文件 类型 1 为文件 2 为脚本
        uid = req_dict.get("uid")  # 用户id

        # 判断文件名是否传值或者为空
        if filename is None:
            return jsonify(statusCode=RET.PARAMERR, msg="文件名字为必填项")
        elif filename == "":
            return jsonify(statusCode=RET.PARAMERR, msg="文件名字不能为空")

        # 判断父id是否传值或者为空
        if pid is None:
            return jsonify(statusCode=RET.PARAMERR, msg="父id为必填项")
        elif pid == "":
            return jsonify(statusCode=RET.PARAMERR, msg="父id不能为空")

        # 判断文件类型是否传值或者为空
        if file_type is None:
            return jsonify(statusCode=RET.PARAMERR, msg="文件类型为必填项")

        # 判断用户uid是否传值或者为空
        if uid is None:
            return jsonify(statusCode=RET.PARAMERR, msg="uid为必填项")

        try:
            try:
                db.session.add(
                    db_mysql.Tree(filename=filename, pid=pid, file_type=file_type, uid=uid))
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

        j_data = {
            "statusstatusCode" : RET.OK,
            "msg" : "创建成功"
        }
        return jsonify(statusCode = RET.OK,msg = "创建成功")

    # 对性能树的修改
    def put(self):
        # 获取请求的json数据，返回字典
        req_dict = request.get_json()

        id = req_dict.get("id")  # 文件名id
        file_type = req_dict.get("file_type")  # 文件 类型 1 为文件 2 为脚本
        filename = req_dict.get("filename")  # 文件名
        meth = req_dict.get("meth")  # 请求类型 post get
        sc_ip = req_dict.get("sc_ip")  # 脚本ip
        sc_path = req_dict.get("sc_path")  # 脚本路径
        sc_praameter = req_dict.get("sc_praameter")  # 脚本参数
        sc_name = req_dict.get("sc_name")  # 脚本名称
        concurrency = req_dict.get("concurrency")  # 并发数
        strategy = req_dict.get("strategy")  # 并发策略
        con_praameter = req_dict.get("con_praameter")  # 并发参数

        if id is None:
            return jsonify(statusCode=RET.PARAMERR, msg="脚本id为必填项")
        # file_type == 1 为文件夹类型只能修改文件夹名称
        if file_type == 1:
            # 判断文件名是否传值或者为空
            if filename is None:
                return jsonify(statusCode=RET.PARAMERR, msg="文件名字为必填项")
            elif filename == "":
                return jsonify(statusCode=RET.PARAMERR, msg="文件名字不能为空")
            try:
                try:
                    user_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == id).update(
                        {"filename": filename})
                    db.session.commit()
                finally:
                    db.session.close()
            except IntegrityError as e:
                # 数据库操作错误后的回滚
                db.session.rollback()
                current_app.logger.error(e)
                db.session.close()
                return jsonify(statusCode=RET.DATAERR, msg="修改失败")
        # file_type == 2 为脚本类型，可以修改脚本名，脚本ip，脚本路径，脚本参数
        elif file_type == 2:
            # 判断脚本名是否传值或者为空
            if filename is None:
                return jsonify(statusCode=RET.PARAMERR, msg="文件名字为必填项")
            elif filename == "":
                return jsonify(statusCode=RET.PARAMERR, msg="文件名字不能为空")
            # 判断用户脚本ip是否传值或者为空
            if sc_ip is None:
                return jsonify(statusCode=RET.PARAMERR, msg="脚本ip为必填项")
            elif sc_ip == "":
                return jsonify(statusCode=RET.PARAMERR, msg="脚本ip不能为空")

            # 判断用户脚本路径是否传值或者为空
            if sc_path is None:
                return jsonify(statusCode=RET.PARAMERR, msg="脚本路径为必填项")
            elif sc_path == "":
                return jsonify(statusCode=RET.PARAMERR, msg="脚本路径不能为空")

            # 判断用户脚本参数是否传值或者为空
            if sc_praameter is None:
                return jsonify(statusCode=RET.PARAMERR, msg="脚本参数为必填项")
            elif sc_praameter == "":
                return jsonify(statusCode=RET.PARAMERR, msg="脚本参数不能为空")

            # 判断用户脚本参数是否传值或者为空
            if sc_name is None:
                return jsonify(statusCode=RET.PARAMERR, msg="脚本名称为必填项")
            elif sc_praameter == "":
                return jsonify(statusCode=RET.PARAMERR, msg="脚本名称不能为空")

            # 判断用户脚本请求类型是否为空
            if meth is None:
                return jsonify(statusCode=RET.PARAMERR, msg="脚本请求为必填项")
            elif meth == "":
                return jsonify(statusCode=RET.PARAMERR, msg="脚本请求不能为空")

            try:
                try:
                    user_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == id).update(
                        {
                            "filename": filename,
                            "sc_ip": sc_ip,
                            "sc_path": sc_path,
                            "sc_praameter": sc_praameter,
                            "meth": meth,
                            "sc_name": sc_name,
                            "concurrency": concurrency,
                            "strategy": strategy,
                            "con_praameter": con_praameter
                        })
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

    # 对性能树的删除
    def delete(self):
        # 获取请求的json数据，返回字典
        req_dict = request.get_json()
        id = req_dict.get("id")  # 文件名id

        # 创建空列表 存储与id相同的父id
        tree_storagelist = []

        # 判断目录下面是否存在脚本或者目录，只能删除最低级
        try:
            # 查看是否有父id中是否存在被删除数据，存在证明不是末节分支
            tree_pidlist = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.pid == id)
            db.session.commit()
            for row in tree_pidlist:
                tree_storagelist.append(row.id)

        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            db.session.close()
            return jsonify(statusCode=RET.DATAERR, msg="查询父id失败")
        if len(tree_storagelist) > 0:
            return jsonify(statusCode=RET.OK, msg="请先删除子目录")
        else:
            # 删除文件
            try:
                tree_deleteid = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == id).delete()
                db.session.commit()
            except IntegrityError as e:
                # 数据库操作错误后的回滚
                db.session.rollback()
                current_app.logger.error(e)
                db.session.close()
                return jsonify(statusCode=RET.DATAERR, msg="删除失败")
            db.session.close()

            return jsonify(statusCode=RET.OK, msg="删除成功")
api.add_resource(PerformanceTree,'/PerformanceTree')


# 对性能树的查
class PerformanceTreeCheck(Resource):
    decorators = [authtoken.login_required]

    # method_decorators = [Interface_authority]
    def get(self):
        return '对性能树查询操作'
    def post(self):
        # 获取请求的json数据，返回字典
        tfdata = request.get_json()

        # 请求树权限接口 传入uid 返回树对应的权限
        tfurl = "http://127.0.0.1:5000/UserPerm/usertree"
        # tfdata = {"uid":3}
        tfr = requests.post(tfurl,json=tfdata)
        tfdic = tfr.json()

        # uid = req_dict.get("uid")  # 用户id


        check_list = []
        try:
            # user_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.uid == uid)
            user_list = db.session.query(db_mysql.Tree)
            db.session.commit()

        except IntegrityError as e:

            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            db.session.close()
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")
        db.session.close()
        #

        for raw in user_list:
            check_dic = {}
            check_dic["children"] = []
            check_dic["concurrency"] = raw.concurrency
            check_dic["strategy"] = raw.strategy
            check_dic["con_praameter"] = raw.con_praameter
            check_dic["sc_name"] = raw.sc_name
            check_dic["sc_praameter"] = raw.sc_praameter
            check_dic["sc_path"] = raw.sc_path
            check_dic["sc_ip"] = raw.sc_ip
            check_dic["uid"] = raw.uid
            check_dic["file_type"] = raw.file_type
            check_dic["pid"] = raw.pid
            check_dic["label"] = raw.filename
            check_dic["id"] = raw.id
            check_dic["meth"] = raw.meth

            # 如果 tfdic 为admin 是超管账号，展示所有树
            if tfdic == "admin":
                # 一级目录
                if check_dic["pid"] == 0:
                    check_dic["level"] = 1
                    check_dic["button_box_display"] = False
                    check_dic["tree_authority"] = tfdic
                    check_list.append(check_dic)
                # 遍历一级目录list，拿到list中的一级目录参数
                for x in check_list:
                    # 插入二级目录到1级目录的list中
                    if x["id"] == check_dic["pid"]:
                        check_dic["level"] = 2
                        check_dic["button_box_display"] = False
                        check_dic["tree_authority"] = tfdic
                        x["children"].append(check_dic)
                    # 遍历二级目录list 拿到list中的er级目录参数

                    for i in x["children"]:
                        # 插入三级目录到er级目录的list中
                        if i["id"] == check_dic["pid"]:
                            check_dic["level"] = 3
                            check_dic["button_box_display"] = False
                            check_dic["tree_authority"] = tfdic
                            i["children"].append(check_dic)
                        # 遍历三级目录list 拿到list中的er级目录参数
                        for z in i["children"]:
                            # 插入三级目录到er级目录的list中
                            if z["id"] == check_dic["pid"]:
                                check_dic["level"] = 4
                                check_dic["button_box_display"] = False
                                check_dic["tree_authority"] = tfdic
                                z["children"].append(check_dic)

            # 判断 '2' 在不在返回权限中 获取到用户拥有哪个项目的权限
            elif '2' in tfdic.keys():
                treedic = tfdic['2'][0]
                treelist = [k for k, v in treedic.items()]
                for a in treelist:
                    # 一级目录
                    if check_dic["pid"] == int(a):
                        check_dic["level"] = 1
                        check_dic["button_box_display"] = False
                        check_dic["tree_authority"] = tfdic['2'][0][a]
                        check_list.append(check_dic)
                    # 遍历一级目录list，拿到list中的一级目录参数
                    for x in check_list:
                        # 插入二级目录到1级目录的list中
                        if x["id"] == check_dic["pid"]:
                            check_dic["level"] = 2
                            check_dic["button_box_display"] = False
                            check_dic["tree_authority"] = tfdic['2'][0][a]
                            x["children"].append(check_dic)
                        # 遍历二级目录list 拿到list中的er级目录参数

                        for i in x["children"]:
                            # 插入三级目录到er级目录的list中
                            if i["id"] == check_dic["pid"]:
                                check_dic["level"] = 3
                                check_dic["button_box_display"] = False
                                check_dic["tree_authority"] = tfdic['2'][0][a]
                                i["children"].append(check_dic)
                            # 遍历三级目录list 拿到list中的er级目录参数
                            for z in i["children"]:
                                # 插入三级目录到er级目录的list中
                                if z["id"] == check_dic["pid"]:
                                    check_dic["level"] = 4
                                    check_dic["button_box_display"] = False
                                    check_dic["tree_authority"] = tfdic['2'][0][a]
                                    z["children"].append(check_dic)
        return jsonify(date=check_list, statusCode=RET.OK, msg="查询成功")


api.add_resource(PerformanceTreeCheck,'/PerformanceTreeCheck')


class test(Resource):
    # decorators = [ authtoken.login_required ]
    method_decorators = [Interface_authority]
    def post(self):
        print('test post')
        j_data = {
            'msg':'test post',
            'code': 200
        }
        return jsonify(j_data)

api.add_resource(test,'/test')