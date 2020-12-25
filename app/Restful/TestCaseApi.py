from flask import (Blueprint, request, jsonify, current_app)
from flask_restful import Resource, Api
from app.exts import db
from app import db_mysql
from app.api_status.response_code import RET
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from .Httpauth import authtoken, Interface_authority
from sqlalchemy import func
import xlrd
import os, time
from pypinyin import lazy_pinyin
# from .DingTalkApi import DingTalk
from app.aps_scheduler import except_log


TestCaseApi = Blueprint('TestCaseApi', __name__, url_prefix='/TestCaseApi')
api = Api(TestCaseApi)

ALLOWED_EXTENSIONS = {'xls', 'xlsx'}


class Case(Resource):
    decorators = [authtoken.login_required]

    # 新增
    def post(self):
        # 获取请求的json数据, 从列表中取字典的值
        req_dic = request.get_json()
        case_id = req_dic.get("case_id")    # 用例id
        module_name = req_dic.get("module_name")  # 模块名
        test_item = req_dic.get("test_item")   # 测试项
        precondition = req_dic.get("precondition")   # 预置条件
        test_process = req_dic.get("test_process")   # 测试步骤
        expected_result = req_dic.get("expected_result")   # 预期结果
        test_note = req_dic.get("test_note")   # 备注

        print(req_dic)
        try:
            db.session.add(
                db_mysql.TestCase(module_name=module_name, test_item=test_item, precondition=precondition,
                                  test_process=test_process, expected_result=expected_result, test_note=test_note,
                                  case_id=case_id))
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
        req_list = request.get_json()

        for val in req_list.get("case_obj"):

            id = val.get("id")   # 用例内容id
            module_name = val.get("module_name")  # 模块名
            test_item = val.get("test_item")  # 测试项
            precondition = val.get("precondition")  # 预置条件
            test_process = val.get("test_process")  # 测试步骤
            expected_result = val.get("expected_result")  # 预期结果
            test_note = val.get("test_note")  # 备注

            try:
                case_list = db.session.query(db_mysql.TestCase).filter(db_mysql.TestCase.id == id).update(
                    {
                        "module_name": module_name,
                        "test_item": test_item,
                        "precondition": precondition,
                        "test_process": test_process,
                        "expected_result": expected_result,
                        "test_note": test_note
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
        req_list = request.get_json()
        for val in req_list.get("case_obj"):
            id = val.get("id")  # 用例内容id

            # 删除文件
            try:
                id_val = db.session.query(db_mysql.TestCase).filter(db_mysql.TestCase.id == id).delete()
                db.session.commit()
            except IntegrityError as e:
                # 数据库操作错误后的回滚
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(statusCode=RET.DATAERR, msg="删除失败")
            db.session.close()

        return jsonify(statusCode=RET.OK, msg="删除成功")


class QueryCase(Resource):
    decorators = [authtoken.login_required]

    # 查询用例内容
    def post(self):

        # 获取请求的json数据，返回字典
        req_dict = request.get_json()
        case_id = req_dict.get("case_id")  # 用例id

        check_list = []

        try:
            case_list = db.session.query(db_mysql.TestCase).filter(db_mysql.TestCase.case_id == case_id)
            db.session.commit()
        except IntegrityError as e:

            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")
        db.session.close()

        for raw in case_list:
            check_dic = {}
            check_dic["id"] = raw.id
            check_dic["case_id"] = raw.case_id
            check_dic["module_name"] = raw.module_name
            check_dic["test_item"] = raw.test_item
            check_dic["precondition"] = raw.precondition
            check_dic["test_process"] = raw.test_process
            check_dic["expected_result"] = raw.expected_result
            check_dic["test_note"] = raw.test_note
            check_dic["develop_result"] = raw.develop_result
            check_dic["develop_name"] = raw.develop_name
            check_dic["test_result"] = raw.test_result
            check_dic["test_name"] = raw.test_name
            check_dic["product_result"] = raw.product_result
            check_dic["product_name"] = raw.product_name

            check_list.append(check_dic)
            
        if len(check_list) == 0:
            return jsonify(statusCode=RET.DATAERR, msg="暂无测试用例")
        else:
            return jsonify(data=check_list, statusCode=RET.OK, msg="查询成功")


class CheckResult(Resource):
    decorators = [authtoken.login_required]

    # 修改
    def put(self):
        # 获取请求的json数据，返回字典
        req_dic = request.get_json()

        id = req_dic.get("id")  # 用例内容id
        role = req_dic.get("role")  # 角色类型：0为开发，1为测试，2为产品
        develop_result = req_dic.get("develop_result")  # 开发执行结果
        develop_name = req_dic.get("develop_name")  # 开发执行人名字
        test_result = req_dic.get("test_result")    # 测试执行结果
        test_name = req_dic.get("test_name")    # 测试执行人名字
        product_result = req_dic.get("product_result")  # 产品执行结果
        product_name = req_dic.get("product_name")  # 产品执行人名字

        # 开发提交结果
        if role == 0:
            try:
                case_list = db.session.query(db_mysql.TestCase).filter(db_mysql.TestCase.id == id).update(
                    {
                        "develop_result": develop_result,
                        "develop_name": develop_name
                    })
                db.session.commit()
            except IntegrityError as e:
                # 数据库操作错误后的回滚
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(statusCode=RET.DATAERR, msg="修改失败")
            db.session.close()
            return jsonify(statusCode=RET.OK, msg="修改成功")

        # 测试提交结果
        elif role == 1:
            try:
                case_list = db.session.query(db_mysql.TestCase).filter(db_mysql.TestCase.id == id).update(
                    {
                        "test_result": test_result,
                        "test_name": test_name
                    })
                db.session.commit()
            except IntegrityError as e:
                # 数据库操作错误后的回滚
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(statusCode=RET.DATAERR, msg="修改失败")
            db.session.close()
            return jsonify(statusCode=RET.OK, msg="修改成功")

        # 产品提交结果
        elif role == 2:
            try:
                case_list = db.session.query(db_mysql.TestCase).filter(db_mysql.TestCase.id == id).update(
                    {
                        "product_result": product_result,
                        "product_name": product_name
                    })
                db.session.commit()
            except IntegrityError as e:
                # 数据库操作错误后的回滚
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(statusCode=RET.DATAERR, msg="修改失败")
            db.session.close()
            return jsonify(statusCode=RET.OK, msg="修改成功")


class Report(Resource):
    decorators = [authtoken.login_required]

    # 新增
    def post(self):
        # 获取请求的json数据, 从列表中取字典的值
        req_dic = request.get_json()
        case_id = req_dic.get("case_id")  # 用例id
        uid = req_dic.get("uid")   # 用户id
        role = req_dic.get("role")  # 用户角色
        test_result = req_dic.get("test_result")  # 0:提交测试，1:测试通过，2:测试不通过
        tree_id = req_dic.get("tree_id")    # 父id为0的项目id
        operation_content = req_dic.get("operation_content")    # 操作内容

        # 开发身份
        if role == 0:
            # DingTalk("流程提醒：提交测试")
            return jsonify(statusCode=RET.OK, msg="提交成功")

        # 测试身份
        elif role == 1:
            if test_result == 1:
                # DingTalk("流程提醒：测试通过")
                try:
                    # 查询用例的所有条数
                    case_all = db.session.query(func.count(db_mysql.TestCase.test_result.is_(None))). \
                        filter(db_mysql.TestCase.case_id == case_id).scalar()
                    # 查询用例pass的条数
                    case_pass = db.session.query(func.count(db_mysql.TestCase.test_result.is_(None))).\
                        filter(db_mysql.TestCase.case_id == case_id, db_mysql.TestCase.test_result == 0).scalar()
                    # 查询用例fail的条数
                    case_fail = db.session.query(func.count(db_mysql.TestCase.test_result.is_(None))).\
                        filter(db_mysql.TestCase.case_id == case_id, db_mysql.TestCase.test_result == 1).scalar()
                    # 查询用例block的条数
                    case_block = db.session.query(func.count(db_mysql.TestCase.test_result.is_(None))).\
                        filter(db_mysql.TestCase.case_id == case_id, db_mysql.TestCase.test_result == 2).scalar()
                    # 查询用例执行为空的条数
                    case_none = db.session.query(func.count(db_mysql.TestCase.test_result.is_(None))).\
                        filter(db_mysql.TestCase.case_id == case_id, db_mysql.TestCase.test_result.is_(None)).scalar()
                    # 根据case_id查询出对应轮次数据
                    report_val = db.session.query(db_mysql.TestReport).filter(db_mysql.TestReport.case_id == case_id)

                    db.session.commit()

                except IntegrityError as e:

                    # 数据库操作错误后的回滚
                    db.session.rollback()
                    current_app.logger.error(e)
                    return jsonify(statusCode=RET.DATAERR, msg="查询失败")
                db.session.close()

                # 取出case_id对应的轮次数，存入report_list
                report_list = []
                for val in report_val:
                    report_list.append(val.test_rounds)
                # 如果report_list为空，count默认为1，否则取列表里最后一位数+1
                if len(report_list) == 0:
                    count = 1
                else:
                    count = report_list[-1] + 1

                # return case_all, case_pass, case_fail, case_block, case_none
                # 将用例对应的统计数据插入数据库
                try:
                    db.session.add(
                        db_mysql.TestReport(case_id=case_id, test_rounds=count, case_number=case_all,
                                            case_pass=case_pass, case_fail=case_fail, case_block=case_block,
                                            no_test=case_none, uid=uid, test_result=test_result))
                    db.session.commit()

                except IntegrityError as e:
                    # 数据库操作错误后的回滚
                    db.session.rollback()
                    current_app.logger.error(e)

                    # 增加用户操作日志
                    operation_content = "测试通过:%s" % operation_content

                    except_log().putlog(tree_id, uid, operation_content, 2, 3)

                    return jsonify(statusCode=RET.DATAERR, msg="数据创建失败")
                db.session.close()

                # 增加用户操作日志
                operation_content = "测试通过:%s" % operation_content

                except_log().putlog(tree_id, uid, operation_content, 1, 3)

                return jsonify(statusCode=RET.OK, msg="创建成功")

            elif test_result == 2:
                # DingTalk("流程提醒：测试不通过")
                try:
                    # 查询用例的所有条数
                    case_all = db.session.query(func.count(db_mysql.TestCase.test_result.is_(None))). \
                        filter(db_mysql.TestCase.case_id == case_id).scalar()
                    # 查询用例pass的条数
                    case_pass = db.session.query(func.count(db_mysql.TestCase.test_result.is_(None))). \
                        filter(db_mysql.TestCase.case_id == case_id, db_mysql.TestCase.test_result == 0).scalar()
                    # 查询用例fail的条数
                    case_fail = db.session.query(func.count(db_mysql.TestCase.test_result.is_(None))). \
                        filter(db_mysql.TestCase.case_id == case_id, db_mysql.TestCase.test_result == 1).scalar()
                    # 查询用例block的条数
                    case_block = db.session.query(func.count(db_mysql.TestCase.test_result.is_(None))). \
                        filter(db_mysql.TestCase.case_id == case_id, db_mysql.TestCase.test_result == 2).scalar()
                    # 查询用例执行为空的条数
                    case_none = db.session.query(func.count(db_mysql.TestCase.test_result.is_(None))). \
                        filter(db_mysql.TestCase.case_id == case_id, db_mysql.TestCase.test_result.is_(None)).scalar()
                    # 根据case_id查询出对应轮次数据
                    report_val = db.session.query(db_mysql.TestReport).filter(db_mysql.TestReport.case_id == case_id)

                    db.session.commit()

                except IntegrityError as e:

                    # 数据库操作错误后的回滚
                    db.session.rollback()
                    current_app.logger.error(e)
                    return jsonify(statusCode=RET.DATAERR, msg="查询失败")
                db.session.close()

                # 取出case_id对应的轮次数，存入report_list
                report_list = []
                for val in report_val:
                    report_list.append(val.test_rounds)
                # 如果report_list为空，count默认为1，否则取列表里最后一位数+1
                if len(report_list) == 0:
                    count = 1
                else:
                    count = report_list[-1] + 1

                # return case_all, case_pass, case_fail, case_block, case_none
                # 将用例对应的统计数据插入数据库
                try:
                    db.session.add(
                        db_mysql.TestReport(case_id=case_id, test_rounds=count, case_number=case_all,
                                            case_pass=case_pass, case_fail=case_fail, case_block=case_block,
                                            no_test=case_none, uid=uid, test_result=test_result))
                    db.session.commit()

                except IntegrityError as e:
                    # 数据库操作错误后的回滚
                    db.session.rollback()
                    current_app.logger.error(e)

                    # 增加用户操作日志
                    operation_content = "测试不通过:%s" % operation_content

                    except_log().putlog(tree_id, uid, operation_content, 2, 3)

                    return jsonify(statusCode=RET.DATAERR, msg="数据创建失败")
                db.session.close()

                # 增加用户操作日志
                operation_content = "测试不通过:%s" % operation_content

                except_log().putlog(tree_id, uid, operation_content, 1, 3)

                return jsonify(statusCode=RET.OK, msg="创建成功")

        # 产品身份
        elif role == 2:
            if test_result == 1:
                # DingTalk("流程提醒：产品验收通过")
                return jsonify(statusCode=RET.OK, msg="提交成功")
            elif test_result == 2:
                # DingTalk("流程提醒：产品验收不通过")
                return jsonify(statusCode=RET.OK, msg="提交成功")


class QueryReport(Resource):
    decorators = [authtoken.login_required]

    # 查询
    def post(self):

        # 获取请求的json数据，返回字典
        req_dict = request.get_json()
        case_id = req_dict.get("case_id")  # 用例id

        check_list = []

        try:
            report_list = db.session.query(db_mysql.TestReport).\
                filter(db_mysql.TestReport.case_id == case_id).order_by("test_rounds")
            db.session.commit()
        except IntegrityError as e:

            # 数据库操作错误后的回滚
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(statusCode=RET.DATAERR, msg="查询失败")
        db.session.close()

        for raw in report_list:
            user_list = db.session.query(db_mysql.User).filter(db_mysql.User.id == raw.uid)
            for val in user_list:
                check_dic = {}
                check_dic["id"] = raw.id
                check_dic["test_rounds"] = raw.test_rounds
                check_dic["case_number"] = raw.case_number
                check_dic["case_pass"] = raw.case_pass
                check_dic["case_fail"] = raw.case_fail
                check_dic["case_block"] = raw.case_block
                check_dic["no_test"] = raw.no_test
                check_dic["username"] = val.username
                check_dic["set_time"] = str(raw.set_time)
                check_dic["test_result"] = raw.test_result

                check_list.append(check_dic)

        return jsonify(data=check_list, statusCode=RET.OK, msg="查询成功")


class UploadCase(Resource):
    decorators = [authtoken.login_required]

    # 新增
    def post(self):
        # 获取请求的json数据, 从列表中取字典的值
        case_dic = request.form.to_dict()
        case_id = case_dic.get("case_id")   # 用例id
        file = request.files.get('filename')
        filename = (file.filename).strip('"')

        t = str(time.time()).split('.')

        # 验证case_id是否为空
        if case_id is None:
            return jsonify(statusCode=RET.PARAMERR, msg="缺少case_id")
        elif case_id == "":
            return jsonify(statusCode=RET.PARAMERR, msg="缺少case_id")

        # 验证file是否为空
        if file is None:
            return jsonify(statusCode=RET.PARAMERR, msg="请选择上传文件")
        elif file == "":
            return jsonify(statusCode=RET.PARAMERR, msg="请选择上传文件")

        def allowed_file(filename):
            # 校验文件后缀
            return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

        if file and allowed_file(filename):
            # 取出文件名转换成拼音
            name = filename.split('.')[0]
            ext = filename.split('.')[1]
            new_filename = ''.join(lazy_pinyin(name)) + t[0] + '.' + ext
            # 储存文件
            base_path = '/mnt/uploads/test_environment/case'
            file.save(os.path.join(base_path, secure_filename(new_filename)))
            case = base_path + '/' + new_filename
            # print(case)

            # 打开Excel，选择存有数据的工作表
            testcase = xlrd.open_workbook(case)
            sheet = testcase.sheet_by_name('Sheet1')
            nrows = sheet.nrows
            ncols = sheet.ncols

            colspan = {}
            # 统计出合并单元格有哪些
            if sheet.merged_cells:
                for item in sheet.merged_cells:
                    for row in range(item[0], item[1]):
                        for col in range(item[2], item[3]):
                            # 合并单元格的首格是有值的，所以在这里进行了去重
                            if (row, col) != (item[0], item[2]):
                                colspan.update({(row, col): (item[0], item[2])})
            # 读取每行数据
            for i in range(1, nrows):
                row = []
                for j in range(ncols):
                    # 假如碰见合并的单元格坐标，取合并的首格的值即可
                    if colspan.get((i, j)):
                        row.append(sheet.cell_value(*colspan.get((i, j))))
                    else:
                        row.append(sheet.cell_value(i, j))

            # for r in range(1, sheet.nrows):
                # module_name = sheet.cell(r, 0).value
                # test_item = sheet.cell(r, 1).value
                # precondition = sheet.cell(r, 2).value
                # test_process = sheet.cell(r, 3).value
                # expected_result = sheet.cell(r, 4).value
                # test_note = sheet.cell(r, 5).value

                try:
                    db.session.add(
                        db_mysql.TestCase(module_name=row[0], test_item=row[1], expected_result=row[2],
                                          test_note=row[3], case_id=case_id))
                    db.session.commit()

                except IntegrityError as e:
                    # 数据库操作错误后的回滚
                    db.session.rollback()
                    current_app.logger.error(e)
                    return jsonify(statusCode=RET.DATAERR, msg="数据创建失败")
                db.session.close()

            return jsonify(statusCode=RET.OK, msg="上传成功")

        else:
            return jsonify(statusCode=RET.DATAERR, msg="文件格式不对")


class QueryResult(Resource):
    decorators = [authtoken.login_required]

    # 查询各执行结果
    def post(self):

        # 获取请求的json数据，返回字典
        req_dict = request.get_json()
        case_id = req_dict.get("case_id")   # 用例id
        develop_res = req_dict.get("develop_res")  # 开发执行结果：0为pass，1为fail，2为block
        test_res = req_dict.get("test_res")   # 测试执行结果：0为pass，1为fail，2为block
        product_res = req_dict.get("product_res")   # 产品执行结果：0为pass，1为fail，2为block

        check_list = []

        if len(str(develop_res)) == 1:
            try:
                case_list = db.session.query(db_mysql.TestCase).filter(db_mysql.TestCase.case_id == case_id)\
                    .filter(db_mysql.TestCase.develop_result == develop_res)
                db.session.commit()
            except IntegrityError as e:

                # 数据库操作错误后的回滚
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(statusCode=RET.DATAERR, msg="查询失败")
            db.session.close()

            for raw in case_list:
                check_dic = {}
                check_dic["id"] = raw.id
                check_dic["case_id"] = raw.case_id
                check_dic["module_name"] = raw.module_name
                check_dic["test_item"] = raw.test_item
                check_dic["precondition"] = raw.precondition
                check_dic["test_process"] = raw.test_process
                check_dic["expected_result"] = raw.expected_result
                check_dic["test_note"] = raw.test_note
                check_dic["develop_result"] = raw.develop_result
                check_dic["test_result"] = raw.test_result
                check_dic["product_result"] = raw.product_result

                check_list.append(check_dic)

            if len(check_list) == 0:
                return jsonify(statusCode=RET.DATAERR, msg="暂无测试用例")
            else:
                return jsonify(data=check_list, statusCode=RET.OK, msg="查询成功")
        elif len(str(test_res)) == 1:
            try:
                case_list = db.session.query(db_mysql.TestCase).filter(db_mysql.TestCase.case_id == case_id)\
                    .filter(db_mysql.TestCase.test_result == test_res)
                db.session.commit()
            except IntegrityError as e:

                # 数据库操作错误后的回滚
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(statusCode=RET.DATAERR, msg="查询失败")
            db.session.close()

            for raw in case_list:
                check_dic = {}
                check_dic["id"] = raw.id
                check_dic["case_id"] = raw.case_id
                check_dic["module_name"] = raw.module_name
                check_dic["test_item"] = raw.test_item
                check_dic["precondition"] = raw.precondition
                check_dic["test_process"] = raw.test_process
                check_dic["expected_result"] = raw.expected_result
                check_dic["test_note"] = raw.test_note
                check_dic["develop_result"] = raw.develop_result
                check_dic["test_result"] = raw.test_result
                check_dic["product_result"] = raw.product_result

                check_list.append(check_dic)

            if len(check_list) == 0:
                return jsonify(statusCode=RET.DATAERR, msg="暂无测试用例")
            else:
                return jsonify(data=check_list, statusCode=RET.OK, msg="查询成功")
        elif len(str(product_res)) == 1:
            try:
                case_list = db.session.query(db_mysql.TestCase).filter(db_mysql.TestCase.case_id == case_id)\
                    .filter(db_mysql.TestCase.product_result == product_res)
                db.session.commit()
            except IntegrityError as e:

                # 数据库操作错误后的回滚
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(statusCode=RET.DATAERR, msg="查询失败")
            db.session.close()

            for raw in case_list:
                check_dic = {}
                check_dic["id"] = raw.id
                check_dic["case_id"] = raw.case_id
                check_dic["module_name"] = raw.module_name
                check_dic["test_item"] = raw.test_item
                check_dic["precondition"] = raw.precondition
                check_dic["test_process"] = raw.test_process
                check_dic["expected_result"] = raw.expected_result
                check_dic["test_note"] = raw.test_note
                check_dic["develop_result"] = raw.develop_result
                check_dic["test_result"] = raw.test_result
                check_dic["product_result"] = raw.product_result

                check_list.append(check_dic)

            if len(check_list) == 0:
                return jsonify(statusCode=RET.DATAERR, msg="暂无测试用例")
            else:
                return jsonify(data=check_list, statusCode=RET.OK, msg="查询成功")


# 新增修改删除用例接口
api.add_resource(Case, '/case')
# 查询测试用例内容接口
api.add_resource(QueryCase, '/querycase')
# 修改开发或测试的执行结果接口
api.add_resource(CheckResult, '/result')
# 生成测试报告统计数据接口
api.add_resource(Report, '/report')
# 查询测试报告统计接口
api.add_resource(QueryReport, '/queryreport')
# 上传Excel文档接口
api.add_resource(UploadCase, '/upload')
# 按执行结果查询接口
api.add_resource(QueryResult, '/queryresult')