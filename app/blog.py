from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, session
)

from .db_mysql import Post
from app.exts import db
from functools import wraps
blog = Blueprint('blog',__name__,url_prefix='/blog')





#共用函数，获取post

# def get_post(id, check_users=True):
#     # post = get_db().execute(
#     #     'SELECT p.id, title, body, created, author_id, username'
#     #     ' FROM post p JOIN user u ON p.author_id = u.id'
#     #     ' WHERE p.id = ?',
#     #     (id,)
#     # ).fetchone()
#
#     post = Post.query.filter_by(id='{id}'.format(id=id)).first()
#     print(post.title,post.body,post.id,post.users_id)
#
#     if post is None:
#         abort(404, "Post id {0} doesn't exist.".format(id))
#
#     if check_users and post['users_id'] != g.user['id']:
#         abort(403)
#
#     return post



def kk(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        print (request.method)         # 获取请求参数
        # print('test01')
        return f(*args, **kwargs)
    return wrapper







#博客首页

@blog.route('/')
@kk
def index():
    posts = Post.query.all()
    userid = session.get('user_id')

    return render_template('blog/index.html', posts=posts,userid=userid)


#创建博客
@blog.route('/create',methods=('GET','POST'))


def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = '请输入标题!'
        if error is not None:
            flash(error)

        else:
            id = session.get('user_id')
            print(id)
            ins = Post(title=title,body=body,users_id='{id}'.format(id=id))
            db.session.add(ins)
            db.session.commit()
            return redirect(url_for('blog.index'))
    return  render_template('blog/create.html')

#更新博客
@blog.route('/<int:id>/update',methods = ('GET', 'POST'))
# @login_required
def update(id):
      post = Post.query.filter_by(id='{id}'.format(id=id)).first()
      print(post.title, post.body, post.id, post.users_id)

      if request.method == 'POST':
         title = request.form['title']
         body = request.form['body']
         error = None

         if not title:
             error = 'Title is required.'

         if error is not None:
             flash(error)

         else:
            # upt = post.query.filter(Post.id == id ).update({"title":title,"body":body})
            post.title = title
            post.body  = body
            db.session.commit()
            return redirect(url_for('blog.index'))
            flash('更改成功','info')

      return render_template('blog/update.html',post=post)



@blog.route('/<int:id>/delete', methods=('POST',))
# @login_required
def delete(id):
    Post.query.filter_by(id='{id}'.format(id=id)).delete()
    db.session.commit()
    return redirect(url_for('blog.index'))

#用户登录后才能创建编辑删除帖子

# def login_required(view):
#     @functools.wraps(view)
#     def wrapped_view(**kwargs):
#         if g.user is None:
#             return redirect(url_for('auth.login'))
#         return view(**kwargs)
#     return wrapped_view()