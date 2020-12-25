from flask import Blueprint, request, jsonify, current_app,session
from app.exts import db
from app import db_mysql
from app.api_status.response_code import RET
from sqlalchemy.exc import IntegrityError
import requests
from .Httpauth import authtoken ,serializer,Interface_authority #Interface_authority初始化验证接口权限函数
from flask_restful import Resource, Api
from app.aps_scheduler import schedulerdate, Url01, Url02, except_log

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
        file_type = req_dict.get("file_type")  # 文件 类型 1 为文件 2 为脚本 3 为 全链路脚本
        project_type = req_dict.get("project_type")  # 项目类型 2 为压测中心 3 为用例中心 4 为日志管理
        uid = req_dict.get("uid")  # 用户id

        operation_content = req_dict.get("operation_content") #用户操作内容

        operation_content = "新增树父节点:%s"%operation_content

        # putlog(self, tree_id, uid, operation_content, operation_result, project_type)
        # 判断文件名是否传值或者为空
        if filename is None:
            except_log().putlog(pid, uid, operation_content, 2,project_type)
            return jsonify(statusCode=RET.PARAMERR, msg="文件名字为必填项")
        elif filename == "":
            except_log().putlog(pid, uid, operation_content, 2,project_type)
            return jsonify(statusCode=RET.PARAMERR, msg="文件名字不能为空")

        # 判断父id是否传值或者为空
        if pid is None:
            except_log().putlog(pid, uid, operation_content, 2,project_type)
            return jsonify(statusCode=RET.PARAMERR, msg="父id为必填项")
        elif pid == "":
            except_log().putlog(pid, uid, operation_content, 2,project_type)
            return jsonify(statusCode=RET.PARAMERR, msg="父id不能为空")

        # 判断项目id是否传值或者为空
        if project_type is None:
            except_log().putlog(pid, uid, operation_content, 2,project_type)
            return jsonify(statusCode=RET.PARAMERR, msg="项目id为必填项")
        elif project_type == "":
            except_log().putlog(pid, uid, operation_content, 2,project_type)
            return jsonify(statusCode=RET.PARAMERR, msg="项目id不能为空")

        # 判断文件类型是否传值或者为空
        if file_type is None:
            except_log().putlog(pid, uid, operation_content, 2,project_type)
            return jsonify(statusCode=RET.PARAMERR, msg="文件类型为必填项")

        # 判断用户uid是否传值或者为空
        if uid is None:
            except_log().putlog(pid, uid, operation_content, 2,project_type)
            return jsonify(statusCode=RET.PARAMERR, msg="uid为必填项")

        try:
            try:
                treedata = db_mysql.Tree(filename=filename, pid=pid, file_type=file_type, uid=uid,project_type=project_type)
                db.session.add(treedata)
                db.session.flush()
                db.session.commit()
                zzid = treedata.id
            finally:
                db.session.close()

        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            db.session.close()
            except_log().putlog(pid, uid, operation_content, 2,project_type)
            return jsonify(statusCode=RET.DATAERR, msg="数据创建失败")
        db.session.close()

        j_data = {
            # "zzid" : zzid ,
            "statusstatusCode" : RET.OK,
            "msg" : "创建成功"
        }
        # print(zzid)
        except_log().putlog(pid, uid, operation_content, 1,project_type)
        return jsonify(statusCode = RET.OK,msg = "创建成功",zzid = zzid)

    # 对性能树的修改
    def put(self):
        # 获取请求的json数据，返回字典
        req_dict = request.get_json()

        id = req_dict.get("id")  # 文件名id
        file_type = req_dict.get("file_type")  # 文件 类型 1 为文件 2 为脚本 3为全链路脚本
        filename = req_dict.get("filename")  # 文件名
        # meth = req_dict.get("meth")  # 请求类型 post get
        # sc_ip = req_dict.get("sc_ip")  # 脚本ip
        # sc_path = req_dict.get("sc_path")  # 脚本路径
        sc_praameter = req_dict.get("sc_praameter")  # 脚本参数
        sc_name = req_dict.get("sc_name")  # 脚本名称
        concurrency = req_dict.get("concurrency")  # 并发数
        strategy = req_dict.get("strategy")  # 并发策略
        con_praameter = req_dict.get("con_praameter")  # 并发参数
        # test_env = req_dict.get("test_env")  # 压测环境  测试：0 预发：1 线上：2
        link_parameters = req_dict.get("link_parameters")  # 全链路参数

        project_type = req_dict.get("project_type")
        # tree_id = req_dict.get("tree_id")
        # uid = req_dict.get("uid")
        operation_content = req_dict.get("operation_content")
        operation_content =  "修改树:%s"%operation_content

        Permission_parameters = req_dict.get("Permission_parameters")
        uid = Permission_parameters["uid"]


        if id is None:
            except_log().putlog(id, uid, operation_content, 2,project_type)
            return jsonify(statusCode=RET.PARAMERR, msg="脚本id为必填项")
        # file_type == 1 为文件夹类型只能修改文件夹名称
        if file_type == 1 or file_type == 6 or file_type == 7:
            # 判断文件名是否传值或者为空
            if filename is None:
                except_log().putlog(id, uid, operation_content, 2, project_type)
                return jsonify(statusCode=RET.PARAMERR, msg="文件名字为必填项")
            elif filename == "":
                except_log().putlog(id, uid, operation_content, 2, project_type)
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
                except_log().putlog(id, uid, operation_content, 2, project_type)
                return jsonify(statusCode=RET.DATAERR, msg="修改失败")
        # file_type == 2 为脚本类型，可以修改脚本名，脚本ip，脚本路径，脚本参数
        elif file_type == 2 or file_type == 3 or file_type == 4 or file_type == 5 or file_type == 8 or file_type == 9:


            #判断链路参数是否传值
            if link_parameters is None:
                except_log().putlog(id, uid, operation_content, 2, project_type)
                return jsonify(statusCode=RET.PARAMERR, msg="链路参数为必填项")
            elif link_parameters == "":
                except_log().putlog(id, uid, operation_content, 2, project_type)
                return jsonify(statusCode=RET.PARAMERR, msg="链路参数不能为空")

            try:
                try:
                    user_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == id).update(
                        {
                            "sc_name": sc_name,
                            "concurrency": concurrency,
                            "strategy": strategy,
                            "con_praameter": con_praameter,
                            "link_parameters":link_parameters
                        })
                    db.session.commit()
                finally:
                    db.session.close()
            except IntegrityError as e:
                # 数据库操作错误后的回滚
                db.session.rollback()
                current_app.logger.error(e)
                db.session.close()

                except_log().putlog(id, uid, operation_content, 2, project_type)
                return jsonify(statusCode=RET.DATAERR, msg="修改失败")
        except_log().putlog(id, uid, operation_content, 1, project_type)
        return jsonify(statusCode=RET.OK, msg="修改成功")

    # 对性能树的删除
    def delete(self):
        # 获取请求的json数据，返回字典
        req_dict = request.get_json()
        id = req_dict.get("id")  # 文件名id

        project_type = req_dict.get("project_type")
        # tree_id = req_dict.get("tree_id")
        uid = req_dict.get("uid")
        operation_content = req_dict.get("operation_content")
        operation_content =  "删除树:%s"%operation_content

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
            except_log().putlog(id, uid, operation_content, 2, project_type)
            return jsonify(statusCode=RET.DATAERR, msg="查询父id失败")
        if len(tree_storagelist) > 0:
            except_log().putlog(id, uid, operation_content, 2, project_type)
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
                except_log().putlog(id, uid, operation_content, 2, project_type)
                return jsonify(statusCode=RET.DATAERR, msg="删除失败")
            db.session.close()
            except_log().putlog(id, uid, operation_content, 1, project_type)
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
        try:
            tfdata = request.get_json()
            uid = tfdata.get("uid")  # uid
            project_type = tfdata.get("project_type")
        except Exception as e:
            return jsonify(statusCode=RET.PARAMERR, msg="请查看是否传入json格式的参数")


        # 判断uid是否传值或者为空
        if uid is None:
            return jsonify(statusCode=RET.PARAMERR, msg="uid为必填项")
        elif uid == "":
            return jsonify(statusCode=RET.PARAMERR, msg="uid不能为空")


        # 请求树权限接口 传入uid 返回树对应的权限
        tfurl = "http://127.0.0.1:5000/UserPerm/usertree"
        # tfdata = {"uid":3}
        tfr = requests.post(tfurl,json=tfdata)
        tfdic = tfr.json()

        # uid = req_dict.get("uid")  # 用户id


        check_list = []
        try:
            # user_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.uid == uid)
            user_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.project_type == project_type)
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
            # check_dic["sc_name"] = raw.sc_name
            # check_dic["sc_praameter"] = raw.sc_praameter
            # check_dic["sc_path"] = raw.sc_path
            # check_dic["sc_ip"] = raw.sc_ip
            check_dic["uid"] = raw.uid
            check_dic["file_type"] = raw.file_type
            check_dic["pid"] = raw.pid
            check_dic["label"] = raw.filename
            check_dic["id"] = raw.id
            # check_dic["meth"] = raw.meth
            check_dic["test_env"] = raw.test_env
            check_dic["link_parameters"] = raw.link_parameters



            if tfdic["data"] == {} :
                return jsonify(statusCode=RET.NODATA, msg="没有压测树查看权限")
            # 如果 tfdic 为admin 是超管账号，展示所有树
            elif tfdic["data"] == "admin":
                # 一级目录
                if check_dic["pid"] == 0:
                    check_dic["level"] = 1
                    check_dic["button_box_display"] = False
                    check_dic["tree_authority"] = tfdic["data"]
                    check_list.append(check_dic)
                # 遍历一级目录list，拿到list中的一级目录参数
                for x in check_list:
                    # 插入二级目录到1级目录的list中
                    if x["id"] == check_dic["pid"]:
                        check_dic["level"] = 2
                        check_dic["button_box_display"] = False
                        check_dic["tree_authority"] = tfdic["data"]
                        x["children"].append(check_dic)
                    # 遍历二级目录list 拿到list中的er级目录参数

                    for i in x["children"]:
                        # 插入三级目录到er级目录的list中
                        if i["id"] == check_dic["pid"]:
                            check_dic["level"] = 3
                            check_dic["button_box_display"] = False
                            check_dic["tree_authority"] = tfdic["data"]
                            i["children"].append(check_dic)
                        # 遍历三级目录list 拿到list中的er级目录参数
                        for z in i["children"]:
                            # 插入三级目录到er级目录的list中
                            if z["id"] == check_dic["pid"]:
                                check_dic["level"] = 4
                                check_dic["button_box_display"] = False
                                check_dic["tree_authority"] = tfdic["data"]
                                z["children"].append(check_dic)
                            for y in z["children"]:
                                # 插入无wu级目录到er级目录的list中
                                if check_dic["file_type"] == 6:
                                    if y["id"] == check_dic["pid"]:
                                        check_dic["level"] = 5
                                        check_dic["button_box_display"] = False
                                        check_dic["tree_authority"] = tfdic["data"]
                                        y["children"].append(check_dic)
            else:
                if project_type == 2 :
                    # 判断 '2' 在不在返回权限中 获取到用户拥有哪个项目的权限
                    if "2" in tfdic["data"].keys():
                        treedic = tfdic["data"]["2"][0]
                        treelist = [k for k, v in treedic.items()]
                        for a in treelist:
                            # 一级目录
                            if check_dic["id"] == int(a):
                                check_dic["level"] = 1
                                check_dic["button_box_display"] = False
                                check_dic["tree_authority"] = tfdic["data"]['2'][0][a]
                                check_list.append(check_dic)
                        # 遍历一级目录list，拿到list中的一级目录参数
                        for x in check_list:
                            # 插入二级目录到1级目录的list中
                            if x["id"] == check_dic["pid"]:
                                check_dic["level"] = 2
                                check_dic["button_box_display"] = False
                                check_dic["tree_authority"] = x["tree_authority"]
                                x["children"].append(check_dic)
                            # 遍历二级目录list 拿到list中的er级目录参数

                            for i in x["children"]:
                                # 插入三级目录到er级目录的list中
                                if i["id"] == check_dic["pid"]:
                                    check_dic["level"] = 3
                                    check_dic["button_box_display"] = False
                                    check_dic["tree_authority"] = i["tree_authority"]
                                    i["children"].append(check_dic)
                                # 遍历三级目录list 拿到list中的er级目录参数
                                for z in i["children"]:
                                    # 插入三级目录到er级目录的list中
                                    if z["id"] == check_dic["pid"]:
                                        check_dic["level"] = 4
                                        check_dic["button_box_display"] = False
                                        check_dic["tree_authority"] = z["tree_authority"]
                                        z["children"].append(check_dic)
                                    for y in z["children"]:
                                        # 插入无wu级目录到er级目录的list中
                                        if check_dic["file_type"] == 6:
                                            if y["id"] == check_dic["pid"]:
                                                check_dic["level"] = 5
                                                check_dic["button_box_display"] = False
                                                check_dic["tree_authority"] = y["tree_authority"]
                                                y["children"].append(check_dic)
                if project_type == 3:
                    if "3" in tfdic["data"].keys():
                        treedic = tfdic["data"]["3"][0]
                        treelist = [k for k, v in treedic.items()]
                        for a in treelist:
                            # 一级目录
                            if check_dic["id"] == int(a):
                                check_dic["level"] = 1
                                check_dic["button_box_display"] = False
                                check_dic["tree_authority"] = tfdic["data"]['3'][0][a]
                                check_list.append(check_dic)
                        # 遍历一级目录list，拿到list中的一级目录参数
                        for x in check_list:
                            # 插入二级目录到1级目录的list中
                            if x["id"] == check_dic["pid"]:
                                check_dic["level"] = 2
                                check_dic["button_box_display"] = False
                                check_dic["tree_authority"] = x["tree_authority"]
                                x["children"].append(check_dic)
                            # 遍历二级目录list 拿到list中的er级目录参数

                            for i in x["children"]:
                                # 插入三级目录到er级目录的list中
                                if i["id"] == check_dic["pid"]:
                                    check_dic["level"] = 3
                                    check_dic["button_box_display"] = False
                                    check_dic["tree_authority"] = i["tree_authority"]
                                    i["children"].append(check_dic)
                                # 遍历三级目录list 拿到list中的er级目录参数
                                for z in i["children"]:
                                    # 插入三级目录到er级目录的list中
                                    if z["id"] == check_dic["pid"]:
                                        check_dic["level"] = 4
                                        check_dic["button_box_display"] = False
                                        check_dic["tree_authority"] = z["tree_authority"]
                                        z["children"].append(check_dic)
                                    for y in z["children"]:
                                        # 插入无wu级目录到er级目录的list中
                                        if check_dic["file_type"] == 6:
                                            if y["id"] == check_dic["pid"]:
                                                check_dic["level"] = 5
                                                check_dic["button_box_display"] = False
                                                check_dic["tree_authority"] = y["tree_authority"]
                                                y["children"].append(check_dic)

                if project_type == 5:
                    if "5" in tfdic["data"].keys():
                        treedic = tfdic["data"]["5"][0]
                        treelist = [k for k, v in treedic.items()]
                        for a in treelist:
                            # 一级目录
                            if check_dic["id"] == int(a):
                                check_dic["level"] = 1
                                check_dic["button_box_display"] = False
                                check_dic["tree_authority"] = tfdic["data"]['5'][0][a]
                                check_list.append(check_dic)
                        # 遍历一级目录list，拿到list中的一级目录参数
                        for x in check_list:
                            # 插入二级目录到1级目录的list中
                            if x["id"] == check_dic["pid"]:
                                check_dic["level"] = 2
                                check_dic["button_box_display"] = False
                                check_dic["tree_authority"] = x["tree_authority"]
                                x["children"].append(check_dic)
                            # 遍历二级目录list 拿到list中的er级目录参数

                            for i in x["children"]:
                                # 插入三级目录到er级目录的list中
                                if i["id"] == check_dic["pid"]:
                                    check_dic["level"] = 3
                                    check_dic["button_box_display"] = False
                                    check_dic["tree_authority"] = i["tree_authority"]
                                    i["children"].append(check_dic)
                                # 遍历三级目录list 拿到list中的er级目录参数
                                for z in i["children"]:
                                    # 插入三级目录到er级目录的list中
                                    if z["id"] == check_dic["pid"]:
                                        check_dic["level"] = 4
                                        check_dic["button_box_display"] = False
                                        check_dic["tree_authority"] = z["tree_authority"]
                                        z["children"].append(check_dic)
                                    for y in z["children"]:
                                        # 插入无wu级目录到er级目录的list中
                                        if check_dic["file_type"] == 6:
                                            if y["id"] == check_dic["pid"]:
                                                check_dic["level"] = 5
                                                check_dic["button_box_display"] = False
                                                check_dic["tree_authority"] = y["tree_authority"]
                                                y["children"].append(check_dic)
        return jsonify(date=check_list, statusCode=RET.OK, msg="查询成功")


