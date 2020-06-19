from flask import (Blueprint, flash, redirect, render_template, request, session, url_for, jsonify, current_app)
from flask_restful import Resource, Api
from first_app.exts import db
from first_app import db_mysql
from first_app.api_status.response_code import RET
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from .Httpauth  import authtoken ,serializer,Interface_authority #Interface_authority初始化验证接口权限函数

AuthorityApi = Blueprint('AuthorityApi', __name__, url_prefix='/AuthorityApi')
api = Api(AuthorityApi)




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





class AuthProject(Resource):    # 项目工程的增查
    # 新增项目工程
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        project_name = req_dict.get("project_name")   # 项目工程id

        # 判断项目工程名不能重复、是否传值和为空
        pro_list = db.session.query(db_mysql.Project)
        db.session.commit()
        for i in pro_list:
            if i.project_name == project_name:
                return jsonify(statusCode=RET.PARAMERR, msg="项目工程名不能重复")
        if project_name is None:
            return jsonify(statusCode=RET.PARAMERR, msg="项目工程名为必填项")
        elif project_name == "":
            return jsonify(statusCode=RET.PARAMERR, msg="项目工程名不能为空")

        try:
            db.session.add(
                db_mysql.Group(project_name=project_name))
            db.session.commit()

        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="数据创建失败")
        db.session.close()
        return jsonify(statusCode=RET.OK, msg="创建成功")

    # 查询不包含权限管理的工程名
    def get(self):

        check_list = []

        try:
            pro_list = db.session.query(db_mysql.Project).offset(1)
            db.session.commit()
        except IntegrityError as e:

            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")
        db.session.close()

        for raw in pro_list:
            check_dic = {}
            check_dic["id"] = raw.id
            check_dic["project_name"] = raw.project_name

            check_list.append(check_dic)

        return jsonify(data=check_list, statusCode=RET.OK, msg="查询成功")


class AuthGroup(Resource):  # 组的增删改查
    # 查询
    def get(self):

        check_list = []

        try:
            group_list = db.session.query(db_mysql.Group)
            db.session.commit()
        except IntegrityError as e:

            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")
        db.session.close()

        for raw in group_list:
            check_dic = {}
            check_dic["id"] = raw.id
            check_dic["group_name"] = raw.group_name
            check_dic["project_id"] = raw.project_id

            check_list.append(check_dic)

        return jsonify(data=check_list, statusCode=RET.OK, msg="查询成功")

    # 新增
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        g_name = req_dict.get("group_name")  # 组名
        project_id = req_dict.get("project_id")   # 项目工程id

        # 判断组名不能重复、是否传值和为空
        group_list = db.session.query(db_mysql.Group)
        db.session.commit()
        for i in group_list:
            if i.group_name == g_name:
                return jsonify(statusCode=RET.PARAMERR, msg="组名字不能重复")
        if g_name is None:
            return jsonify(statusCode=RET.PARAMERR, msg="组名字为必填项")
        elif g_name == "":
            return jsonify(statusCode=RET.PARAMERR, msg="组名字不能为空")

        try:
            db.session.add(
                db_mysql.Group(group_name=g_name, project_id=project_id))
            db.session.commit()

        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="数据创建失败")
        db.session.close()
        return jsonify(statusCode=RET.OK, msg="创建成功")

    # 修改
    def put(self):
        # 获取请求的json数据，返回字典
        req_dict = request.get_json()
        group_id = req_dict.get("group_id")  # 组id
        group_name = req_dict.get("group_name")     # 组名称
        project_id = req_dict.get("project_id")   # 工程项目id

        try:
            g_list = db.session.query(db_mysql.Group).filter(db_mysql.Group.id == group_id).update(
                {
                    "group_name": group_name,
                    "project_id": project_id
                })
            db.session.commit()
        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="修改失败")
        db.session.close()
        return jsonify(statusCode=RET.OK, msg="修改成功")

    # 删除
    # def delete(self):
    #     # 获取请求的json数据，返回字典
    #     req_dict = request.get_json()
    #     group_id = req_dict.get("group_id")  # 组id
    #
    #     # 创建空列表 存储id
    #     g_list = []
    #
    #     # 判断组列表里是否存在查询的id
    #     try:
    #         # 取出表
    #         group_list = db.session.query(db_mysql.Group)
    #         db.session.commit()
    #         for row in group_list:
    #             g_list.append(row.id)
    #
    #     except IntegrityError as e:
    #         # 数据库操作错误后的回滚
    #         db.session.rollback()
    #         current_app.logger.error(e)
    #         return jsonify(statusCode=RET.DATAERR, msg="查询id失败")
    #     else:
    #         # 删除文件
    #         try:
    #             group_deleteid = db.session.query(db_mysql.Group).filter(db_mysql.Group.id == group_id).delete()
    #             db.session.commit()
    #         except IntegrityError as e:
    #             # 数据库操作错误后的回滚
    #             db.session.rollback()
    #             current_app.logger.error(e)
    #             return jsonify(statusCode=RET.DATAERR, msg="删除失败")
    #         db.session.close()
    #
    #         return jsonify(statusCode=RET.OK, msg="删除成功")


