# -*- coding: utf-8 -*-
from flask import (Blueprint, request, current_app, jsonify)
from flask_restful import Resource, Api
from app.exts import db
from app import db_mysql
from sqlalchemy.exc import IntegrityError
from .Httpauth import authtoken
from app.api_status.response_code import RET


MonitorResult = Blueprint('MonitorResult', __name__, url_prefix='/MonitorResult')
api = Api(MonitorResult)


class AddMonitor(Resource):

    # 新增监控报告
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        one_node = req_dict.get("one_node")  # 一级节点id
        two_node = req_dict.get("two_node")  # 二级节点id
        three_node = req_dict.get("three_node")  # 三级节点id
        four_node = req_dict.get("four_node")  # 四级节点id
        service_name = req_dict.get("service_name")   # 服务主机名
        service_ip = req_dict.get("service_ip")   # 服务ip
        result_details = req_dict.get("result_details")   # 运行结果详情
        run_result = req_dict.get("run_result")  # 运行结果：1为成功，2为失败
        is_new = req_dict.get("is_new")    # 是否为新的，1是，2否

        try:
            db.session.add(
                db_mysql.MonitorResult(one_node=one_node, two_node=two_node, three_node=three_node, four_node=four_node,
                                       service_name=service_name, service_ip=service_ip, result_details=result_details,
                                       run_result=run_result, is_new=is_new))
            db.session.commit()

        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="数据创建失败")
        db.session.close()
        return jsonify(statusCode=RET.OK, msg="添加成功")

    # 删除
    def delete(self):
            # 获取请求的json数据，返回字典
            req_dict = request.get_json()
            id = req_dict.get("id")  # 监控id
            # req_list = request.get_json()
            # for val in req_list.get("case_obj"):
            #     id = val.get("id")  # 用例内容id

            # 删除文件
            try:
                id_val = db.session.query(db_mysql.MonitorResult).filter(db_mysql.MonitorResult.id == id).delete()
                db.session.commit()
            except IntegrityError as e:
                # 数据库操作错误后的回滚
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(statusCode=RET.DATAERR, msg="删除失败")
            db.session.close()

            return jsonify(statusCode=RET.OK, msg="删除成功")

    # 修改
    def put(self):
        # 获取请求的json数据，返回字典
        req_dic = request.get_json()

        id = req_dic.get("id")  # 监控id
        is_new = req_dic.get("is_new")  # 是否为最新，1是，2否

        try:
            mon_list = db.session.query(db_mysql.MonitorResult).filter(db_mysql.MonitorResult.id == id).update(
                {
                    "is_new": is_new
                })
            db.session.commit()
        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="修改失败")
        db.session.close()
        return jsonify(statusCode=RET.OK, msg="修改成功")


