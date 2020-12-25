from flask import (Blueprint, request, current_app, jsonify)
from flask_restful import Resource, Api
from app.exts import db
from app import db_mysql
from sqlalchemy.exc import IntegrityError
from .Httpauth import authtoken
from app.api_status.response_code import RET


user_permissions = Blueprint('user_permissions', __name__, url_prefix='/UserPerm')
api = Api(user_permissions)


class PermUserTree(Resource):

    # 初始化用户对应的project_id和tree_id的权限
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        uid = req_dict.get("uid")  # 用户id

        try:
            # 从GroupUser表里取出所有uid，判断请求的uid是否在列表里
            uid_list = db.session.query(db_mysql.GroupUser)
            db.session.commit()
            UidList = []
            for val in uid_list:
                UidList.append(val.uid)
            if uid in UidList:
                # 根据uid查询所在的组
                UG_list = db.session.query(db_mysql.GroupUser).filter(db_mysql.GroupUser.uid == uid)
                db.session.commit()
                id_val = []
                for gid in UG_list:
                    id_val.append(gid.group_id)
                if 1 in id_val:
                    # val_dic['status'] = 'admin'
                    return jsonify(data='admin', statusCode=RET.OK, msg="查询成功")
                else:
                    for i in UG_list:
                        # 从group表取出用户所在的组
                        p_list = db.session.query(db_mysql.Group).filter(db_mysql.Group.id == i.group_id)

                        # 取出组所对应的project_id
                        prolist = []
                        for a in p_list:
                            GP = a.project_id
                            pro = list(GP.split(","))
                            for b in pro:
                                b = int(b)
                                prolist.append(b)
                        pro_list = list(set(prolist))
                        # print(pro_list)

                        pro_tree = {}
                        # 判断project_id为几，返回对应的不同内容
                        for proid in pro_list:
                            # 取出userfunc表中的用户对于的tree_id，存入uf_list
                            ut_list = []
                            # 根据uid查询所在项目
                            UF_list = db.session.query(db_mysql.UserFunc).filter(db_mysql.UserFunc.uid == uid,
                                                                                 db_mysql.UserFunc.project_id == proid)
                            for ut in UF_list:
                                ut_list.append(ut.tree_id)

                            # 取出groupfunc表中用户所在组的tree_id，存入gf_list
                            gt_list = []
                            for gi in UG_list:
                                t_list = db.session.query(db_mysql.GroupFunc).filter(db_mysql.GroupFunc.group_id == gi.group_id,
                                                                                     db_mysql.GroupFunc.project_id == proid)
                                for gt in t_list:
                                    gt_list.append(gt.tree_id)
                                # print(gt_list)

                            # 用户所有tree_id = ut_list + gt_list
                            ugt_list = list(set(ut_list + gt_list))
                            print(ugt_list)

                            Tree_Func = []
                            tree_func = {}

                            for treeid in ugt_list:
                                user_tree = db.session.query(db_mysql.UserFunc).filter(db_mysql.UserFunc.uid == uid,
                                                                                       db_mysql.UserFunc.tree_id == treeid,
                                                                                       db_mysql.UserFunc.project_id == proid)
                                func_list = []
                                for userfunc in user_tree:
                                    user_func = userfunc.func_id
                                    func_list.append(user_func)

                                for groupid in UG_list:
                                    group_tree = db.session.query(db_mysql.GroupFunc).filter(db_mysql.GroupFunc.group_id == groupid.group_id,
                                                                                             db_mysql.GroupFunc.tree_id == treeid,
                                                                                             db_mysql.GroupFunc.project_id == proid)

                                    for groupfunc in group_tree:
                                        group_func = groupfunc.func_id
                                        func_list.append(group_func)
                                # print(func_list)
                                treefunc = []
                                for val in func_list:
                                    val_list = list(val.split(','))
                                    for va in val_list:
                                        va = int(va)
                                        treefunc.append(va)
                                treefunc = list(set(treefunc))
                                # print(treefunc)

                                # 把tree对应的func存入字典
                                tree_func[treeid] = treefunc

                            # tree和func对应关系存入列表
                            Tree_Func.append(tree_func)

                            # 将不同项目工程所对应的项目权限存入pro_tree
                            pro_tree[proid] = Tree_Func

                        # 将循环的project_id所对应的项目权限return
                        return jsonify(data=pro_tree, statusCode=RET.OK, msg="查询成功")
            else:
                # 从userfunc表里取出用户的project_id
                p_list = db.session.query(db_mysql.UserFunc).filter(db_mysql.UserFunc.uid == uid)

                # 取出组所对应的project_id
                prolist = []
                for a in p_list:
                    prolist.append(a.project_id)
                pro_list = list(set(prolist))
                # print(pro_list)

                pro_tree = {}
                # 判断project_id为几，返回对应的不同内容
                for proid in pro_list:
                    # 取出userfunc表中的用户对于的tree_id，存入uf_list
                    ut_list = []
                    # 根据uid查询所在项目
                    UF_list = db.session.query(db_mysql.UserFunc).filter(db_mysql.UserFunc.uid == uid,
                                                                         db_mysql.UserFunc.project_id == proid)
                    for ut in UF_list:
                        ut_list.append(ut.tree_id)

                    # 用户所有tree_id = ut_list + gt_list
                    ugt_list = list(set(ut_list))
                    print(ugt_list)

                    Tree_Func = []
                    tree_func = {}

                    for treeid in ugt_list:
                        user_tree = db.session.query(db_mysql.UserFunc).filter(db_mysql.UserFunc.uid == uid,
                                                                               db_mysql.UserFunc.tree_id == treeid,
                                                                               db_mysql.UserFunc.project_id == proid)
                        func_list = []
                        for userfunc in user_tree:
                            user_func = userfunc.func_id
                            func_list.append(user_func)

                        treefunc = []
                        for val in func_list:
                            val_list = list(val.split(','))
                            for va in val_list:
                                if va == "":
                                    treefunc.append(va)
                                else:
                                    va = int(va)
                                    treefunc.append(va)
                        treefunc = list(set(treefunc))
                        # print(treefunc)

                        # 把tree对应的func存入字典
                        tree_func[treeid] = treefunc

                    # tree和func对应关系存入列表
                    Tree_Func.append(tree_func)

                    # 将不同项目工程所对应的项目权限存入pro_tree
                    pro_tree[proid] = Tree_Func

                # 将循环的project_id所对应的项目权限return
                return jsonify(data=pro_tree, statusCode=RET.OK, msg="查询成功")

        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return "数据库失败"
        db.session.close()