class AuthEnvIp(Resource):  # ip的增删改查
    # 新增
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        Ip_type = req_dict.get("ip_type")  # ip类型
        Ip_name = req_dict.get("ip_name")  # ip名称

        # 判断ip名不能重复、是否传值和为空
        ip_list = db.session.query(db_mysql.Envip)
        db.session.commit()
        for i in ip_list:
            if i.ip_name == Ip_name:
                return jsonify(statusCode=RET.PARAMERR, msg="ip已存在")
        if Ip_name is None:
            return jsonify(statusCode=RET.PARAMERR, msg="ip名字为必填项")
        elif Ip_name == "":
            return jsonify(statusCode=RET.PARAMERR, msg="ip名字不能为空")

        try:
            db.session.add(
                db_mysql.Envip(ip_name=Ip_name, ip_type=Ip_type))
            db.session.commit()

        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="数据创建失败")
        db.session.close()
        return jsonify(statusCode=RET.OK, msg="创建成功")

    # 查询
    def get(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        Ip_type = req_dict.get("ip_type")  # ip类型

        check_list = []

        try:
            ip_list = db.session.query(db_mysql.Envip).filter(db_mysql.Envip.ip_type == Ip_type)
            db.session.commit()
        except IntegrityError as e:

            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")
        db.session.close()

        for raw in ip_list:
            check_dic = {}
            check_dic["id"] = raw.id
            check_dic["ip_name"] = raw.ip_name

            check_list.append(check_dic)

        return jsonify(data=check_list, statusCode=RET.OK, msg="查询成功")

    # 修改
    def put(self):
        # 获取请求的json数据，返回字典
        req_dict = request.get_json()

        Ip_id = req_dict.get("ip_id")  # ip的id
        Ip_name = req_dict.get("ip_name")  # ip名字
        Ip_type = req_dict.get("ip_type")  # ip类型

        try:
            ip_list = db.session.query(db_mysql.Envip).filter(db_mysql.Envip.id == Ip_id).update(
                {
                    "ip_name": Ip_name,
                    "ip_type": Ip_type
                })
            db.session.commit()
        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="修改失败")
        db.session.close()
        return jsonify(statusCode=RET.OK, msg="修改成功")

    # 删除
    def delete(self):
        # 获取请求的json数据，返回字典
        req_dict = request.get_json()
        ip_id = req_dict.get("ip_id")  # ip id

        # 创建空列表 存储id
        ip_list = []

        # 判断组列表里是否存在查询的id
        try:
            # 取出表
            iplist = db.session.query(db_mysql.Envip)
            db.session.commit()
            for row in iplist:
                ip_list.append(row.id)

        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="查询id失败")
        else:
            # 删除文件
            try:
                ip_deleteid = db.session.query(db_mysql.Envip).filter(db_mysql.Envip.id == ip_id).delete()
                db.session.commit()
            except IntegrityError as e:
                # 数据库操作错误后的回滚
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(statusCode=RET.DATAERR, msg="删除失败")
            db.session.close()

            return jsonify(statusCode=RET.OK, msg="删除成功")


class AuthEnvIpInfo(Resource):  # 查询所有ip类型和ip列表
    # 查询
    def get(self):
        type_dic = {}
        type_list = []
        iptype_list = [0, 1, 2]
        for iptype in iptype_list:
            try:
                ip_list = db.session.query(db_mysql.Envip).filter(db_mysql.Envip.ip_type == iptype)
                db.session.commit()
            except IntegrityError as e:

                # 数据库操作错误后的回滚
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(statusCode=RET.DATAERR, msg="查询失败")
            db.session.close()

            for raw in ip_list:
                check_dic = {}
                check_dic["id"] = raw.id
                check_dic["ip_name"] = raw.ip_name

                type_list.append(check_dic)
                type_dic[iptype] = type_list

        return jsonify(data=type_dic, statusCode=RET.OK, msg="查询成功")