class FilterMonitor(Resource):

    # 根据一级节点或（四级节点和结果）查询监控
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        one_node = req_dict.get("one_node")    # 一级节点id
        four_node = req_dict.get("four_node")  # 四级节点id
        run_result = req_dict.get("run_result")   # 运行结果 1为成功，2为失败
        page = req_dict.get("page")    # 分页
        limit = req_dict.get("limit")   # 每页条数

        if one_node is not None:

            obj_dic = {}
            check_list = []

            # 查询符合四级节点的所有监控数据，统计分页
            try:
                page_list = db.session.query(db_mysql.MonitorResult).filter(
                    db_mysql.MonitorResult.one_node == one_node). \
                    order_by(db_mysql.MonitorResult.create_time.desc()).paginate(int(page), int(limit), False)

                db.session.commit()

            except IntegrityError as e:
                # 数据库操作错误后的回滚
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(statusCode=RET.DATAERR, msg="查询失败")
            db.session.close()

            # 获取总页数
            page_num = page_list.pages
            # 当前页数
            page_present = page_list.page
            # 是否存在上一页
            page_prev = page_list.has_prev
            # 是否存在下一页
            page_next = page_list.has_next
            # 总条数
            total_size = page_list.total

            # 查询符合四级节点的所有检测数据，按时间倒序排列
            try:
                report_list = db.session.query(db_mysql.MonitorResult).filter(
                    db_mysql.MonitorResult.one_node == one_node). \
                    order_by(db_mysql.MonitorResult.create_time.desc()).limit(limit).offset((page - 1) * limit)

                db.session.commit()
            except IntegrityError as e:

                # 数据库操作错误后的回滚
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(statusCode=RET.DATAERR, msg="查询失败")
            db.session.close()

            for val in report_list:
                check_dic = {}
                check_dic["id"] = val.id
                one_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == val.one_node)
                for one in one_list:
                    check_dic["one_node"] = one.filename
                two_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == val.two_node)
                for two in two_list:
                    check_dic["two_node"] = two.filename
                three_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == val.three_node)
                for three in three_list:
                    check_dic["three_node"] = three.filename
                four_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == val.four_node)
                for four in four_list:
                    check_dic["four_node"] = four.filename
                check_dic["service_name"] = val.service_name
                check_dic["service_ip"] = val.service_ip
                check_dic["run_result"] = val.run_result
                check_dic["create_time"] = str(val.create_time)

                check_list.append(check_dic)

            obj_dic["page_num"] = page_num
            obj_dic["page_present"] = page_present
            obj_dic["total_size"] = total_size
            obj_dic["page_prev"] = page_prev
            obj_dic["page_next"] = page_next
            obj_dic["list"] = check_list

            if len(check_list) == 0:
                return jsonify(data=obj_dic, statusCode=RET.OK, msg="暂无查询内容")
            else:
                return jsonify(data=obj_dic, statusCode=RET.OK, msg="查询成功")

        else:
            obj_dic = {}
            check_list = []

            if run_result == 0:
                # 查询符合四级节点的所有监控数据，统计分页
                try:
                    page_list = db.session.query(db_mysql.MonitorResult).\
                        filter(db_mysql.MonitorResult.four_node == four_node).order_by(db_mysql.MonitorResult.create_time.desc()).\
                        paginate(int(page), int(limit), False)

                    db.session.commit()

                except IntegrityError as e:
                    # 数据库操作错误后的回滚
                    db.session.rollback()
                    current_app.logger.error(e)
                    return jsonify(statusCode=RET.DATAERR, msg="查询失败")
                db.session.close()

                # 获取总页数
                page_num = page_list.pages
                # 当前页数
                page_present = page_list.page
                # 是否存在上一页
                page_prev = page_list.has_prev
                # 是否存在下一页
                page_next = page_list.has_next
                # 总条数
                total_size = page_list.total

                # 查询符合四级节点的所有检测数据，按时间倒序排列
                try:
                    report_list = db.session.query(db_mysql.MonitorResult).\
                        filter(db_mysql.MonitorResult.four_node == four_node).order_by(db_mysql.MonitorResult.create_time.desc()).\
                        limit(limit).offset((page - 1) * limit)

                    db.session.commit()
                except IntegrityError as e:

                    # 数据库操作错误后的回滚
                    db.session.rollback()
                    current_app.logger.error(e)
                    return jsonify(statusCode=RET.DATAERR, msg="查询失败")
                db.session.close()

                for val in report_list:
                    check_dic = {}
                    check_dic["id"] = val.id
                    one_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == val.one_node)
                    for one in one_list:
                        check_dic["one_node"] = one.filename
                    two_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == val.two_node)
                    for two in two_list:
                        check_dic["two_node"] = two.filename
                    three_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == val.three_node)
                    for three in three_list:
                        check_dic["three_node"] = three.filename
                    four_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == val.four_node)
                    for four in four_list:
                        check_dic["four_node"] = four.filename
                    check_dic["service_name"] = val.service_name
                    check_dic["service_ip"] = val.service_ip
                    check_dic["run_result"] = val.run_result
                    check_dic["create_time"] = str(val.create_time)

                    check_list.append(check_dic)

                obj_dic["page_num"] = page_num
                obj_dic["page_present"] = page_present
                obj_dic["total_size"] = total_size
                obj_dic["page_prev"] = page_prev
                obj_dic["page_next"] = page_next
                obj_dic["list"] = check_list

                if len(check_list) == 0:
                    return jsonify(data=obj_dic, statusCode=RET.OK, msg="暂无查询内容")
                else:
                    return jsonify(data=obj_dic, statusCode=RET.OK, msg="查询成功")

            elif run_result == 1:
                # 查询符合四级节点的所有监控数据，统计分页
                try:
                    page_list = db.session.query(db_mysql.MonitorResult). \
                        filter(db_mysql.MonitorResult.four_node == four_node).filter(db_mysql.MonitorResult.run_result == 1).\
                        order_by(db_mysql.MonitorResult.create_time.desc()).paginate(int(page), int(limit), False)

                    db.session.commit()

                except IntegrityError as e:
                    # 数据库操作错误后的回滚
                    db.session.rollback()
                    current_app.logger.error(e)
                    return jsonify(statusCode=RET.DATAERR, msg="查询失败")
                db.session.close()

                # 获取总页数
                page_num = page_list.pages
                # 当前页数
                page_present = page_list.page
                # 是否存在上一页
                page_prev = page_list.has_prev
                # 是否存在下一页
                page_next = page_list.has_next
                # 总条数
                total_size = page_list.total

                # 查询符合四级节点的所有检测数据，按时间倒序排列
                try:
                    report_list = db.session.query(db_mysql.MonitorResult). \
                        filter(db_mysql.MonitorResult.four_node == four_node).filter(db_mysql.MonitorResult.run_result == 1).\
                        order_by(db_mysql.MonitorResult.create_time.desc()).limit(limit).offset((page - 1) * limit)

                    db.session.commit()
                except IntegrityError as e:

                    # 数据库操作错误后的回滚
                    db.session.rollback()
                    current_app.logger.error(e)
                    return jsonify(statusCode=RET.DATAERR, msg="查询失败")
                db.session.close()

                for val in report_list:
                    check_dic = {}
                    check_dic["id"] = val.id
                    one_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == val.one_node)
                    for one in one_list:
                        check_dic["one_node"] = one.filename
                    two_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == val.two_node)
                    for two in two_list:
                        check_dic["two_node"] = two.filename
                    three_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == val.three_node)
                    for three in three_list:
                        check_dic["three_node"] = three.filename
                    four_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == val.four_node)
                    for four in four_list:
                        check_dic["four_node"] = four.filename
                    check_dic["service_name"] = val.service_name
                    check_dic["service_ip"] = val.service_ip
                    check_dic["run_result"] = val.run_result
                    check_dic["create_time"] = str(val.create_time)

                    check_list.append(check_dic)

                obj_dic["page_num"] = page_num
                obj_dic["page_present"] = page_present
                obj_dic["total_size"] = total_size
                obj_dic["page_prev"] = page_prev
                obj_dic["page_next"] = page_next
                obj_dic["list"] = check_list

                if len(check_list) == 0:
                    return jsonify(data=obj_dic, statusCode=RET.OK, msg="暂无查询内容")
                else:
                    return jsonify(data=obj_dic, statusCode=RET.OK, msg="查询成功")

            elif run_result == 2:
                # 查询符合四级节点的所有监控数据，统计分页
                try:
                    page_list = db.session.query(db_mysql.MonitorResult). \
                        filter(db_mysql.MonitorResult.four_node == four_node).filter(db_mysql.MonitorResult.run_result >= 2 ).\
                        order_by(db_mysql.MonitorResult.create_time.desc()).paginate(int(page), int(limit), False)

                    db.session.commit()

                except IntegrityError as e:
                    # 数据库操作错误后的回滚
                    db.session.rollback()
                    current_app.logger.error(e)
                    return jsonify(statusCode=RET.DATAERR, msg="查询失败")
                db.session.close()

                # 获取总页数
                page_num = page_list.pages
                # 当前页数
                page_present = page_list.page
                # 是否存在上一页
                page_prev = page_list.has_prev
                # 是否存在下一页
                page_next = page_list.has_next
                # 总条数
                total_size = page_list.total

                # 查询符合四级节点的所有检测数据，按时间倒序排列
                try:
                    report_list = db.session.query(db_mysql.MonitorResult). \
                        filter(db_mysql.MonitorResult.four_node == four_node).filter(db_mysql.MonitorResult.run_result >= 2).\
                        order_by(db_mysql.MonitorResult.create_time.desc()).limit(limit).offset((page - 1) * limit)

                    db.session.commit()
                except IntegrityError as e:

                    # 数据库操作错误后的回滚
                    db.session.rollback()
                    current_app.logger.error(e)
                    return jsonify(statusCode=RET.DATAERR, msg="查询失败")
                db.session.close()

                for val in report_list:
                    check_dic = {}
                    check_dic["id"] = val.id
                    one_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == val.one_node)
                    for one in one_list:
                        check_dic["one_node"] = one.filename
                    two_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == val.two_node)
                    for two in two_list:
                        check_dic["two_node"] = two.filename
                    three_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == val.three_node)
                    for three in three_list:
                        check_dic["three_node"] = three.filename
                    four_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == val.four_node)
                    for four in four_list:
                        check_dic["four_node"] = four.filename
                    check_dic["service_name"] = val.service_name
                    check_dic["service_ip"] = val.service_ip
                    check_dic["run_result"] = val.run_result
                    check_dic["create_time"] = str(val.create_time)

                    check_list.append(check_dic)

                obj_dic["page_num"] = page_num
                obj_dic["page_present"] = page_present
                obj_dic["total_size"] = total_size
                obj_dic["page_prev"] = page_prev
                obj_dic["page_next"] = page_next
                obj_dic["list"] = check_list

                if len(check_list) == 0:
                    return jsonify(data=obj_dic, statusCode=RET.OK, msg="暂无查询内容")
                else:
                    return jsonify(data=obj_dic, statusCode=RET.OK, msg="查询成功")