class PermUserFunc(Resource):

    # 查询用户有哪些接口权限
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        uid = req_dict.get("uid")  # 用户id
        type = req_dict.get("type")  # 项目工程类型 2：压测中心，3：用例管理，4：日志管理
        tree_id = req_dict.get("tree_id")   # 项目id

        port_req = []

        try:
            # 从GroupUser表里取出所有uid，判断请求的uid是否在内
            u_list = db.session.query(db_mysql.GroupUser)
            db.session.commit()

            uid_list = []
            gf_list = []
            for i in u_list:
                uid_list.append(i.uid)
            if uid in uid_list:
                # 根据uid查询所在的组
                UG_list = db.session.query(db_mysql.GroupUser).filter(db_mysql.GroupUser.uid == uid)
                db.session.commit()

                for raw in UG_list:
                    if raw.group_id == 1:
                        return "admin"
                    else:
                        # 通过用户所在组的id，取出组对应的func_id

                        for gi in UG_list:
                            g_list = db.session.query(db_mysql.GroupFunc).filter(db_mysql.GroupFunc.group_id == gi.group_id,
                                                                                 db_mysql.GroupFunc.tree_id == tree_id)
                            db.session.commit()

                            for gf in g_list:
                                gf_list.append(gf.func_id)

            # 从UserFunc表中取出所有uid，判断请求的uid是否在内
            u_list = db.session.query(db_mysql.UserFunc)
            db.session.commit()

            UF_list = []
            uf_list = []
            for i in u_list:
                UF_list.append(i.uid)
            if uid in UF_list:
                # 根据uid查询所在项目的功能权限
                UF_list = db.session.query(db_mysql.UserFunc).filter(db_mysql.UserFunc.uid == uid,
                                                                     db_mysql.UserFunc.tree_id == tree_id)
                db.session.commit()

                for uf in UF_list:
                    uf_list.append(uf.func_id)

            ugf_list = uf_list + gf_list
            a_list = []
            for i in ugf_list:
                i = list(i.split(","))
                a_list.append(i)

            b_list = []
            for i in a_list:
                for x in i:
                    if x == "":
                        b_list.append(x)
                    else:
                        x = int(x)
                        b_list.append(x)
            c_list = list(set(b_list))

            for i in c_list:
                p_list = db.session.query(db_mysql.Function).filter(db_mysql.Function.id == i)
                db.session.commit()

                for val in p_list:
                    port_dic = {}
                    port_dic[val.port_name] = val.request_type
                    port_req.append(port_dic)
            return port_req

        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return "数据库失败"
        finally:
            db.session.close()