class AuthFunction(Resource):  # 权限的增删改查
    # 新增
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        f_name = req_dict.get("func_name")  # 权限名称
        port_name = req_dict.get("port_name")   # 接口名称
        request_type = req_dict.get("request_type")   # 请求方式

        # 判断权限名不能重复、是否传值和为空
        func_list = db.session.query(db_mysql.Function)
        db.session.commit()
        for i in func_list:
            if i.func_name == f_name:
                return jsonify(statusCode=RET.PARAMERR, msg="权限名称已存在")
        if f_name is None:
            return jsonify(statusCode=RET.PARAMERR, msg="权限名称为必填项")
        elif f_name == "":
            return jsonify(statusCode=RET.PARAMERR, msg="权限名称不能为空")

        try:
            db.session.add(
                db_mysql.Function(func_name=f_name, port_name=port_name, request_type=request_type))
            db.session.commit()

        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="数据创建失败")
        db.session.close()
        return jsonify(statusCode=RET.OK, msg="创建成功")

    # 查询
    def get(self):
        check_list = []

        try:
            func_list = db.session.query(db_mysql.Function).offset(1)
            db.session.commit()
        except IntegrityError as e:

            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")
        db.session.close()

        for raw in func_list:
            check_dic = {}
            check_dic["id"] = raw.id
            check_dic["func_name"] = raw.func_name

            check_list.append(check_dic)

        return jsonify(data=check_list, statusCode=RET.OK, msg="查询成功")

    # 修改
    def put(self):
        # 获取请求的json数据，返回字典
        req_dict = request.get_json()

        func_id = req_dict.get("func_id")  # 权限id
        f_name = req_dict.get("func_name")  # 权限名字
        port_name = req_dict.get("port_name")  # 接口名称
        request_type = req_dict.get("request_type")  # 请求方式

        try:
            func_list = db.session.query(db_mysql.Function).filter(db_mysql.Function.id == func_id).update(
                {
                    "func_name": f_name,
                    "port_name": port_name,
                    "request_type": request_type
                })
            db.session.commit()
        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="修改失败")
        db.session.close()
        return jsonify(statusCode=RET.OK, msg="修改成功")

    # 删除
    def delete(self):
        # 获取请求的json数据，返回字典
        req_dict = request.get_json()
        func_id = req_dict.get("func_id")  # 功能权限id

        # 创建空列表 存储id
        func_list = []

        # 判断组列表里是否存在查询的id
        try:
            # 取出表
            f_list = db.session.query(db_mysql.Function)
            db.session.commit()
            for row in f_list:
                func_list.append(row.id)

        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="查询id失败")
        else:
            # 删除文件
            try:
                func_delete = db.session.query(db_mysql.Function).filter(db_mysql.Function.id == func_id).delete()
                db.session.commit()
            except IntegrityError as e:
                # 数据库操作错误后的回滚
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(statusCode=RET.DATAERR, msg="删除失败")
            db.session.close()

            return jsonify(statusCode=RET.OK, msg="删除成功")


class AuthUser(Resource):   # 用户的增删改查
    # 查询
    def get(self):

        check_list = []

        try:
            user_list = db.session.query(db_mysql.User)
            db.session.commit()
        except IntegrityError as e:

            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")
        db.session.close()

        for raw in user_list:
            check_dic = {}
            check_dic["id"] = raw.id
            check_dic["username"] = raw.username
            check_dic["name"] = raw.name

            check_list.append(check_dic)

        return jsonify(data=check_list, statusCode=RET.OK, msg="查询成功")

    # 新增
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        username = req_dict.get("username")  # 账号
        name = req_dict.get("name")    # 用户姓名
        ip_type = req_dict.get("ip_type")   # 授权环境类型
        password = '123456'   # 默认密码123456

        # 判断用户名不能重复、是否传值和为空
        user_list = db.session.query(db_mysql.User)
        db.session.commit()
        for i in user_list:
            if i.username == username:
                return jsonify(statusCode=RET.PARAMERR, msg="用户名已存在")
        if username is None:
            return jsonify(statusCode=RET.PARAMERR, msg="用户名为必填项")
        elif username == "":
            return jsonify(statusCode=RET.PARAMERR, msg="用户名不能为空")

        # 判断姓名是否传值和为空
        if name is None:
            return jsonify(statusCode=RET.PARAMERR, msg="姓名为必填项")
        elif name == "":
            return jsonify(statusCode=RET.PARAMERR, msg="姓名不能为空")

        # 判断是否选择授权环境
        if ip_type is None:
            return jsonify(statusCode=RET.PARAMERR, msg="授权环境为必选项")
        elif ip_type == "":
            return jsonify(statusCode=RET.PARAMERR, msg="授权环境不能为空")

        try:
            db.session.add(
                db_mysql.User(username=username, password=generate_password_hash(password), name=name, ip_type=ip_type))
            db.session.commit()

        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="数据创建失败")
        db.session.close()
        return jsonify(statusCode=RET.OK, msg="创建成功")

    # 修改
    def put(self):
        # 获取请求的json数据，返回字典
        req_dict = request.get_json()

        uid = req_dict.get("uid")  # 用户id
        name = req_dict.get("name")   # 用户姓名
        password = req_dict.get("password")  # 用户密码
        type = req_dict.get("type")   # 1为修改名字，2为修改密码
        password = str(password)
        if type == 1:
            try:
                u_list = db.session.query(db_mysql.User).filter(db_mysql.User.id == uid).update(
                    {
                        "name": name
                    })
                db.session.commit()
            except IntegrityError as e:
                # 数据库操作错误后的回滚
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(statusCode=RET.DATAERR, msg="修改失败")
            db.session.close()
            return jsonify(statusCode=RET.OK, msg="修改成功")
        else:
            try:
                u_list = db.session.query(db_mysql.User).filter(db_mysql.User.id == uid).update(
                    {
                        "password": generate_password_hash(password)
                    })
                db.session.commit()
            except IntegrityError as e:
                # 数据库操作错误后的回滚
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(statusCode=RET.DATAERR, msg="修改失败")
            db.session.close()
            return jsonify(statusCode=RET.OK, msg="修改成功")

    # 删除
    def delete(self):
        # 获取请求的json数据，返回字典
        req_dict = request.get_json()
        uid = req_dict.get("uid")  # 用户id

        # 创建空列表 存储id
        func_list = []

        # 判断组列表里是否存在查询的id
        try:
            # 取出表
            u_list = db.session.query(db_mysql.User)
            db.session.commit()
            for row in u_list:
                func_list.append(row.id)

        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="查询id失败")
        else:
            # 删除文件
            try:
                # 删除user、groupuser、unserfunc表
                delete = db.session.query(db_mysql.User).filter(db_mysql.User.id == uid).delete()
                delete = db.session.query(db_mysql.GroupUser).filter(db_mysql.GroupUser.uid == uid).delete()
                delete = db.session.query(db_mysql.UserFunc).filter(db_mysql.UserFunc.uid == uid).delete()
                db.session.commit()
            except IntegrityError as e:
                # 数据库操作错误后的回滚
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(statusCode=RET.DATAERR, msg="删除失败")
            db.session.close()

            return jsonify(statusCode=RET.OK, msg="删除成功")