class DetailsMonitor(Resource):

    # 查询监控结果详情
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        id = req_dict.get("id")  # 监控id

        obj_dic = {}
        check_list = []

        try:
            det_list = db.session.query(db_mysql.MonitorResult).filter(db_mysql.MonitorResult.id == id)

            db.session.commit()
        except IntegrityError as e:

            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")
        db.session.close()

        for val in det_list:
            check_dic = {}
            check_dic["result_details"] = val.result_details

            check_list.append(check_dic)

        return jsonify(data=check_list, statusCode=RET.OK, msg="查询成功")


class View(Resource):

    # 按服务查询
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        project_type = req_dict.get("project_type")  # 项目工程id

        check_list = []
        one_tree = []
        # 取出project=5的一级节点tree_id
        try:
            id_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.project_type == project_type,
                                                             db_mysql.Tree.pid == 0)

            db.session.commit()

        except IntegrityError as e:
            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")
        db.session.close()

        for tree_id in id_list:
            one_tree.append(tree_id.id)

        # 遍历tree_list，判断is_new=1的数据是否有run_result=2的
        for one_id in one_tree:

            obj_dic = {}
            # 取tree第一个节点的对应名称
            name_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == one_id)
            for name in name_list:
                obj_dic["node_id"] = one_id
                obj_dic["one_node"] = name.filename

            res_list = db.session.query(db_mysql.MonitorResult).\
                filter(db_mysql.MonitorResult.one_node == one_id, db_mysql.MonitorResult.is_new == 1).\
                order_by(db_mysql.MonitorResult.create_time.desc())

            for i in res_list:
                if i.run_result == 2:
                    obj_dic["run_result"] = 2
                    obj_dic["run_time"] = str(i.create_time)
                    break
                else:
                    obj_dic["run_result"] = 1
                    obj_dic["run_time"] = str(i.create_time)
            check_list.append(obj_dic)

        return jsonify(data=check_list, statusCode=RET.OK, msg="查询成功")