class GetPermissions(Resource):
    decorators = [authtoken.login_required]

    # 初始化给前端返回的一些用户信息
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        uid = req_dict.get("uid")  # 用户id
        projectid = req_dict.get("project_id")  # 项目id

        try:
            # 查询所有uid，判断uid是否存在
            u_list = db.session.query(db_mysql.User)
            db.session.commit()

            project_list = []

            user_list = []
            for i in u_list:
                user_list.append(i.id)
            if uid in user_list:
                # 判断uid是否在UserFunc表里
                uf = db.session.query(db_mysql.UserFunc)
                tree_func = {}
                uf_list = []
                treefunc = []
                user_f = []
                group_f = []
                user_proj = []
                for u_val in uf:
                    uf_list.append(u_val.uid)
                if uid in uf_list:
                    user_tree = db.session.query(db_mysql.UserFunc).filter(db_mysql.UserFunc.uid == uid,
                                                                           db_mysql.UserFunc.project_id == projectid)
                    func_list = []
                    for userfunc in user_tree:
                        user_func = userfunc.func_id
                        func_list.append(user_func)

                    for val in func_list:
                        val_list = list(val.split(','))
                        for va in val_list:
                            if va is "":
                                # user_f.append(va)
                                pass
                            else:
                                va = int(va)
                                user_f.append(va)

                    # 从UserFunc表中取出uid对应的project_id
                    user_p = db.session.query(db_mysql.UserFunc).filter(db_mysql.UserFunc.uid == uid)
                    for up in user_p:
                        user_proj.append(up.project_id)

                # 查询GroupUser表里的所有uid，判断uid是否存在
                uid_val = db.session.query(db_mysql.GroupUser)
                db.session.commit()

                uid_list = []
                for val in uid_val:
                    uid_list.append(val.uid)
                # 去重
                uid_list = list(set(uid_list))

                # 如果uid在列表里，从GroupUser取出对应的组id
                if uid in uid_list:
                    UG_list = db.session.query(db_mysql.GroupUser).filter(db_mysql.GroupUser.uid == uid)
                    for groupid in UG_list:
                        group_tree = db.session.query(db_mysql.GroupFunc).filter(db_mysql.GroupFunc.group_id == groupid.group_id,
                                                                                 db_mysql.GroupFunc.project_id == projectid)
                        gf_list = []
                        for groupfunc in group_tree:
                            gf_list.append(groupfunc.func_id)

                        for val in gf_list:
                            val_list = list(val.split(','))
                            for va in val_list:
                                if va is "":
                                    # group_f.append(va)
                                    pass
                                else:
                                    va = int(va)
                                    group_f.append(va)

                    treefunc = user_f + group_f
                    treefunc = list(set(treefunc))
                    # 把tree对应的func存入字典
                    tree_func["user_func"] = treefunc

                    group_proj = []
                    group_list = []
                    for gid in UG_list:
                        group_list.append(gid.group_id)

                    for i in UG_list:
                        group_p = db.session.query(db_mysql.GroupFunc).filter(db_mysql.GroupFunc.group_id == i.group_id)
                        for gp in group_p:
                            group_proj.append(gp.project_id)

                        project_list = list(set(user_proj + group_proj))

                        tree_func["project_id"] = project_list
                        if 1 in group_list:
                            tree_func["status"] = "admin"
                            return jsonify(data=tree_func, statusCode=RET.OK, msg="查询成功")
                        else:
                            tree_func["status"] = "common"
                            return jsonify(data=tree_func, statusCode=RET.OK, msg="查询成功")
                else:
                    tree_func["status"] = "common"
                    user_proj = list(set(user_proj))
                    tree_func["project_id"] = user_proj
                    tree_func["user_func"] = user_f
                    return jsonify(data=tree_func, statusCode=RET.OK, msg="查询成功")
            else:
                return jsonify(statusCode=RET.DATAERR, msg="该用户不存在")

        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")
        db.session.close()


class BatchPressure(Resource):
    decorators = [authtoken.login_required]

    # 查询批量压测用户有哪些tree有权限
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        uid = req_dict.get("uid")  # 用户id

        try:
            UF = db.session.query(db_mysql.UserFunc).filter(db_mysql.UserFunc.uid == uid)
            db.session.commit()

        except IntegrityError as e:

            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")
        db.session.close()

        tree_list = []
        for i in UF:
            func_list = []
            func = i.func_id
            user_func = func.split(",")
            for val in user_func:
                val = int(val)
                func_list.append(val)
            if 17 in func_list:
                tree_list.append(i.tree_id)
        return jsonify(data=tree_list, statusCode=RET.OK, msg="查询成功")


# 登录页面初始化请求用户权限接口
api.add_resource(PermUserTree, '/usertree')
# 判断请求用户接口权限验证接口
api.add_resource(PermUserFunc, '/userfunc')
# 判断用户身份接口
api.add_resource(GetPermissions, '/getpermissions')
# 用户批量压测权限对应的tree
api.add_resource(BatchPressure, '/batchpressure')