class AuthUserInfo(Resource):
    # 查询uid、uname、ip_type
    def get(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        uid = req_dict.get("uid")  # 用户id

        check_list = []

        try:
            u_list = db.session.query(db_mysql.User).filter(db_mysql.User.id == uid)
            db.session.commit()
        except IntegrityError as e:

            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")
        db.session.close()

        for raw in u_list:
            check_dic = {}
            check_dic["id"] = raw.id
            check_dic["name"] = raw.name
            check_dic["username"] = raw.username
            check_dic["ip_type"] = raw.ip_type

            check_list.append(check_dic)

        return jsonify(data=check_list, statusCode=RET.OK, msg="查询成功")

    # 修改授权环境
    def put(self):
        # 获取请求的json数据，返回字典
        req_dict = request.get_json()

        uid = req_dict.get("uid")  # 用户id
        ip_type = req_dict.get("ip_type")  # 授权环境

        try:
            u_list = db.session.query(db_mysql.User).filter(db_mysql.User.id == uid).update(
                {
                    "ip_type": ip_type
                })
            db.session.commit()
        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="修改失败")
        db.session.close()
        return jsonify(statusCode=RET.OK, msg="修改成功")


class AuthUserGroupAdd(Resource):
    # 员工详情页，添加组时，组的查询接口，显示未加入的组
    def get(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        uid = req_dict.get("uid")  # 用户id

        check_list = []

        try:
            # 从GroupUser表中取出请求uid的数据
            usergroup_list = db.session.query(db_mysql.GroupUser).filter(db_mysql.GroupUser.uid == uid)
            # 从Group表中取出所有数据
            group_list = db.session.query(db_mysql.Group)

            db.session.commit()
        except IntegrityError as e:

            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")
        db.session.close()

        a_list = []
        b_list = []
        for x in usergroup_list:
            a_list.append(x.group_id)

        for y in group_list:
            b_list.append(y.id)

        # 把a_list和b_list里的数据删除重复的
        i = 0
        count = 0
        c_list = a_list+b_list
        while i < len(c_list):
            value = c_list[i]
            count = c_list[0:len(c_list)].count(value)
            if 1 < count:
                j = 0
                while j < count:
                    del c_list[c_list.index(value)]
                    j += 1
                i = i
            else:
                i += 1

        # 将去重后的c_list里的group_id，从Group表里取对应的name
        for z in c_list:
            z_list = db.session.query(db_mysql.Group).filter(db_mysql.Group.id == z)
            print(z_list)
            for raw in z_list:
                check_dic = {}
                check_dic["id"] = raw.id
                check_dic["group_name"] = raw.group_name

                check_list.append(check_dic)

        return jsonify(data=check_list, statusCode=RET.OK, msg="查询成功")


class AuthUserGroup(Resource):  # 用户对组的增删查
    # 新增
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        uid = req_dict.get("uid")  # 用户id
        group_id = req_dict.get("group_id")  # 所属组的id

        # 判断用户添加的组是否已存在
        user_list = db.session.query(db_mysql.GroupUser).filter(db_mysql.GroupUser.uid == uid)
        db.session.commit()
        for i in user_list:
            if i.group_id == group_id:
                return jsonify(statusCode=RET.PARAMERR, msg="该组已存在")

        # 判断用户id是否传值和为空
        if uid is None:
            return jsonify(statusCode=RET.PARAMERR, msg="uid为空")
        elif uid == "":
            return jsonify(statusCode=RET.PARAMERR, msg="uid为空")

        # 判断组id是否传值和为空
        if group_id is None:
            return jsonify(statusCode=RET.PARAMERR, msg="group_id为空")
        elif group_id == "":
            return jsonify(statusCode=RET.PARAMERR, msg="group_id为空")


        try:
            db.session.add(
                db_mysql.GroupUser(uid=uid, group_id=group_id))
            db.session.commit()

        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="数据创建失败")
        db.session.close()
        return jsonify(statusCode=RET.OK, msg="添加成功")

    # 查询
    def get(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        uid = req_dict.get("uid")  # 用户id

        check_list = []

        try:
            u_list = db.session.query(db_mysql.GroupUser).filter(db_mysql.GroupUser.uid == uid)
            db.session.commit()
        except IntegrityError as e:

            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")
        db.session.close()

        for raw in u_list:
            check_dic = {}
            check_dic["group_id"] = raw.group_id
            # 拿到组id
            group_id = raw.group_id
            # 去组表里查对应的组名称
            g_list = db.session.query(db_mysql.Group).filter(db_mysql.Group.id == group_id)
            for i in g_list:
                group_name = i.group_name
                check_dic["group_name"] = group_name

            check_list.append(check_dic)

        return jsonify(data=check_list, statusCode=RET.OK, msg="查询成功")

    # 删除
    def delete(self):
        # 获取请求的json数据，返回字典
        req_dict = request.get_json()
        uid = req_dict.get("uid")  # 用户id
        group_id = req_dict.get("group_id")  # 组id

        # 删除某个用户下的某个组
        try:
            delete = db.session.query(db_mysql.GroupUser).filter(db_mysql.GroupUser.group_id == group_id,
                                                                 db_mysql.GroupUser.uid == uid).delete()
            db.session.commit()
        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="删除失败")
        db.session.close()

        return jsonify(statusCode=RET.OK, msg="删除成功")


