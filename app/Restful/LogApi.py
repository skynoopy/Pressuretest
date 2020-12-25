from flask import (Blueprint, request, current_app, jsonify)
from flask_restful import Resource, Api
from app.exts import db
from app import db_mysql
from sqlalchemy.exc import IntegrityError
from .Httpauth import authtoken
from app.api_status.response_code import RET
# from flask_paginate import Pagination, get_page_args


LogApi = Blueprint('LogApi', __name__, url_prefix='/LogApi')
api = Api(LogApi)


class ReportLog(Resource):
    decorators = [authtoken.login_required]

    # 压测日志按用户名、项目、日期查询
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        tree_id = req_dict.get("tree_id")  # 项目id
        uid = req_dict.get("uid")  # 用户id，为0时代表all
        page = req_dict.get("page")    # 分页
        limit = req_dict.get("limit")   # 每页条数
        starttime = req_dict.get("starttime")   # 开始时间
        endtime = req_dict.get("endtime")   # 结束时间

        obj_dic = {}
        check_list = []

        # 查询项目下所有用户的压测记录
        if uid == 0:    # 按所有用户查询
            if starttime is None and endtime is None:   # 不按日期查询
                try:
                    page_list = db.session.query(db_mysql.ReportLog).\
                        filter(db_mysql.ReportLog.tree_id == tree_id).order_by(db_mysql.ReportLog.create_time.desc()).\
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

                try:
                    report_list = db.session.query(db_mysql.ReportLog).\
                        filter(db_mysql.ReportLog.tree_id == tree_id).order_by(db_mysql.ReportLog.create_time.desc()).\
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
                    check_dic["report_name"] = val.report_name
                    check_dic["uid"] = val.uid
                    u_val = db.session.query(db_mysql.User).filter(db_mysql.User.id == val.uid)
                    for u in u_val:
                        check_dic["name"] = u.name
                    check_dic["create_time"] = str(val.create_time)

                    check_list.append(check_dic)

                obj_dic["page_num"] = page_num
                obj_dic["page_present"] = page_present
                obj_dic["total_size"] = total_size
                obj_dic["page_prev"] = page_prev
                obj_dic["page_next"] = page_next
                obj_dic["list"] = check_list

                return jsonify(data=obj_dic, statusCode=RET.OK, msg="查询成功")

            else:   # 按日期查询
                try:
                    page_list = db.session.query(db_mysql.ReportLog). \
                        filter(db_mysql.ReportLog.tree_id == tree_id).filter(db_mysql.ReportLog.create_time >= starttime)\
                        .filter(db_mysql.ReportLog.create_time <= endtime)\
                        .order_by(db_mysql.ReportLog.create_time.desc()). \
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

                try:
                    report_list = db.session.query(db_mysql.ReportLog). \
                        filter(db_mysql.ReportLog.tree_id == tree_id).filter(db_mysql.ReportLog.create_time >= starttime).\
                        filter(db_mysql.ReportLog.create_time <= endtime).order_by(db_mysql.ReportLog.create_time.desc()). \
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
                    check_dic["report_name"] = val.report_name
                    check_dic["uid"] = val.uid
                    u_val = db.session.query(db_mysql.User).filter(db_mysql.User.id == val.uid)
                    for u in u_val:
                        check_dic["name"] = u.name
                    check_dic["create_time"] = str(val.create_time)

                    check_list.append(check_dic)

                obj_dic["page_num"] = page_num
                obj_dic["page_present"] = page_present
                obj_dic["total_size"] = total_size
                obj_dic["page_prev"] = page_prev
                obj_dic["page_next"] = page_next
                obj_dic["list"] = check_list

                return jsonify(data=obj_dic, statusCode=RET.OK, msg="查询成功")

        else:   # 按uid查询
            if starttime is None and endtime is None:
                try:
                    report_list = db.session.query(db_mysql.ReportLog).\
                        filter(db_mysql.ReportLog.tree_id == tree_id, db_mysql.ReportLog.uid == uid).\
                        order_by(db_mysql.ReportLog.create_time.desc()).limit(limit).offset((page - 1) * limit)
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
                    check_dic["report_name"] = val.report_name
                    check_dic["uid"] = val.uid
                    u_val = db.session.query(db_mysql.User).filter(db_mysql.User.id == val.uid)
                    for u in u_val:
                        check_dic["name"] = u.name
                    check_dic["create_time"] = str(val.create_time)

                    check_list.append(check_dic)

                # 不存在提示用户没有记录
                if len(check_list) == 0:
                    return jsonify(statusCode=RET.DATAERR, msg="暂时没有压测记录")

                # 存在返回对应记录
                else:
                    try:
                        page_list = db.session.query(db_mysql.ReportLog). \
                            filter(db_mysql.ReportLog.tree_id == tree_id, db_mysql.ReportLog.uid == uid). \
                            order_by(db_mysql.ReportLog.create_time.desc()).paginate(int(page), int(limit), False)
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

                    # 将数据存入obj_list
                    obj_dic["page_num"] = page_num
                    obj_dic["page_present"] = page_present
                    obj_dic["total_size"] = total_size
                    obj_dic["page_prev"] = page_prev
                    obj_dic["page_next"] = page_next
                    obj_dic["list"] = check_list

                    return jsonify(data=obj_dic, statusCode=RET.OK, msg="查询成功")

            else:   # 按日期查询
                try:
                    report_list = db.session.query(db_mysql.ReportLog). \
                        filter(db_mysql.ReportLog.tree_id == tree_id, db_mysql.ReportLog.uid == uid). \
                        filter(db_mysql.ReportLog.create_time >= starttime).filter(db_mysql.ReportLog.create_time <= endtime). \
                        order_by(db_mysql.ReportLog.create_time.desc()).limit(limit).offset((page - 1) * limit)
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
                    check_dic["report_name"] = val.report_name
                    check_dic["uid"] = val.uid
                    u_val = db.session.query(db_mysql.User).filter(db_mysql.User.id == val.uid)
                    for u in u_val:
                        check_dic["name"] = u.name
                    check_dic["create_time"] = str(val.create_time)

                    check_list.append(check_dic)

                # 不存在提示用户没有记录
                if len(check_list) == 0:
                    return jsonify(statusCode=RET.DATAERR, msg="暂时没有压测记录")

                # 存在返回对应记录
                else:
                    try:
                        page_list = db.session.query(db_mysql.ReportLog). \
                            filter(db_mysql.ReportLog.tree_id == tree_id, db_mysql.ReportLog.uid == uid). \
                            filter(db_mysql.ReportLog.create_time >= starttime).filter(db_mysql.ReportLog.create_time <= endtime). \
                            order_by(db_mysql.ReportLog.create_time.desc()).paginate(int(page), int(limit), False)
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

                    # 将数据存入obj_list
                    obj_dic["page_num"] = page_num
                    obj_dic["page_present"] = page_present
                    obj_dic["total_size"] = total_size
                    obj_dic["page_prev"] = page_prev
                    obj_dic["page_next"] = page_next
                    obj_dic["list"] = check_list

                    return jsonify(data=obj_dic, statusCode=RET.OK, msg="查询成功")


