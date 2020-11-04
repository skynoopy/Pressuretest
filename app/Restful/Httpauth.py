from werkzeug.security import check_password_hash  #验证密码hash
from flask import (g, jsonify, make_response,request,session)
from app.db_mysql import User
from flask_httpauth import HTTPBasicAuth,HTTPTokenAuth
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from configs import SECRET_KEY
from functools import wraps
import requests,json,os,time

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
authtoken = HTTPTokenAuth(scheme='xbj')

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
      try:

          url = 'http://127.0.0.1:5000/UserPerm/userfunc'
          data = request.get_json(force=True) #获取传入权限参数
          data = data.get('Permission_parameters')
          request_method = request.method.lower()
          ktree = request.path.split('/')[2]     #获取请求url路径
          print(data)

          @wraps(func)
          def wrapper():
              req = requests.post(url, json=data)  #请求权限接口获取对应接口列表
              req_result = req.json()
              print(req_result)

              if req_result == None:       #判断权限是否为空
                  j_data = {
                      'msg': '无任何权限',
                      'statusCode': 403
                  }
                  return jsonify(j_data)

              elif req_result == 'admin':  #判断是否为admin
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
          return wrapper
      except Exception as e:
          print(e)