class AuthGroupUser(Resource):  # 组对用户的增删查
    # 新增
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        uid = req_dict.get("uid")  # 用户id
        group_id = req_dict.get("group_id")  # 所属组的id

        # 判断组添加的用户是否已存在
        # g_list = db.session.query(db_mysql.GroupUser).filter(db_mysql.GroupUser.group_id == group_id)
        # db.session.commit()
        # for i in g_list:
        #     if i.uid == uid:
        #         return jsonify(statusCode=RET.PARAMERR, msg="用户已存在")

        # 判断用户id是否传值和为空
        if uid is None:
            return jsonify(statusCode=RET.PARAMERR, msg="uid为空")
        elif uid == "":
            return jsonify(statusCode=RET.PARAMERR, msg="uid为空")

        # 判断组id是否传值和为空
        if group_id is None:
            return jsonify(statusCode=RET.PARAMERR, msg="group_id为空")
        elif group_id == "":
            return jsonify(statusCode=RET.PARAMERR, msg="group_id为空")

        try:
            db.session.add(
                db_mysql.GroupUser(uid=uid, group_id=group_id))
            db.session.commit()

        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="数据创建失败")
        db.session.close()
        return jsonify(statusCode=RET.OK, msg="创建成功")

    # 查询
    def get(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        group_id = req_dict.get("group_id")  # 用户id

        check_list = []

        try:
            g_list = db.session.query(db_mysql.GroupUser).filter(db_mysql.GroupUser.group_id == group_id)
            db.session.commit()
        except IntegrityError as e:

            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")
        db.session.close()

        for raw in g_list:
            check_dic = {}
            check_dic["uid"] = raw.uid
            # 拿到用户id
            uid = raw.uid
            # 去用户表里查对应的组名称
            u_list = db.session.query(db_mysql.User).filter(db_mysql.User.id == uid)
            for i in u_list:
                u_name = i.name
                us_name = i.username
                check_dic["name"] = u_name
                check_dic["username"] = us_name

            check_list.append(check_dic)

        return jsonify(data=check_list, statusCode=RET.OK, msg="查询成功")

    # 删除
    def delete(self):
        # 获取请求的json数据，返回字典
        req_dict = request.get_json()
        uid = req_dict.get("uid")  # 用户id
        group_id = req_dict.get("group_id")  # 组id

        # 删除某个组下的某个用户
        try:
            delete = db.session.query(db_mysql.GroupUser).filter(db_mysql.GroupUser.group_id == group_id,
                                                                 db_mysql.GroupUser.uid == uid).delete()
            db.session.commit()
        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="删除失败")
        db.session.close()

        return jsonify(statusCode=RET.OK, msg="删除成功")


