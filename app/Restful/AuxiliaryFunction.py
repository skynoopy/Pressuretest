import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from flask_restful import Resource, Api
from flask import Blueprint,request,jsonify, current_app
from .Httpauth import authtoken #Interface_authority初始化验证接口权限函数
from app.api_status.response_code import RET


AuxiliaryFunction = Blueprint('AuxiliaryFunction',__name__,url_prefix='/AuxiliaryFunction')
api = Api(AuxiliaryFunction)

# 压测结果邮件发送
class ResultEmail(Resource):
    decorators = [authtoken.login_required]
    # method_decorators = [Interface_authority]
    def post(self):
        # 获取请求的json数据，返回字典
        req_dict = request.get_json()
        useremail = req_dict.get("useremail")  # 用户邮箱
        datamsg = req_dict.get("datamsg")  # 发送内容

        # 判断用户邮箱是否传值或者为空
        if useremail is None:
            return jsonify(statusCode=RET.PARAMERR, msg="用户邮箱为必填项")
        elif useremail == "":
            return jsonify(statusCode=RET.PARAMERR, msg="用户邮箱不能为空")

        # 判断发送内容是否传值或者为空
        if datamsg is None:
            return jsonify(statusCode=RET.PARAMERR, msg="发送内容为必填项")
        elif datamsg == "":
            return jsonify(statusCode=RET.PARAMERR, msg="发送内容不能为空")

        my_sender = 'automation@wenba100.com'  # 发件人邮箱账号
        my_pass = 'Monitor!123456'  # 发件人邮箱密码
        # my_user = 'ou.wang@wenba100.com'  # 收件人邮箱账号，我这边发送给自己
        ret = True
        try:
            msgtext = ("压测报告：\n\n%s"%(datamsg))
            msg = MIMEText(msgtext, 'plain', 'utf-8')
            msg['From'] = formataddr(["QA系统",my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['To'] = formataddr(["%s"%useremail,useremail])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['Subject'] = "压测报告"  # 邮件的主题，也可以说是标题

            server = smtplib.SMTP_SSL("smtp.exmail.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是25
            server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
            server.sendmail(my_sender, [useremail, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.quit()  # 关闭连接
            print("发送成功")
        except Exception:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
            print("发送失败")
        return jsonify(statusCode=RET.OK, msg="发送成功")

api.add_resource(ResultEmail,'/ResultEmail')