api.add_resource(PerformanceTreeCheck,'/PerformanceTreeCheck')



# 对单节点的查询
class PerformanceTreeCheckOne(Resource):
    # decorators = [authtoken.login_required]
    # method_decorators = [Interface_authority]

    def get(self):
        test="单节点查询"
        return jsonify(test)
    def post(self):
        # 获取请求的json数据，返回字典
        try:
            tfdata = request.get_json()
            treeid = tfdata.get("treeid")  # uid
        except Exception as e:
            return jsonify(statusCode=RET.PARAMERR, msg="请查看是否传入json格式的参数")

        # 判断uid是否传值或者为空
        if treeid is None:
            return jsonify(statusCode=RET.PARAMERR, msg="treeid为必填项")
        elif treeid == "":
            return jsonify(statusCode=RET.PARAMERR, msg="treeid不能为空")

        check_list = []
        try:
            user_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == treeid)
            # user_list = db.session.query(db_mysql.Tree)
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
            check_dic["test_env"] = raw.test_env
            check_dic["link_parameters"] = raw.link_parameters

        return jsonify(date=check_dic, statusCode=RET.OK, msg="查询成功")




api.add_resource(PerformanceTreeCheckOne, '/PerformanceTreeCheckOne')


#------------------------------------ 用例脑图 ----------------------------------------
# 脑图 ：BrainMap
# 对脑图的 增删改
class BrainMap(Resource):
    # decorators = [authtoken.login_required]
    # method_decorators = [Interface_authority]

    def get(self):
        return '对脑图增删改操作'
    # 对脑图的新增
    def post(self):

        # 获取请求的json数据，返回字典
        req_dict = request.get_json()
        brainmapname = req_dict.get("brainmapname")  # 内容
        pid = req_dict.get("pid")  # 父id
        rdstatus = req_dict.get("rdstatus")  # 开发状态 1 为 pass 2 为 fail 3 为阻断 默认为空
        qastatus = req_dict.get("qastatus")  # 测试状态 1 为 pass 2 为 fail 3 为阻断 默认为空
        uid = req_dict.get("uid")  # 用户id
        tree_id = req_dict.get("tree_id")  # 树id

        # 判断父id是否传值或者为空
        if pid is None:
            return jsonify(statusCode=RET.PARAMERR, msg="父id为必填项")
        elif pid == "":
            return jsonify(statusCode=RET.PARAMERR, msg="父id不能为空")

        # 判断父id是否传值或者为空
        if tree_id is None:
            return jsonify(statusCode=RET.PARAMERR, msg="树id为必填项")
        elif tree_id == "":
            return jsonify(statusCode=RET.PARAMERR, msg="树id不能为空")

        # 判断用户uid是否传值或者为空
        if uid is None:
            return jsonify(statusCode=RET.PARAMERR, msg="uid为必填项")
        try:
            try:
                db.session.add(
                    db_mysql.Brainmap(brainmapname=brainmapname, pid=pid, rdstatus=rdstatus,qastatus=qastatus,
                                      uid=uid,tree_id=tree_id))
                db.session.commit()
            finally:
                db.session.close()

        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            db.session.close()
            return jsonify(statusCode=RET.DATAERR, msg="数据创建失败")

        # j_data = {
        #     "statusstatusCode" : RET.OK,
        #     "msg" : "创建成功"
        # }
        return jsonify(statusCode = RET.OK,msg = "添加成功")

    # 对性能树的修改
    def put(self):
        # 获取请求的json数据，返回字典
        req_dict = request.get_json()

        id = req_dict.get("id")  # 文件名id
        brainmapname = req_dict.get("brainmapname")  # 内容
        rdstatus = req_dict.get("rdstatus")  # 开发状态 1 为 pass 2 为 fail 3 为阻断 默认为空
        qastatus = req_dict.get("qastatus")  # 测试状态 1 为 pass 2 为 fail 3 为阻断 默认为空
        uid = req_dict.get("uid")  # 用户id

        try:
            try:
                user_list = db.session.query(db_mysql.Brainmap).filter(db_mysql.Brainmap.id == id).update(
                    {
                        "brainmapname": brainmapname,
                        "rdstatus": rdstatus,
                        "qastatus": qastatus,
                        "uid": uid
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

        map_storagelist = []
        delist = []
        def deid(map_id):
            # 判断目录下面是否存在脚本或者目录，只能删除最低级
            try:
                # 查看是否有父id中是否存在被删除数据，存在证明不是末节分支
                map_pidlist = db.session.query(db_mysql.Brainmap).filter(db_mysql.Brainmap.pid == map_id)
                db.session.commit()
                for row in map_pidlist:
                    map_storagelist.append(row.id)
                    delist.append(row.id)

            except IntegrityError as e:
                # 数据库操作错误后的回滚
                db.session.rollback()

                current_app.logger.error(e)
                db.session.close()
                return jsonify(statusCode=RET.DATAERR, msg="查询父id失败")
        deid(id)
        while True:
            if len(map_storagelist) > 0:
                for i in (map_storagelist):
                    deid(i)
                    map_storagelist.remove(i)
                # return jsonify(statusCode=RET.OK, msg="请先删除子目录")
            else:
                break
        delist.append(id)


        # 删除文件
        try:
            tree_deleteid = db.session.query(db_mysql.Brainmap).filter(db_mysql.Brainmap.id.in_(delist)).delete(synchronize_session=False)
            db.session.commit()
        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            db.session.close()
            return jsonify(statusCode=RET.DATAERR, msg="删除失败")
        print(delist)
        return jsonify(statusCode=RET.OK, msg="删除成功")

        # return jsonify(statusCode=RET.OK, msg="删除成功")
api.add_resource(BrainMap,'/BrainMap')


# 对脑图的查
class BrainMapCheck(Resource):
    # decorators = [authtoken.login_required]

    # method_decorators = [Interface_authority]
    def get(self):
        return '对性能树查询操作'
    def post(self):
        # 获取请求的json数据，返回字典
        try:
            tfdata = request.get_json()
            tree_id = tfdata.get("tree_id")  # uid

        except Exception as e:
            return jsonify(statusCode=RET.PARAMERR, msg="请查看是否传入json格式的参数")


        # 判断uid是否传值或者为空
        if tree_id is None:
            return jsonify(statusCode=RET.PARAMERR, msg="tree_id为必填项")
        elif tree_id == "":
            return jsonify(statusCode=RET.PARAMERR, msg="tree_id不能为空")

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
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")

        check_list = []
        for raw in user_list:
            check_dic = {}
            check_dic["children"] = []
            check_dic["id"] = raw.id
            check_dic["pid"] = raw.pid
            check_dic["brainmapname"] = raw.brainmapname
            # check_dic["rdstatus"] = raw.rdstatus
            check_dic["qastatus"] = raw.qastatus
            check_dic["tree_id"] = raw.tree_id
            check_dic["uid"] = raw.uid


            check_list.append(check_dic)

        # 插入根节点
        check_list.insert(0, {"id": 0, "name": "root","children":[]})

        # 建立索引
        index = {check_list[i]["id"]: i for i in range(len(check_list))}
        # check_list[i]的pid索引对应的节点，添加子节点check_list[i]
        for i in range(1, len(check_list)):
            check_list[index[check_list[i]["pid"]]]["children"].append(check_list[i])
        return jsonify(date=check_list[0]["children"], statusCode=RET.OK, msg="查询成功")

api.add_resource(BrainMapCheck, '/BrainMapCheck')

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