class AuthCheckGroupUser(Resource):  # 组/项目，添加用户时判断用户是否已存在
    # 校验用户是否已存在
    def get(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        uid = req_dict.get("uid")  # 用户id
        group_id = req_dict.get("group_id")  # 组的id
        tree_id = req_dict.get("tree_id")   # 项目id
        type =req_dict.get("type")  # 1为组，2为项目

        if type == 1:
            # try:
            # 判断组添加的用户是否已存在
            g_list = db.session.query(db_mysql.GroupUser).filter(db_mysql.GroupUser.group_id == group_id)
            db.session.commit()
            for i in g_list:
                if i.uid == uid:
                    return jsonify(statusCode=RET.PARAMERR, msg="用户已存在")
                else:
                    return jsonify(statusCode=RET.OK, msg="验证通过")

            # except AttributeError as e:
            #     # 数据库操作错误后的回滚
            #     db.session.rollback()
            #     current_app.logger.error(e)
            #     return jsonify(statusCode=RET.DATAERR, msg="type对应关系错误")
            # db.session.close()
        else:
            # try:
            # 判断项目添加的用户是否已存在
            t_list = db.session.query(db_mysql.UserFunc).filter(db_mysql.UserFunc.tree_id == tree_id)
            db.session.commit()
            for i in t_list:
                if i.uid == uid:
                    return jsonify(statusCode=RET.PARAMERR, msg="用户已存在")
                else:
                    return jsonify(statusCode=RET.OK, msg="验证通过")

            # except AttributeError as e:
            #     # 数据库操作错误后的回滚
            #     db.session.rollback()
            #     current_app.logger.error(e)
            #     return jsonify(statusCode=RET.DATAERR, msg="type对应关系错误")
            # db.session.close()


class AuthGroupUserAdd(Resource):
    # 组添加员工时，搜索已有员工
    def get(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        username = req_dict.get("username")  # 用户名

        check_list = []

        if username == "":
            try:
                user_list = db.session.query(db_mysql.User)
                db.session.commit()
            except IntegrityError as e:

                # 数据库操作错误后的回滚
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(statusCode=RET.DATAERR, msg="查询失败")
            db.session.close()

            for raw in user_list:
                check_dic = {}
                check_dic["id"] = raw.id
                check_dic["username"] = raw.username
                check_dic["name"] = raw.name

                check_list.append(check_dic)

            return jsonify(data=check_list, statusCode=RET.OK, msg="查询成功")
        else:
            try:
                # u_list = db.session.query(db_mysql.User).filter_by(db_mysql.User.username == username).\
                #     filter(db_mysql.User.username.like("%" + username + "%"))
                u_list = db.session.query(db_mysql.User).filter(db_mysql.User.username.like("%" + username + "%"))
                db.session.commit()
            except IntegrityError as e:

                # 数据库操作错误后的回滚
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(statusCode=RET.DATAERR, msg="查询失败")
            db.session.close()

            for raw in u_list:
                check_dic = {}
                check_dic["id"] = raw.id
                check_dic["name"] = raw.name
                check_dic["username"] = raw.username

                check_list.append(check_dic)

            return jsonify(data=check_list, statusCode=RET.OK, msg="查询成功")


class AuthGroupFunc(Resource):  # 组权限的增删改查
    decorators = [ authtoken.login_required ]
    method_decorators = [Interface_authority]

    # 项目下添加某个组
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        group_id = req_dict.get("group_id")  # 组的id
        tree_id = req_dict.get("tree_id")  # 项目id
        func_id = req_dict.get("func_id")   # 功能权限id

        # 判断组添加的用户是否已存在
        g_list = db.session.query(db_mysql.GroupFunc).filter(db_mysql.GroupFunc.tree_id == tree_id)
        db.session.commit()
        for i in g_list:
            if i.group_id == group_id:
                return jsonify(statusCode=RET.PARAMERR, msg="组已存在")

        # 判断项目id是否传值和为空
        if tree_id is None:
            return jsonify(statusCode=RET.PARAMERR, msg="tree_id为空")
        elif tree_id == "":
            return jsonify(statusCode=RET.PARAMERR, msg="tree_id为空")

        # 判断组id是否传值和为空
        if group_id is None:
            return jsonify(statusCode=RET.PARAMERR, msg="group_id为空")
        elif group_id == "":
            return jsonify(statusCode=RET.PARAMERR, msg="group_id为空")

        try:
            func_id = str(func_id)
            db.session.add(
                db_mysql.GroupFunc(group_id=group_id, tree_id=tree_id, func_id=func_id))
            db.session.commit()

        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="数据创建失败")
        db.session.close()
        return jsonify(statusCode=RET.OK, msg="创建成功")

    # 查询tree下所有组列表
    def get(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        tree_id = req_dict.get("tree_id")  # 项目id

        check_list = []

        try:
            g_list = db.session.query(db_mysql.GroupFunc).filter(db_mysql.GroupFunc.tree_id == tree_id)
            db.session.commit()
        except IntegrityError as e:

            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")
        db.session.close()

        for raw in g_list:
            check_dic = {}
            check_dic["func_id"] = raw.func_id
            check_dic["group_id"] = raw.group_id
            # 拿到组id
            group_id = raw.group_id
            # 去组表里查对应的组名称
            u_list = db.session.query(db_mysql.Group).filter(db_mysql.Group.id == group_id)
            for i in u_list:
                u_name = i.group_name
                check_dic["group_name"] = u_name
            check_list.append(check_dic)

        return jsonify(data=check_list, statusCode=RET.OK, msg="查询成功")

    # 修改
    def put(self):
        # 获取请求的json数据，返回字典
        req_dict = request.get_json()

        tree_id = req_dict.get("tree_id")  # 项目id
        group_id = req_dict.get("group_id")  # 组id
        func_id = req_dict.get("func_id")   # 功能权限id

        try:
            func_id = str(func_id)
            u_list = db.session.query(db_mysql.GroupFunc).filter(db_mysql.GroupFunc.tree_id == tree_id,
                                                                 db_mysql.GroupFunc.group_id == group_id).update(
                {
                    "func_id": func_id
                })
            db.session.commit()
        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="修改失败")
        db.session.close()
        return jsonify(statusCode=RET.OK, msg="修改成功")

    # 删除
    def delete(self):
        # 获取请求的json数据，返回字典
        req_dict = request.get_json()
        tree_id = req_dict.get("tree_id")  # 项目id
        group_id = req_dict.get("group_id")  # 组id

        # 删除某个项目下的某个组
        try:
            delete = db.session.query(db_mysql.GroupFunc).filter(db_mysql.GroupFunc.group_id == group_id,
                                                                 db_mysql.GroupFunc.tree_id == tree_id).delete()
            db.session.commit()
        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="删除失败")
        db.session.close()

        return jsonify(statusCode=RET.OK, msg="删除成功")


