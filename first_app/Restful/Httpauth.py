from werkzeug.security import check_password_hash  #验证密码hash
from flask import (g, jsonify, make_response,request)
from first_app.db_mysql import User
from flask_httpauth import HTTPBasicAuth,HTTPTokenAuth
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from configs import SECRET_KEY
from functools import wraps
import requests,json

#密码验证url登录
auth = HTTPBasicAuth() #认证初始化
@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username = username).first()
    print(user)
    if user and check_password_hash(user.password, password):
        g.user = user
        return True
    return False

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

#token认证
authtoken = HTTPTokenAuth(scheme='bsk')
serializer = Serializer(SECRET_KEY,expires_in=60000)

# 回调函数，对 token 进行验证
@authtoken.verify_token
def verify_token(token):
    g.user = None
    try:
        data = serializer.loads(token)
        print(data)
    except:
        return False

    if 'username' in data:
        g.user = data['username']
        print(g.user)
        return True
    return False



#接口验证权限装饰器
def Interface_authority(func):
      url = 'http://127.0.0.1:5000/UserPerm/userfunc'
      data = request.get_json().get('Permission_parameters') #获取传入权限参数

      request_method = request.method.lower()
      # ktree = request.path.split('/')[2]     #获取请求url路径
      ktree = 'groupfunc'

      if data is None:
          j_data = {
              "msg":'参数错误',
              "statusCode": 406
          }
          return jsonify(j_data)
      elif data == "":
          j_data = {
              "msg":'参数不能为空',
              "statusCode": 406
          }
          return jsonify(j_data)


      print(ktree)
      @wraps(func)
      def notadmin_wrapper():
          req = requests.post(url, json=data)  #请求权限接口获取对应接口列表
          req_result = req.json()
          print(req_result)


          if req_result == None:
              j_data = {
                  'msg': '无任何权限',
                  'statusCode': 403
              }
              return jsonify(j_data)

          elif req_result == 'admin':
              return func()

          else:
              for k in req_result:
                  if ktree in k.keys() and request_method in k.values():  #判断请求path和类型是否在权限返回列表中,两者都满足才会允许访问
                      return func()
              else:
                  j_data = {
                      'msg': '无权操作',
                      'code': 200
                  }
                  return jsonify(j_data)

      return notadmin_wrapper

