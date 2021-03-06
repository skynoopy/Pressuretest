from flask import (Blueprint, request, jsonify, current_app)
from flask_restful import Resource, Api
from app.exts import db
from app import db_mysql
from app.api_status.response_code import RET
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from .Httpauth import authtoken, Interface_authority


AuthorityApi = Blueprint('AuthorityApi', __name__, url_prefix='/AuthorityApi')
api = Api(AuthorityApi)


class AuthProject(Resource):    # 项目工程的增查
    decorators = [authtoken.login_required]

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
    decorators = [authtoken.login_required]

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
    decorators = [authtoken.login_required]

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
        # 获取url请求的参数
        ip_type = request.args.get("ip_type")  # ip类型

        check_list = []

        try:
            ip_list = db.session.query(db_mysql.Envip).filter(db_mysql.Envip.ip_type == ip_type)
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
    decorators = [authtoken.login_required]

    # 查询
    # def get(self):
    #
    #     type_dic = {}
    #     iptype_list = [0, 1, 2]
    #
    #     for iptype in iptype_list:
    #         try:
    #             ip_list = db.session.query(db_mysql.Envip).filter(db_mysql.Envip.ip_type == iptype)
    #             db.session.commit()
    #         except IntegrityError as e:
    #
    #             # 数据库操作错误后的回滚
    #             db.session.rollback()
    #             current_app.logger.error(e)
    #             return jsonify(statusCode=RET.DATAERR, msg="查询失败")
    #         db.session.close()
    #
    #         type_list = []
    #         for raw in ip_list:
    #             check_dic = {}
    #             check_dic["id"] = raw.id
    #             check_dic["ip_name"] = raw.ip_name
    #
    #             type_list.append(check_dic)
    #             type_dic[iptype] = type_list
    #
    #     return jsonify(data=type_dic, statusCode=RET.OK, msg="查询成功")

    # 查询
    def post(self):
            # 获取请求的json数据, 返回字典
            req_dict = request.get_json()
            ip_type = req_dict.get("ip_type")  # ip类型

            val_dic = {}

            try:
                ip_val = db.session.query(db_mysql.Envip).filter(db_mysql.Envip.ip_type == ip_type)
                pers_val = db.session.query(db_mysql.UserEnv).filter(db_mysql.UserEnv.ip_type == ip_type)
                db.session.commit()
            except IntegrityError as e:

                # 数据库操作错误后的回滚
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(statusCode=RET.DATAERR, msg="查询失败")
            db.session.close()

            ip_list = []
            for raw in ip_val:
                check_dic = {}
                check_dic["id"] = raw.id
                check_dic["ip_name"] = raw.ip_name

                ip_list.append(check_dic)

            pers_list = []
            for val in pers_val:
                pers_dic = {}
                pers_dic["id"] = val.id
                pers_dic["uid"] = val.uid
                user_val = db.session.query(db_mysql.User).filter(db_mysql.User.id == val.uid)
                for i in user_val:
                    pers_dic["name"] = i.name
                    pers_dic["username"] = i.username

                pers_list.append(pers_dic)

            val_dic["ip_list"] = ip_list
            val_dic["pers_list"] = pers_list

            return jsonify(data=val_dic, statusCode=RET.OK, msg="查询成功")


class AuthFunction(Resource):  # 权限的增删改查
    decorators = [authtoken.login_required]

    # 新增
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        f_name = req_dict.get("func_name")  # 权限名称
        port_name = req_dict.get("port_name")   # 接口名称
        request_type = req_dict.get("request_type")   # 请求方式
        project_id = req_dict.get("project_id")    # 项目工程id

        # 判断权限名不能重复、是否传值和为空
        func_list = db.session.query(db_mysql.Function).filter(db_mysql.Function.project_id == project_id)
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
                db_mysql.Function(func_name=f_name, port_name=port_name,
                                  request_type=request_type, project_id=project_id))
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


class AuthQueryFunction(Resource):
    decorators = [authtoken.login_required]

    # 查询
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        project_id = req_dict.get("project_id")  # 项目工程id

        check_list = []

        try:
            func_list = db.session.query(db_mysql.Function).filter(db_mysql.Function.project_id == project_id)
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