class AuthTreeGroup(Resource):  # 项目添加组时，组的查询
    # 项目添加分组，查询未在项目下的组，并返给前端
    def get(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        tree_id = req_dict.get("tree_id")  # 项目id

        check_list = []

        try:
            # 从GroupFunc表中取出请求tree_id的数据
            gf_list = db.session.query(db_mysql.GroupFunc).filter(db_mysql.GroupFunc.tree_id == tree_id)
            # 从Group表中取出所有数据
            group_list = db.session.query(db_mysql.Group)

            db.session.commit()
        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")
        db.session.close()

        a_list = []
        b_list = []
        for x in gf_list:
            a_list.append(x.group_id)

        for y in group_list:
            b_list.append(y.id)

        # 把a_list和b_list里的数据删除重复的
        i = 0
        count = 0
        c_list = a_list+b_list
        while i < len(c_list):
            value = c_list[i]
            count = c_list[0:len(c_list)].count(value)
            if 1 < count:
                j = 0
                while j < count:
                    del c_list[c_list.index(value)]
                    j += 1
                i = i
            else:
                i += 1

        # 将去重后的c_list里的group_id，从Group表里取对应的name
        for z in c_list:
            z_list = db.session.query(db_mysql.Group).filter(db_mysql.Group.id == z)
            print(z_list)
            for raw in z_list:
                check_dic = {}
                check_dic["id"] = raw.id
                check_dic["group_name"] = raw.group_name

                check_list.append(check_dic)

        return jsonify(data=check_list, statusCode=RET.OK, msg="查询成功")


class AuthUserFunc(Resource):   # 项目对人权限的增删改查
    # 添加用户对项目的权限
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        uid = req_dict.get("uid")  # 员工id
        tree_id = req_dict.get("tree_id")  # 项目id
        func_id = req_dict.get("func_id")   # 权限id

        # # 判断组添加的用户是否已存在
        # g_list = db.session.query(db_mysql.GroupUser).filter(db_mysql.GroupUser.tree_id == tree_id)
        # db.session.commit()
        # for i in g_list:
        #     if i.group_id == group_id:
        #         return jsonify(statusCode=RET.PARAMERR, msg="用户已存在")

        # 判断项目id是否传值和为空
        if tree_id is None:
            return jsonify(statusCode=RET.PARAMERR, msg="tree_id为None")
        elif tree_id == "":
            return jsonify(statusCode=RET.PARAMERR, msg="tree_id为空")

        # 判断组id是否传值和为空
        if uid is None:
            return jsonify(statusCode=RET.PARAMERR, msg="uid为None")
        elif uid == "":
            return jsonify(statusCode=RET.PARAMERR, msg="uid为空")

        try:
            func_id = str(func_id)
            db.session.add(
                db_mysql.UserFunc(uid=uid, tree_id=tree_id, func_id=func_id))
            db.session.commit()

        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="数据创建失败")
        db.session.close()
        return jsonify(statusCode=RET.OK, msg="创建成功")

    # 修改用户对项目的权限
    def put(self):
        # 获取请求的json数据，返回字典
        req_dict = request.get_json()

        tree_id = req_dict.get("tree_id")  # 项目id
        uid = req_dict.get("uid")  # 组id
        func_id = req_dict.get("func_id")   # 功能权限id

        try:
            func_id = str(func_id)
            u_list = db.session.query(db_mysql.UserFunc).filter(db_mysql.UserFunc.tree_id == tree_id,
                                                                db_mysql.UserFunc.uid == uid).update(
                {
                    "func_id": func_id
                })
            db.session.commit()
        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="修改失败")
        db.session.close()
        return jsonify(statusCode=RET.OK, msg="修改成功")

    # 查询用户权限
    def get(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        tree_id = req_dict.get("tree_id")  # 项目id

        check_list = []

        try:
            u_list = db.session.query(db_mysql.UserFunc).filter(db_mysql.UserFunc.tree_id == tree_id)
            db.session.commit()
        except IntegrityError as e:

            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")
        db.session.close()

        for raw in u_list:
            check_dic = {}
            check_dic["uid"] = raw.uid
            check_dic["func_id"] = raw.func_id
            # 拿到uid
            uid = raw.uid
            # 去组表里查对应的组名称
            u_list = db.session.query(db_mysql.User).filter(db_mysql.User.id == uid)
            for i in u_list:
                name = i.name
                username = i.username
                check_dic["name"] = name
                check_dic["username"] = username
            check_list.append(check_dic)

        return jsonify(data=check_list, statusCode=RET.OK, msg="查询成功")

    # 删除
    def delete(self):
        # 获取请求的json数据，返回字典
        req_dict = request.get_json()
        tree_id = req_dict.get("tree_id")  # 项目id
        uid = req_dict.get("uid")  # uid

        # 删除某个项目下的某个组
        try:
            delete = db.session.query(db_mysql.UserFunc).filter(db_mysql.UserFunc.uid == uid,
                                                                db_mysql.UserFunc.tree_id == tree_id).delete()
            db.session.commit()
        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="删除失败")
        db.session.close()

        return jsonify(statusCode=RET.OK, msg="删除成功")