class AddReportLog(Resource):

    # 新增用户压测报告
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        uid = req_dict.get("uid")  # 用户id
        tree_id = req_dict.get("tree_id")   # 项目id
        report_name = req_dict.get("report_name")   # 报告名称
        report_info = req_dict.get("report_info")   # 报告内容

        try:
            tree_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == tree_id)
            db.session.commit()
        except IntegrityError as e:

            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")
        db.session.close()

        for i in tree_list:
            try:
                db.session.add(
                    db_mysql.ReportLog(uid=uid, tree_id=tree_id, tree_name=i.filename,
                                       report_name=report_name, report_info=report_info))
                db.session.commit()

            except IntegrityError as e:
                # 数据库操作错误后的回滚
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(statusCode=RET.DATAERR, msg="数据创建失败")
            db.session.close()
            return jsonify(statusCode=RET.OK, msg="添加成功")


class ResultLog(ReportLog):
    decorators = [authtoken.login_required]

    # 查询压测日志结果
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        id = req_dict.get("id")  # 压测日志id

        check_list = []

        try:
            report_list = db.session.query(db_mysql.ReportLog).filter(db_mysql.ReportLog.id == id)
            db.session.commit()
        except IntegrityError as e:

            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")
        db.session.close()

        for val in report_list:
            check_dic = {}
            check_dic['report_info'] = val.report_info

            check_list.append(check_dic)

        return jsonify(data=check_list, statusCode=RET.OK, msg="查询成功")