class AuthUser(Resource):   # 用户的增删改查
    decorators = [authtoken.login_required]

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
            check_dic["role"] = raw.role

            check_list.append(check_dic)

        return jsonify(data=check_list, statusCode=RET.OK, msg="查询成功")

    # 新增
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        username = req_dict.get("username")  # 账号
        name = req_dict.get("name")    # 用户姓名
        role = req_dict.get("role")    # 用户角色 0为开发，1为测试，2为产品
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

        # 判断角色是否传值和为空
        if role is None:
            return jsonify(statusCode=RET.PARAMERR, msg="角色为必填项")
        elif role == "":
            return jsonify(statusCode=RET.PARAMERR, msg="角色不能为空")

        try:
            db.session.add(
                db_mysql.User(username=username, password=generate_password_hash(password),
                              name=name, role=role))
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
        role = req_dict.get("role")   # 角色
        oldpwd = req_dict.get("oldpwd")  # 旧密码
        newpwd = req_dict.get("newpwd")  # 新密码
        type = req_dict.get("type")   # 1为修改名字，2为修改密码
        oldpwd = str(oldpwd)
        newpwd = str(newpwd)
        if type == 1:
            try:
                u_list = db.session.query(db_mysql.User).filter(db_mysql.User.id == uid).update(
                    {
                        "name": name,
                        "role": role
                    })
                db.session.commit()
            except IntegrityError as e:
                # 数据库操作错误后的回滚
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(statusCode=RET.DATAERR, msg="修改失败")
            db.session.close()
            return jsonify(statusCode=RET.OK, msg="修改成功")

        elif type == 2:
            try:
                pwd_list = db.session.query(db_mysql.User).filter(db_mysql.User.id == uid)
                db.session.commit()
            except IntegrityError as e:
                # 数据库操作错误后的回滚
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(statusCode=RET.DATAERR, msg="修改失败")
            db.session.close()

            for val in pwd_list:
                if not check_password_hash(val.password, oldpwd):
                    return jsonify(statusCode=RET.PARAMERR, msg="原密码输入错误")
                else:
                    try:
                        u_list = db.session.query(db_mysql.User).filter(db_mysql.User.id == uid).update(
                            {
                                "password": generate_password_hash(newpwd)
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


class AuthUserEnv(Resource):
    decorators = [authtoken.login_required]

    # 新增用户授权环境类型
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        uid = req_dict.get("uid")  # 用户id
        ip_type = req_dict.get("ip_type")    # 授权环境类型

        # 判断uid是否传值和为空
        if uid is None:
            return jsonify(statusCode=RET.PARAMERR, msg="uid为必填项")
        elif uid == "":
            return jsonify(statusCode=RET.PARAMERR, msg="uid不能为空")

        # 判断授权环境是否传值和为空
        if ip_type is None:
            return jsonify(statusCode=RET.PARAMERR, msg="角色为必填项")
        elif ip_type == "":
            return jsonify(statusCode=RET.PARAMERR, msg="角色不能为空")

        try:
            val_list = db.session.query(db_mysql.UserEnv).filter(db_mysql.UserEnv.uid == uid)
            db.session.commit()
        except IntegrityError as e:

            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")
        db.session.close()

        ip_list = []
        for i in val_list:
            ip_list.append(i.ip_type)

        if ip_type in ip_list:
            return jsonify(statusCode=RET.PARAMERR, msg="该环境已添加")
        else:
            try:
                db.session.add(
                    db_mysql.UserEnv(uid=uid, ip_type=ip_type))
                db.session.commit()

            except IntegrityError as e:
                # 数据库操作错误后的回滚
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(statusCode=RET.DATAERR, msg="数据创建失败")
            db.session.close()
            return jsonify(statusCode=RET.OK, msg="创建成功")

    # 删除
    def delete(self):
        # 获取请求的json数据，返回字典
        req_dict = request.get_json()
        uid = req_dict.get("uid")  # 用户id
        ip_type = req_dict.get("ip_type")

        try:
            # 删除user_env表
            delete = db.session.query(db_mysql.UserEnv).filter(db_mysql.UserEnv.uid == uid,
                                                               db_mysql.UserEnv.ip_type == ip_type).delete()
            db.session.commit()
        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="删除失败")
        db.session.close()

        return jsonify(statusCode=RET.OK, msg="删除成功")


class AuthUserInfo(Resource):
    decorators = [authtoken.login_required]

    # 查询uid、uname、ip_type
    def get(self):
        # 获取url请求的数据
        uid = request.args.get("uid")  # 用户id

        check_list = []

        try:
            u_list = db.session.query(db_mysql.User).filter(db_mysql.User.id == uid)
            ip_list = db.session.query(db_mysql.UserEnv).filter(db_mysql.UserEnv.uid == uid)
            db.session.commit()
        except IntegrityError as e:

            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")
        db.session.close()

        ip_value = []
        for i in ip_list:
            ip_value.append(i.ip_type)

        for raw in u_list:
            check_dic = {}
            check_dic["id"] = raw.id
            check_dic["name"] = raw.name
            check_dic["username"] = raw.username
            check_dic["role"] = raw.role
            check_dic["ip_type"] = ip_value

            check_list.append(check_dic)

        return jsonify(data=check_list, statusCode=RET.OK, msg="查询成功")

    # 修改授权环境
    # def put(self):
    #     # 获取请求的json数据，返回字典
    #     req_dict = request.get_json()
    #
    #     uid = req_dict.get("uid")  # 用户id
    #     ip_type = req_dict.get("ip_type")  # 授权环境
    #
    #     try:
    #         u_list = db.session.query(db_mysql.User).filter(db_mysql.User.id == uid).update(
    #             {
    #                 "ip_type": ip_type
    #             })
    #         db.session.commit()
    #     except IntegrityError as e:
    #         # 数据库操作错误后的回滚
    #         db.session.rollback()
    #         current_app.logger.error(e)
    #         return jsonify(statusCode=RET.DATAERR, msg="修改失败")
    #     db.session.close()
    #     return jsonify(statusCode=RET.OK, msg="修改成功")


class CheckUserEnv(Resource):
    decorators = [authtoken.login_required]

    # 员工详情页，添加授权环境，授权环境的查询接口，显示未加入的环境
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        uid = req_dict.get("uid")  # 用户id

        check_list = []
        env_list = [0, 1, 2, 3]

        try:
            # 从GroupUser表中取出请求uid的数据
            user_list = db.session.query(db_mysql.UserEnv).filter(db_mysql.UserEnv.uid == uid)
            db.session.commit()
        except IntegrityError as e:

            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")
        db.session.close()

        a_list = []
        for x in user_list:
            a_list.append(x.ip_type)

        # 把a_list和env_list里的数据删除重复的
        i = 0
        count = 0
        c_list = a_list + env_list
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

        check_dic = {}
        check_dic["ip_type"] = c_list

        check_list.append(check_dic)

        return jsonify(data=check_list, statusCode=RET.OK, msg="查询成功")


class AuthUserGroupAdd(Resource):
    decorators = [authtoken.login_required]

    # 员工详情页，添加组时，组的查询接口，显示未加入的组
    def post(self):
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
    decorators = [authtoken.login_required]

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
        # 获取url请求的数据
        uid = request.args.get("uid")  # 用户id

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
    decorators = [authtoken.login_required]

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
        # 获取url请求的数据
        group_id = request.args.get("group_id")  # 用户id

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
    decorators = [authtoken.login_required]

    # 校验用户是否已存在
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        uid = req_dict.get("uid")  # 用户id
        group_id = req_dict.get("group_id")  # 组的id
        tree_id = req_dict.get("tree_id")   # 项目id
        type = req_dict.get("type")  # 1为组，2为项目
        if type == 1:
            # 判断组添加的用户是否已存在
            g_list = db.session.query(db_mysql.GroupUser).filter(db_mysql.GroupUser.group_id == group_id)
            db.session.commit()
            uid_list = []
            for i in g_list:
                uid_list.append(i.uid)
            if uid in uid_list:
                return jsonify(statusCode=RET.PARAMERR, msg="用户已存在")
            else:
                return jsonify(statusCode=RET.OK, msg="验证通过")

        elif type == 2:
            # 判断项目添加的用户是否已存在
            val_list = db.session.query(db_mysql.UserFunc)
            tree_list = []
            for i in val_list:
                tree_list.append(i.tree_id)

            if tree_id in tree_list:
                t_list = db.session.query(db_mysql.UserFunc).filter(db_mysql.UserFunc.tree_id == tree_id)
                db.session.commit()

                for i in t_list:
                    if i.uid == uid:
                        return jsonify(statusCode=RET.PARAMERR, msg="用户已存在")
                    else:
                        return jsonify(statusCode=RET.OK, msg="验证通过")
            else:
                return jsonify(statusCode=RET.OK, msg="验证通过")


class AuthGroupUserAdd(Resource):
    decorators = [authtoken.login_required]

    # 组添加员工时，搜索已有员工
    def post(self):
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
    decorators = [authtoken.login_required]
    method_decorators = [Interface_authority]

    # 项目下添加某个组
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        group_id = req_dict.get("group_id")  # 组的id
        tree_id = req_dict.get("tree_id")  # 项目id
        func_id = req_dict.get("func_id")   # 功能权限id
        project_id = req_dict.get("project_id")   # 项目工程id

        # 判断组是否已存在
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

        # 判断项目工程id是否传值和为空
        if project_id is None:
            return jsonify(statusCode=RET.PARAMERR, msg="project_id为空")
        elif project_id == "":
            return jsonify(statusCode=RET.PARAMERR, msg="project_id为空")

        try:
            func_id = str(func_id)
            db.session.add(
                db_mysql.GroupFunc(group_id=group_id, tree_id=tree_id, func_id=func_id, project_id=project_id))
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

        tree_id = req_dict.get("tree_id")  # 项目id
        group_id = req_dict.get("group_id")  # 组id
        func_id = req_dict.get("func_id")   # 功能权限id
        project_id = req_dict.get("project_id")   # 项目工程id

        try:
            func_id = str(func_id)
            u_list = db.session.query(db_mysql.GroupFunc).filter(db_mysql.GroupFunc.tree_id == tree_id,
                                                                 db_mysql.GroupFunc.group_id == group_id,
                                                                 db_mysql.GroupFunc.project_id == project_id).update(
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
        project_id = req_dict.get("project_id")  # 项目工程id

        # 删除某个项目下的某个组
        try:
            delete = db.session.query(db_mysql.GroupFunc).filter(db_mysql.GroupFunc.group_id == group_id,
                                                                 db_mysql.GroupFunc.tree_id == tree_id,
                                                                 db_mysql.GroupFunc.project_id == project_id).delete()
            db.session.commit()
        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="删除失败")
        db.session.close()

        return jsonify(statusCode=RET.OK, msg="删除成功")


class AuthQueryGroupFunc(Resource):
    decorators = [authtoken.login_required]
    method_decorators = [Interface_authority]

    # 查询tree下所有组列表
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        tree_id = req_dict.get("tree_id")  # 项目id
        project_id = req_dict.get("project_id")  # 功能权限id

        check_list = []

        try:
            g_list = db.session.query(db_mysql.GroupFunc).filter(db_mysql.GroupFunc.tree_id == tree_id,
                                                                 db_mysql.GroupFunc.project_id == project_id)
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


class AuthTreeGroup(Resource):  # 项目添加组时，组的查询
    decorators = [authtoken.login_required]

    # 项目添加分组，查询未在项目下的组，并返给前端
    def post(self):
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
    decorators = [authtoken.login_required]
    method_decorators = [Interface_authority]

    # 添加用户对项目的权限
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        uid = req_dict.get("uid")  # 员工id
        tree_id = req_dict.get("tree_id")  # 项目id
        func_id = req_dict.get("func_id")   # 权限id
        project_id = req_dict.get("project_id")   # 项目工程id

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

        # 判断用户id是否传值和为空
        if uid is None:
            return jsonify(statusCode=RET.PARAMERR, msg="uid为None")
        elif uid == "":
            return jsonify(statusCode=RET.PARAMERR, msg="uid为空")

        # 判断项目工程id是否传值和为空
        if project_id is None:
            return jsonify(statusCode=RET.PARAMERR, msg="project_id为None")
        elif project_id == "":
            return jsonify(statusCode=RET.PARAMERR, msg="project_id为空")

        try:
            func_id = str(func_id)
            db.session.add(
                db_mysql.UserFunc(uid=uid, tree_id=tree_id, func_id=func_id, project_id=project_id))
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
        project_id = req_dict.get("project_id")   # 项目工程id

        try:
            func_id = str(func_id)
            u_list = db.session.query(db_mysql.UserFunc).filter(db_mysql.UserFunc.tree_id == tree_id,
                                                                db_mysql.UserFunc.uid == uid,
                                                                db_mysql.UserFunc.project_id == project_id).update(
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
        uid = req_dict.get("uid")  # uid
        project_id = req_dict.get("project_id")   # 项目工程id

        # 删除某个项目下的某个组
        try:
            delete = db.session.query(db_mysql.UserFunc).filter(db_mysql.UserFunc.uid == uid,
                                                                db_mysql.UserFunc.tree_id == tree_id,
                                                                db_mysql.UserFunc.project_id == project_id).delete()
            db.session.commit()
        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="删除失败")
        db.session.close()

        return jsonify(statusCode=RET.OK, msg="删除成功")


class AuthQueryUserFunc(Resource):
    decorators = [authtoken.login_required]
    method_decorators = [Interface_authority]

    # 查询用户权限
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        tree_id = req_dict.get("tree_id")  # 项目id
        project_id = req_dict.get("project_id")  # 功能权限id

        check_list = []

        try:
            u_list = db.session.query(db_mysql.UserFunc).filter(db_mysql.UserFunc.tree_id == tree_id,
                                                                db_mysql.UserFunc.project_id == project_id)
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


# 组的增删改查接口
api.add_resource(AuthGroup, '/group')
# ip的增删改查接口
api.add_resource(AuthEnvIp, '/envip')
# 查询所有ip类型和ip名字
api.add_resource(AuthEnvIpInfo, '/envipinfo')
# 功能权限的增删改接口
api.add_resource(AuthFunction, '/func')
# 功能权限的查询接口
api.add_resource(AuthQueryFunction, '/queryfunc')
# 用户的增改查接口
api.add_resource(AuthUser, '/user')
# 用户对组的增删查接口
api.add_resource(AuthUserGroup, '/usergroup')
# 组对用户的增删查接口
api.add_resource(AuthGroupUser, '/groupuser')
# 组/项目，添加用户时，判断用户是否存在接口
api.add_resource(AuthCheckGroupUser, '/checkgroupuser')
# 组权限的增删改接口
api.add_resource(AuthGroupFunc, '/groupfunc')
# 组权限的查询接口
api.add_resource(AuthQueryGroupFunc, '/querygroupfunc')
# 用户信息的增删改查接口
api.add_resource(AuthUserInfo, '/userinfo')
# 组添加用户时，查询用户接口
api.add_resource(AuthGroupUserAdd, '/groupuseradd')
# 员工加入组时，查询组接口
api.add_resource(AuthUserGroupAdd, '/usergroupadd')
# 项目加入组时，查询组接口
api.add_resource(AuthTreeGroup, '/treegroup')
# 人的项目权限增删改接口
api.add_resource(AuthUserFunc, '/userfunc')
# 人的项目权限查询接口
api.add_resource(AuthQueryUserFunc, '/queryuserfunc')
# 项目工程的增查接口
api.add_resource(AuthProject, '/project')
# 用户授权环境的查删接口
api.add_resource(AuthUserEnv, '/userenv')
# 用户添加授权环境时，查询未授权的环境
api.add_resource(CheckUserEnv, '/checkuserenv')
