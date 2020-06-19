from flask import (jsonify, Blueprint, request, current_app)
from flask_restful import Resource, Api
from first_app.exts import db
from first_app import db_mysql
from first_app.api_status.response_code import RET
from sqlalchemy.exc import IntegrityError
# from app.__init__ import create_app
#
# app = create_app()

user_permissions = Blueprint('user_permissions', __name__, url_prefix='/UserPerm')
api = Api(user_permissions)


class PermUserTree(Resource):
    # def __init__(self, new_uid):
    #     self.uid = new_uid
    #
    # def user_tree(self):
    #     try:
    #         # 根据uid查询所在项目
    #         UF_list = db.session.query(db_mysql.UserFunc).filter(db_mysql.UserFunc.uid == self.uid)
    #         # 根据uid查询所在的组
    #         UG_list = db.session.query(db_mysql.GroupUser).filter(db_mysql.GroupUser.uid == self.uid)
    #
    #         db.session.commit()
    #
    #     except IntegrityError as e:
    #
    #         # 数据库操作错误后的回滚
    #         db.session.rollback()
    #         current_app.logger.error(e)
    #         return "数据库失败"
    #     db.session.close()
    #
    #     Pro_Tree = []
    #     for i in UG_list:
    #         if i.group_id == 1:
    #             return "admin"
    #         else:
    #             # 从group表取出用户所在的组
    #             p_list = db.session.query(db_mysql.Group).filter(db_mysql.Group.id == i.group_id)
    #
    #             # 取出组所对应的project_id
    #             prolist = []
    #             for a in p_list:
    #                 GP = a.project_id
    #                 pro = list(GP.split(","))
    #                 for b in pro:
    #                     b = int(b)
    #                     prolist.append(b)
    #             pro_list = list(set(prolist))
    #             # print(pro_list)
    #
    #             # 取出userfunc表中的用户对于的tree_id，存入uf_list
    #             ut_list = []
    #             for ut in UF_list:
    #                 ut_list.append(ut.tree_id)
    #
    #             # 取出groupfunc表中用户所在组的tree_id，存入gf_list
    #             gt_list = []
    #             for gi in UG_list:
    #                 t_list = db.session.query(db_mysql.GroupFunc).filter(db_mysql.GroupFunc.group_id == gi.group_id)
    #                 for gt in t_list:
    #                     gt_list.append(gt.tree_id)
    #
    #             # 用户所有tree_id = ut_list + gt_list
    #             ugt_list = list(set(ut_list + gt_list))
    #             # print(ugt_list)
    #
    #             pro_tree = {}
    #             pro_tree[pro_list[0]] = ugt_list
    #             Pro_Tree.append(pro_tree)
    #             return Pro_Tree

    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        uid = req_dict.get("uid")  # 用户id
        try:
            # 根据uid查询所在项目
            UF_list = db.session.query(db_mysql.UserFunc).filter(db_mysql.UserFunc.uid == uid)
            # 根据uid查询所在的组
            UG_list = db.session.query(db_mysql.GroupUser).filter(db_mysql.GroupUser.uid == uid)

            db.session.commit()

        except IntegrityError as e:

            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return "数据库失败"
        db.session.close()

        Pro_Tree = []
        for i in UG_list:
            if i.group_id == 1:
                return "admin"
            else:
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

                # 取出userfunc表中的用户对于的tree_id，存入uf_list
                ut_list = []
                for ut in UF_list:
                    ut_list.append(ut.tree_id)

                # 取出groupfunc表中用户所在组的tree_id，存入gf_list
                gt_list = []
                for gi in UG_list:
                    t_list = db.session.query(db_mysql.GroupFunc).filter(db_mysql.GroupFunc.group_id == gi.group_id)
                    for gt in t_list:
                        gt_list.append(gt.tree_id)

                # 用户所有tree_id = ut_list + gt_list
                ugt_list = list(set(ut_list + gt_list))
                # print(ugt_list)

                Tree_Func = []
                tree_func = {}

                for treeid in ugt_list:
                    user_tree = db.session.query(db_mysql.UserFunc).filter(db_mysql.UserFunc.uid == uid,
                                                                           db_mysql.UserFunc.tree_id == treeid)
                    func_list = []
                    for userfunc in user_tree:
                        user_func = userfunc.func_id
                        func_list.append(user_func)

                    for groupid in UG_list:
                        group_tree = db.session.query(db_mysql.GroupFunc).filter(db_mysql.GroupFunc.group_id == groupid.group_id,
                                                                                 db_mysql.GroupFunc.tree_id == treeid)

                        for groupfunc in group_tree:
                            group_func = groupfunc.func_id
                            func_list.append(group_func)
                    print(func_list)
                    treefunc = []
                    for val in func_list:
                        val_list = list(val.split(','))
                        for va in val_list:
                            va = int(va)
                            treefunc.append(va)
                    treefunc = list(set(treefunc))
                    # print(treefunc)
                    tree_func[treeid] = treefunc   # 把tree对应的func存入字典
                Tree_Func.append(tree_func)   # tree和func对应关系存入列表
                # print(Tree_Func)
                pro_tree = {}
                # 判断project_id为几，返回对应的不同内容
                for proid in pro_list:
                    if proid == 2:
                        pro_tree[proid] = Tree_Func
                        Pro_Tree.append(pro_tree)
                        # return Pro_Tree
                    elif proid == 3:
                        # Pro_Tree.append("用例管理")
                        pass
                    elif proid == 4:
                        # Pro_Tree.append("日志管理")
                        pass
                    return Pro_Tree