class Filter(Resource):

    # 根据四级节点和结果筛选监控
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        four_node = req_dict.get("four_node")  # 四级节点id
        is_new = req_dict.get("is_new")   # 结果是否为最新 1为是，2为否

        check_list = []

        # 按四级节点和is_new查询数据，按时间倒序排列
        try:
            report_list = db.session.query(db_mysql.MonitorResult).\
                filter(db_mysql.MonitorResult.four_node == four_node, db_mysql.MonitorResult.is_new == is_new)

            db.session.commit()
        except IntegrityError as e:

            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")
        db.session.close()

        for val in report_list:
            check_dic = {}
            check_dic["id"] = val.id
            check_dic["one_node"] = val.one_node
            check_dic["two_node"] = val.two_node
            check_dic["three_node"] = val.three_node
            check_dic["four_node"] = val.four_node
            check_dic["service_name"] = val.service_name
            check_dic["service_ip"] = val.service_ip
            check_dic["result_details"] = val.result_details
            check_dic["run_result"] = val.run_result
            check_dic["is_new"] = val.is_new

            check_list.append(check_dic)

        # if len(check_list) == 0:
        #     return jsonify(statusCode=RET.OK, msg="暂无查询内容")
        # else:
        return jsonify(data=check_list, statusCode=RET.OK, msg="查询成功")


# 新增监控报告接口
api.add_resource(AddMonitor, '/addmonitor')
# 根据四级节点和运行结果筛选监控接口
api.add_resource(FilterMonitor, '/filtermonitor')
# 查询监控详情接口
api.add_resource(DetailsMonitor, '/detailsmonitor')
# 视图查询接口
api.add_resource(View, '/view')
# 按四级节点和is_new查询接口
api.add_resource(Filter, '/filter')