class AddOperationLog(Resource):

    # 新增用户操作记录
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        uid = req_dict.get("uid")  # 用户id
        tree_id = req_dict.get("tree_id")   # 项目id
        project_type = req_dict.get("project_type")    # 项目工程id 2为压测中心，3为用例管理
        operation_content = req_dict.get("operation_content")   # 操作内容
        operation_result = req_dict.get("operation_result")   # 操作结果 1成功，2失败

        try:
            user_list = db.session.query(db_mysql.User).filter(db_mysql.User.id == uid)
            db.session.commit()
        except IntegrityError as e:

            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")
        db.session.close()

        for i in user_list:
            try:
                db.session.add(
                    db_mysql.OperationLog(uid=uid, name=i.name, username=i.username, tree_id=tree_id, project_type=project_type,
                                          operation_content=operation_content, operation_result=operation_result))
                db.session.commit()

            except IntegrityError as e:
                # 数据库操作错误后的回滚
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(statusCode=RET.DATAERR, msg="数据创建失败")
            db.session.close()
            return jsonify(statusCode=RET.OK, msg="添加成功")


class QueryOperation(Resource):
    decorators = [authtoken.login_required]

    # 操作记录按用户名、项目、日期查询
    def post(self):
        # 获取请求的json数据, 返回字典
        req_dict = request.get_json()
        tree_id = req_dict.get("tree_id")  # 项目id
        uid = req_dict.get("uid")  # 用户id，为0时代表all
        result = req_dict.get("result")  # 运行结果，1成功，2失败
        starttime = req_dict.get("starttime")   # 开始时间
        endtime = req_dict.get("endtime")   # 结束时间
        page = req_dict.get("page")    # 分页
        limit = req_dict.get("limit")  # 每页条数

        obj_dic = {}
        check_list = []

        # 查询项目下所有用户的压测记录,统计分页
        if uid == 0:
            # 操作结果为全部时
            if result == 0:
                # 不按日期查询
                if starttime is None and endtime is None:
                    try:
                        page_list = db.session.query(db_mysql.OperationLog).filter(db_mysql.OperationLog.tree_id == tree_id).\
                            order_by(db_mysql.OperationLog.create_time.desc()).paginate(int(page), int(limit), False)

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

                    try:
                        report_list = db.session.query(db_mysql.OperationLog).filter(db_mysql.OperationLog.tree_id == tree_id).\
                            order_by(db_mysql.OperationLog.create_time.desc()).limit(limit).offset((page - 1) * limit)

                        db.session.commit()
                    except IntegrityError as e:

                        # 数据库操作错误后的回滚
                        db.session.rollback()
                        current_app.logger.error(e)
                        return jsonify(statusCode=RET.DATAERR, msg="查询失败")
                    db.session.close()

                    try:
                        tree_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == tree_id)

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
                        check_dic["uid"] = val.uid
                        check_dic["name"] = val.name
                        check_dic["username"] = val.username
                        if val.project_type == 2:
                            check_dic["project_type"] = "压测中心"
                        elif val.project_type == 3:
                            check_dic["project_type"] = "用例管理"
                        for i in tree_list:
                            check_dic["tree_name"] = i.filename
                        check_dic["operation_content"] = val.operation_content
                        check_dic["create_time"] = str(val.create_time)
                        check_dic["operation_result"] = val.operation_result

                        check_list.append(check_dic)

                    if len(check_list) == 0:
                        return jsonify(statusCode=RET.DATAERR, msg="暂时没有操作记录")

                    else:
                        obj_dic["page_num"] = page_num
                        obj_dic["page_present"] = page_present
                        obj_dic["total_size"] = total_size
                        obj_dic["page_prev"] = page_prev
                        obj_dic["page_next"] = page_next
                        obj_dic["list"] = check_list

                        return jsonify(data=obj_dic, statusCode=RET.OK, msg="查询成功")
                # 按日期查询
                else:
                    try:
                        page_list = db.session.query(db_mysql.OperationLog)\
                            .filter(db_mysql.OperationLog.tree_id == tree_id)\
                            .filter(db_mysql.OperationLog.create_time >= starttime)\
                            .filter(db_mysql.OperationLog.create_time <= endtime) \
                            .order_by(db_mysql.OperationLog.create_time.desc()).paginate(int(page), int(limit), False)

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

                    try:
                        report_list = db.session.query(db_mysql.OperationLog).filter(
                            db_mysql.OperationLog.tree_id == tree_id). \
                            filter(db_mysql.OperationLog.create_time >= starttime).\
                            filter(db_mysql.OperationLog.create_time <= endtime). \
                            order_by(db_mysql.OperationLog.create_time.desc()).limit(limit).offset((page - 1) * limit)

                        db.session.commit()
                    except IntegrityError as e:

                        # 数据库操作错误后的回滚
                        db.session.rollback()
                        current_app.logger.error(e)
                        return jsonify(statusCode=RET.DATAERR, msg="查询失败")
                    db.session.close()

                    try:
                        tree_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == tree_id)

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
                        check_dic["uid"] = val.uid
                        check_dic["name"] = val.name
                        check_dic["username"] = val.username
                        if val.project_type == 2:
                            check_dic["project_type"] = "压测中心"
                        elif val.project_type == 3:
                            check_dic["project_type"] = "用例管理"
                        for i in tree_list:
                            check_dic["tree_name"] = i.filename
                        check_dic["operation_content"] = val.operation_content
                        check_dic["create_time"] = str(val.create_time)
                        check_dic["operation_result"] = val.operation_result

                        check_list.append(check_dic)

                    if len(check_list) == 0:
                        return jsonify(statusCode=RET.DATAERR, msg="暂时没有操作记录")

                    else:
                        obj_dic["page_num"] = page_num
                        obj_dic["page_present"] = page_present
                        obj_dic["total_size"] = total_size
                        obj_dic["page_prev"] = page_prev
                        obj_dic["page_next"] = page_next
                        obj_dic["list"] = check_list

                        return jsonify(data=obj_dic, statusCode=RET.OK, msg="查询成功")
            # 操作结果不为全部时
            else:
                if starttime is None and endtime is None:
                    try:
                        page_list = db.session.query(db_mysql.OperationLog).filter(
                            db_mysql.OperationLog.tree_id == tree_id, db_mysql.OperationLog.operation_result == result). \
                            order_by(db_mysql.OperationLog.create_time.desc()).paginate(int(page), int(limit), False)

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

                    try:
                        report_list = db.session.query(db_mysql.OperationLog).filter(
                            db_mysql.OperationLog.tree_id == tree_id, db_mysql.OperationLog.operation_result == result). \
                            order_by(db_mysql.OperationLog.create_time.desc()).limit(limit).offset((page - 1) * limit)

                        db.session.commit()
                    except IntegrityError as e:

                        # 数据库操作错误后的回滚
                        db.session.rollback()
                        current_app.logger.error(e)
                        return jsonify(statusCode=RET.DATAERR, msg="查询失败")
                    db.session.close()

                    try:
                        tree_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == tree_id)

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
                        check_dic["uid"] = val.uid
                        check_dic["name"] = val.name
                        check_dic["username"] = val.username
                        if val.project_type == 2:
                            check_dic["project_type"] = "压测中心"
                        elif val.project_type == 3:
                            check_dic["project_type"] = "用例管理"
                        for i in tree_list:
                            check_dic["tree_name"] = i.filename
                        check_dic["operation_content"] = val.operation_content
                        check_dic["create_time"] = str(val.create_time)
                        check_dic["operation_result"] = val.operation_result

                        check_list.append(check_dic)

                    if len(check_list) == 0:
                        return jsonify(statusCode=RET.DATAERR, msg="暂时没有操作记录")

                    else:
                        obj_dic["page_num"] = page_num
                        obj_dic["page_present"] = page_present
                        obj_dic["total_size"] = total_size
                        obj_dic["page_prev"] = page_prev
                        obj_dic["page_next"] = page_next
                        obj_dic["list"] = check_list

                        return jsonify(data=obj_dic, statusCode=RET.OK, msg="查询成功")
                else:
                    try:
                        page_list = db.session.query(db_mysql.OperationLog).filter(
                            db_mysql.OperationLog.tree_id == tree_id, db_mysql.OperationLog.operation_result == result). \
                            filter(db_mysql.OperationLog.create_time >= starttime).\
                            filter(db_mysql.OperationLog.create_time <= endtime). \
                            order_by(db_mysql.OperationLog.create_time.desc()).paginate(int(page), int(limit), False)

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

                    try:
                        report_list = db.session.query(db_mysql.OperationLog).filter(
                            db_mysql.OperationLog.tree_id == tree_id, db_mysql.OperationLog.operation_result == result,
                            db_mysql.OperationLog.create_time >= starttime, db_mysql.OperationLog.create_time <= endtime). \
                            order_by(db_mysql.OperationLog.create_time.desc()).limit(limit).offset((page - 1) * limit)

                        db.session.commit()
                    except IntegrityError as e:

                        # 数据库操作错误后的回滚
                        db.session.rollback()
                        current_app.logger.error(e)
                        return jsonify(statusCode=RET.DATAERR, msg="查询失败")
                    db.session.close()

                    try:
                        tree_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == tree_id)

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
                        check_dic["uid"] = val.uid
                        check_dic["name"] = val.name
                        check_dic["username"] = val.username
                        if val.project_type == 2:
                            check_dic["project_type"] = "压测中心"
                        elif val.project_type == 3:
                            check_dic["project_type"] = "用例管理"
                        for i in tree_list:
                            check_dic["tree_name"] = i.filename
                        check_dic["operation_content"] = val.operation_content
                        check_dic["create_time"] = str(val.create_time)
                        check_dic["operation_result"] = val.operation_result

                        check_list.append(check_dic)

                    if len(check_list) == 0:
                        return jsonify(statusCode=RET.DATAERR, msg="暂时没有操作记录")

                    else:
                        obj_dic["page_num"] = page_num
                        obj_dic["page_present"] = page_present
                        obj_dic["total_size"] = total_size
                        obj_dic["page_prev"] = page_prev
                        obj_dic["page_next"] = page_next
                        obj_dic["list"] = check_list

                        return jsonify(data=obj_dic, statusCode=RET.OK, msg="查询成功")

        else:
            # 操作结果为全部时
            if result == 0:
                if starttime is None and endtime is None:
                    try:
                        report_list = db.session.query(db_mysql.OperationLog).\
                            filter(db_mysql.OperationLog.tree_id == tree_id, db_mysql.OperationLog.uid == uid).\
                            order_by(db_mysql.OperationLog.create_time.desc()).limit(limit).offset((page - 1) * limit)
                        db.session.commit()

                    except IntegrityError as e:

                        # 数据库操作错误后的回滚
                        db.session.rollback()
                        current_app.logger.error(e)
                        return jsonify(statusCode=RET.DATAERR, msg="查询失败")
                    db.session.close()

                    try:
                        tree_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == tree_id)

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
                        check_dic["uid"] = val.uid
                        check_dic["name"] = val.name
                        check_dic["username"] = val.username
                        if val.project_type == 2:
                            check_dic["project_type"] = "压测中心"
                        elif val.project_type == 3:
                            check_dic["project_type"] = "用例管理"
                        for i in tree_list:
                            check_dic["tree_name"] = i.filename
                        check_dic["operation_content"] = val.operation_content
                        check_dic["create_time"] = str(val.create_time)
                        check_dic["operation_result"] = val.operation_result

                        check_list.append(check_dic)

                    # 不存在提示用户没有记录
                    if len(check_list) == 0:
                        return jsonify(statusCode=RET.DATAERR, msg="暂时没有操作记录")
                    # 存在返回对应记录
                    else:
                        # 获取分页信息
                        try:
                            page_list = db.session.query(db_mysql.OperationLog).filter(
                                db_mysql.OperationLog.tree_id == tree_id). \
                                order_by(db_mysql.OperationLog.create_time.desc()).paginate(int(page), int(limit), False)

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

                        # 将分页数据和请求页内容存入obj_list
                        obj_dic["page_num"] = page_num
                        obj_dic["page_present"] = page_present
                        obj_dic["total_size"] = total_size
                        obj_dic["page_prev"] = page_prev
                        obj_dic["page_next"] = page_next
                        obj_dic["list"] = check_list

                        return jsonify(data=obj_dic, statusCode=RET.OK, msg="查询成功")
                else:
                    try:
                        report_list = db.session.query(db_mysql.OperationLog). \
                            filter(db_mysql.OperationLog.tree_id == tree_id, db_mysql.OperationLog.uid == uid,
                                   db_mysql.OperationLog.create_time >= starttime, db_mysql.OperationLog.create_time <= endtime). \
                            order_by(db_mysql.OperationLog.create_time.desc()).limit(limit).offset((page - 1) * limit)
                        db.session.commit()

                    except IntegrityError as e:

                        # 数据库操作错误后的回滚
                        db.session.rollback()
                        current_app.logger.error(e)
                        return jsonify(statusCode=RET.DATAERR, msg="查询失败")
                    db.session.close()

                    try:
                        tree_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == tree_id)

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
                        check_dic["uid"] = val.uid
                        check_dic["name"] = val.name
                        check_dic["username"] = val.username
                        if val.project_type == 2:
                            check_dic["project_type"] = "压测中心"
                        elif val.project_type == 3:
                            check_dic["project_type"] = "用例管理"
                        for i in tree_list:
                            check_dic["tree_name"] = i.filename
                        check_dic["operation_content"] = val.operation_content
                        check_dic["create_time"] = str(val.create_time)
                        check_dic["operation_result"] = val.operation_result

                        check_list.append(check_dic)

                    # 不存在提示用户没有记录
                    if len(check_list) == 0:
                        return jsonify(statusCode=RET.DATAERR, msg="暂时没有操作记录")
                    # 存在返回对应记录
                    else:
                        # 获取分页信息
                        try:
                            page_list = db.session.query(db_mysql.OperationLog).filter(
                                db_mysql.OperationLog.tree_id == tree_id,
                                db_mysql.OperationLog.create_time >= starttime, db_mysql.OperationLog.create_time <= endtime). \
                                order_by(db_mysql.OperationLog.create_time.desc()).paginate(int(page), int(limit), False)

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

                        # 将分页数据和请求页内容存入obj_list
                        obj_dic["page_num"] = page_num
                        obj_dic["page_present"] = page_present
                        obj_dic["total_size"] = total_size
                        obj_dic["page_prev"] = page_prev
                        obj_dic["page_next"] = page_next
                        obj_dic["list"] = check_list

                        return jsonify(data=obj_dic, statusCode=RET.OK, msg="查询成功")
            else:
                if starttime is None and endtime is None:
                    try:
                        report_list = db.session.query(db_mysql.OperationLog). \
                            filter(db_mysql.OperationLog.tree_id == tree_id, db_mysql.OperationLog.uid == uid,
                                   db_mysql.OperationLog.operation_result == result). \
                            order_by(db_mysql.OperationLog.create_time.desc()).limit(limit).offset((page - 1) * limit)
                        db.session.commit()

                    except IntegrityError as e:

                        # 数据库操作错误后的回滚
                        db.session.rollback()
                        current_app.logger.error(e)
                        return jsonify(statusCode=RET.DATAERR, msg="查询失败")
                    db.session.close()

                    try:
                        tree_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == tree_id)

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
                        check_dic["uid"] = val.uid
                        check_dic["name"] = val.name
                        check_dic["username"] = val.username
                        if val.project_type == 2:
                            check_dic["project_type"] = "压测中心"
                        elif val.project_type == 3:
                            check_dic["project_type"] = "用例管理"
                        for i in tree_list:
                            check_dic["tree_name"] = i.filename
                        check_dic["operation_content"] = val.operation_content
                        check_dic["create_time"] = str(val.create_time)
                        check_dic["operation_result"] = val.operation_result

                        check_list.append(check_dic)

                    # 不存在提示用户没有记录
                    if len(check_list) == 0:
                        return jsonify(statusCode=RET.DATAERR, msg="暂时没有操作记录")
                    # 存在返回对应记录
                    else:
                        # 获取分页信息
                        try:
                            page_list = db.session.query(db_mysql.OperationLog).filter(
                                db_mysql.OperationLog.tree_id == tree_id, db_mysql.OperationLog.operation_result == result). \
                                order_by(db_mysql.OperationLog.create_time.desc()).paginate(int(page), int(limit), False)

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

                        # 将分页数据和请求页内容存入obj_list
                        obj_dic["page_num"] = page_num
                        obj_dic["page_present"] = page_present
                        obj_dic["total_size"] = total_size
                        obj_dic["page_prev"] = page_prev
                        obj_dic["page_next"] = page_next
                        obj_dic["list"] = check_list

                        return jsonify(data=obj_dic, statusCode=RET.OK, msg="查询成功")
                else:
                    try:
                        report_list = db.session.query(db_mysql.OperationLog). \
                            filter(db_mysql.OperationLog.tree_id == tree_id, db_mysql.OperationLog.uid == uid,
                                   db_mysql.OperationLog.operation_result == result,
                                   db_mysql.OperationLog.create_time >= starttime,
                                   db_mysql.OperationLog.create_time <= endtime). \
                            order_by(db_mysql.OperationLog.create_time.desc()).limit(limit).offset((page - 1) * limit)
                        db.session.commit()

                    except IntegrityError as e:

                        # 数据库操作错误后的回滚
                        db.session.rollback()
                        current_app.logger.error(e)
                        return jsonify(statusCode=RET.DATAERR, msg="查询失败")
                    db.session.close()

                    try:
                        tree_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.id == tree_id)

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
                        check_dic["uid"] = val.uid
                        check_dic["name"] = val.name
                        check_dic["username"] = val.username
                        if val.project_type == 2:
                            check_dic["project_type"] = "压测中心"
                        elif val.project_type == 3:
                            check_dic["project_type"] = "用例管理"
                        for i in tree_list:
                            check_dic["tree_name"] = i.filename
                        check_dic["operation_content"] = val.operation_content
                        check_dic["create_time"] = str(val.create_time)
                        check_dic["operation_result"] = val.operation_result

                        check_list.append(check_dic)

                    # 不存在提示用户没有记录
                    if len(check_list) == 0:
                        return jsonify(statusCode=RET.DATAERR, msg="暂时没有操作记录")
                    # 存在返回对应记录
                    else:
                        # 获取分页信息
                        try:
                            page_list = db.session.query(db_mysql.OperationLog).filter(
                                db_mysql.OperationLog.tree_id == tree_id,
                                db_mysql.OperationLog.operation_result == result,
                                db_mysql.OperationLog.create_time >= starttime,
                                db_mysql.OperationLog.create_time <= endtime). \
                                order_by(db_mysql.OperationLog.create_time.desc()).paginate(int(page), int(limit),
                                                                                            False)

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

                        # 将分页数据和请求页内容存入obj_list
                        obj_dic["page_num"] = page_num
                        obj_dic["page_present"] = page_present
                        obj_dic["total_size"] = total_size
                        obj_dic["page_prev"] = page_prev
                        obj_dic["page_next"] = page_next
                        obj_dic["list"] = check_list

                        return jsonify(data=obj_dic, statusCode=RET.OK, msg="查询成功")


class ProjectTree(Resource):
    # decorators = [authtoken.login_required]
    def post(self):
        req_dict = request.get_json()
        project_type = req_dict.get("project_type")

        check_list = []

        try:
            user_list = db.session.query(db_mysql.Tree).filter(db_mysql.Tree.pid == 0, db_mysql.Tree.project_type == project_type)
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
            check_dic["filename"] = raw.filename

            check_list.append(check_dic)

        return jsonify(data=check_list, statusCode=RET.OK, msg="查询成功")


# 查询压测日志接口
api.add_resource(ReportLog, '/reportlog')
# 查询压测日志结果接口
api.add_resource(ResultLog, '/resultlog')
# 新增用户操作记录
api.add_resource(AddOperationLog, '/addoperationlog')
# 查询用户操作记录
api.add_resource(QueryOperation, '/queryoperation')
# 查询压测项目下pid为0的项目
api.add_resource(ProjectTree, '/projecttree')
# 新增用户压测报告记录
api.add_resource(AddReportLog, '/addreportlog')