class PermUserFunc(Resource):
    # def __init__(self, new_type, new_tree_id, new_uid):
    #     self.type = new_type
    #     self.tree_id = new_tree_id
    #     self.uid = new_uid
    #
    # def user_func(self):
    #     if self.type == 2:
    #         try:
    #             # 根据uid查询所在项目的功能权限
    #             UF_list = db.session.query(db_mysql.UserFunc).filter(db_mysql.UserFunc.uid == self.uid,
    #                                                                  db_mysql.UserFunc.tree_id == self.tree_id)
    #             # 根据uid查询所在的组
    #             UG_list = db.session.query(db_mysql.GroupUser).filter(db_mysql.GroupUser.uid == self.uid)
    #
    #             db.session.commit()
    #
    #         except IntegrityError as e:
    #
    #             # 数据库操作错误后的回滚
    #             db.session.rollback()
    #             current_app.logger.error(e)
    #             return "数据库失败"
    #         db.session.close()
    #
    #         port_req = []
    #         for raw in UG_list:
    #             if raw.group_id == 1:
    #                 return "admin"
    #             else:
    #                 # 通过用户所在组的id，取出组对应的func_id
    #                 gf_list = []
    #                 for gi in UG_list:
    #                     g_list = db.session.query(db_mysql.GroupFunc).filter(db_mysql.GroupFunc.group_id == gi.group_id,
    #                                                                          db_mysql.GroupFunc.tree_id == self.tree_id)
    #                     for gf in g_list:
    #                         gf_list.append(gf.func_id)
    #
    #                 uf_list = []
    #                 for uf in UF_list:
    #                     uf_list.append(uf.func_id)
    #
    #                 ugf_list = uf_list + gf_list
    #                 a_list = []
    #                 for i in ugf_list:
    #                     i = list(i.split(","))
    #                     a_list.append(i)
    #
    #                 b_list = []
    #                 for i in a_list:
    #                     for x in i:
    #                         x = int(x)
    #                         b_list.append(x)
    #                 c_list = list(set(b_list))
    #
    #                 for i in c_list:
    #                     p_list = db.session.query(db_mysql.Function).filter(db_mysql.Function.id == i)
    #                     for val in p_list:
    #                         port_dic = {}
    #                         port_dic[val.port_name] = val.request_type
    #                         port_req.append(port_dic)
    #                 return port_req
    #
    #     elif self.type == 3:
    #         pass
    #     elif self.type == 4:
    #         pass

    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        uid = req_dict.get("uid")  # 用户id
        type = req_dict.get("type")  # 项目工程类型 2：压测中心，3：用例管理，4：日志管理
        tree_id = req_dict.get("tree_id")   # 项目id

        if type == 2:
            try:
                # 根据uid查询所在项目的功能权限
                UF_list = db.session.query(db_mysql.UserFunc).filter(db_mysql.UserFunc.uid == uid,
                                                                     db_mysql.UserFunc.tree_id == tree_id)
                # 根据uid查询所在的组
                UG_list = db.session.query(db_mysql.GroupUser).filter(db_mysql.GroupUser.uid == uid)

                db.session.commit()

            except IntegrityError as e:

                # 数据库操作错误后的回滚
                db.session.rollback()
                current_app.logger.error(e)
                return "数据库失败"
            db.session.close()

            port_req = []
            for raw in UG_list:
                if raw.group_id == 1:
                    return "admin"
                else:
                    # 通过用户所在组的id，取出组对应的func_id
                    gf_list = []
                    for gi in UG_list:
                        g_list = db.session.query(db_mysql.GroupFunc).filter(db_mysql.GroupFunc.group_id == gi.group_id,
                                                                             db_mysql.GroupFunc.tree_id == tree_id)
                        for gf in g_list:
                            gf_list.append(gf.func_id)

                    uf_list = []
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
                            x = int(x)
                            b_list.append(x)
                    c_list = list(set(b_list))

                    for i in c_list:
                        p_list = db.session.query(db_mysql.Function).filter(db_mysql.Function.id == i)
                        for val in p_list:
                            port_dic = {}
                            port_dic[val.port_name] = val.request_type
                            port_req.append(port_dic)
                    return port_req

        elif self.type == 3:
            pass
        elif self.type == 4:
            pass


# 登录页面初始化请求用户权限接口
api.add_resource(PermUserTree, '/usertree')
# 判断请求用户接口权限验证接口
api.add_resource(PermUserFunc, '/userfunc')


# b = UserTree(2)
# print(b.user_tree())
#
# a = UserFunc(2, 2, 3)
# print(a.user_func())
