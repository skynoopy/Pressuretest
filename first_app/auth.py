import functools
from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash,generate_password_hash
from .db_mysql import User
from first_app.exts import db


rz = Blueprint('auth',__name__,url_prefix='/auth')

@rz.route('/')
def auth():
    return '我是认证模块o!'
    # with app.app_context():
    #  db.init_app(app)
    # uu1 = User.query.all()
    #         k1 = 'k1'
    #         uu2 = User.query.filter_by(username=k1).first()
    #         uu3 = User.query.first()

            # return (uu2.username)
    # for u in uu1:
    #     kk = u.username
    #     return ("注册首页: {user}" .format(user=kk))



#注册
@rz.route('/register', methods=['GET','POST'])
def register():
     if request.method == 'POST':
         username = request.form['username']
         password = request.form['password']
         error = None
         print(username,password)
         # k1 = 'k1'
         # uu2 = User.query.filter_by(username=k1).first()
         # print(uu2.username)

         if not username:   #判断是否为空，是否已经注册
             error = 'Username is required'
         elif not password:
             error = 'Password is required'

         elif User.query.filter_by(username=username).first() is not None:
              error = 'user {} is already registered.'.format(username)

         if error is None:  #验证成功 插入数据库新用户信息, 不直接存密码生成密码哈希存入

             user = User(username=username, password=generate_password_hash(password))
             db.session.add(user)
             db.session.commit()


             return redirect(url_for('auth.login')) #跳转至登录页面
         flash(error)
     return render_template('auth/register.html') #注册页面，验证失败也会返回


@rz.route('/login', methods=('GET','POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        # print(username,password)

        #查询注册用户存入变量备用
        user = User.query.filter_by(username=username).first()
        # print(user.username,user.password)
        # user = db.execute(
        #     'select * from user where usernam = ?',(username,).fetchone()
        # )
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user.password,password): #比对哈希密码值
            error = 'Incorrect password.'

        if error is None:
           session.clear()
           session['username'] = request.form['username']
           session['user_id'] = user.id  #存入用户id
           session.permanent = True
           print(session.get('username'),session.get('user_id'))


           # from app.forms import ScriptForm
           # form = ScriptForm()
           # hostip = form.hostip.data
           # return render_template('home_page/index.html')

           return redirect(url_for('home_page.index'))  #可直接跳转到home_page下的index函数下


           # return redirect(url_for('auth.index'))
           # return ('登录成功')
        flash(error)
    return  render_template('auth/login.html')

@rz.before_app_request #视图函数运行之前函数，会提前检查用户id是否已经在session 不再则从数据库获取数据存入g.user中
def load_logged_in_user():
     user_id = session.get('user_id')
     if user_id is None:
         g.user = None
     else:

         user = User.query.filter_by(username=user_id).first()
         g.user = user

         # user = User.query.filter_by(User.id == user_id).all
         # user = User.query.get(id=user_id)
         print(user)

         # g.user = get_db().execute(
         #     'select * from user where id = ?',(user_id,)
         # ).fetchon()


#注销 把用户id从session移除
@rz.route('/logout')
def logout():
    session.clear()
    session.pop('username')
    return render_template('auth/logout.html')

@rz.route('/dist')
def dist():
    return render_template('dist/index.html')

#用户登录后才能创建编辑删除帖子
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view()