# 组的增删改查接口
api.add_resource(AuthGroup, '/group')
# ip的增删改查接口
api.add_resource(AuthEnvIp, '/envip')
# 查询所有ip类型和ip名字
api.add_resource(AuthEnvIpInfo, '/envipinfo')
# 功能权限的增删改查接口
api.add_resource(AuthFunction, '/func')
# 用户的增改查接口
api.add_resource(AuthUser, '/user')
# 用户对组的增删查接口
api.add_resource(AuthUserGroup, '/usergroup')
# 组对用户的增删查接口
api.add_resource(AuthGroupUser, '/groupuser')
# 组/项目，添加用户时，判断用户是否存在接口
api.add_resource(AuthCheckGroupUser, '/checkgroupuser')
# 组权限的增删改查接口
api.add_resource(AuthGroupFunc, '/groupfunc')
# 用户信息的增删改查接口
api.add_resource(AuthUserInfo, '/userinfo')
# 组添加用户时，查询用户接口
api.add_resource(AuthGroupUserAdd, '/groupuseradd')
# 员工加入组时，查询组接口
api.add_resource(AuthUserGroupAdd, '/usergroupadd')
# 项目加入组时，查询组接口
api.add_resource(AuthTreeGroup, '/treegroup')
# 人的项目权限增删改查接口
api.add_resource(AuthUserFunc, '/userfunc')
# 项目工程的增查接口
api.add_resource(AuthProject, '/project')