from app.exts import db


# db = SQLAlchemy()
# app = Flask(__name__)
# app.app_context().push()
#
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:bsk123@127.0.0.1:3306/Flask_demo'
#
# app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# app.config['SQLALCHEMY_ECHO'] = True



# class Role(db.Model):
#     __tablename__ = 'roles'
#     id = db.Column(db.Integer, primary_key=True,autoincrement=True)
#     name = db.Column(db.String(64),unique=True)
#     user = db.relationship('User',backref='role')
#
#     def __repr__(self):
#         return '<Role %r>' % self.name




class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.Text)
    # posts = db.Column(db.Integer, db.ForeignKey('roles.id'))

    posts = db.relationship('Post',backref='users')
    trees = db.relationship('Tree',backref='users')

    def __repr__(self):
        return 'User:%s' % self.username



class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    title = db.Column(db.String(50),index=True,nullable=False)
    body = db.Column(db.Text, nullable=False)

    users_id = db.Column(db.Integer,db.ForeignKey('users.id'))

    def __repr__(self):
        return 'title:%s post:%s' % self.title, self.body


class Tree(db.Model):
    __tablename__ = 'tree'  # 定义该表在mysql数据库中的实际名称
    # 定义表的内容
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(50), nullable=False)
    pid = db.Column(db.Integer, nullable=False)
    file_type = db.Column(db.Integer, nullable=False)
    uid = db.Column(db.Integer, nullable=False)
    meth = db.Column(db.String(10), nullable=False)
    sc_ip = db.Column(db.String(50), nullable=False)
    sc_path = db.Column(db.String(50), nullable=False)
    sc_praameter = db.Column(db.String(1000), nullable=False)
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return 'filename:%s  file_type:%s' % self.filename, self.file_type



#
# role1 = Role(name='admin')
# role2 = Role(name='general')

# user1 = User(username='k1',password='k1@123')
# user2 = User(username='k2',password='123456')




# with app.app_context():

     # db.init_app(app)
     # db.session.delete(user1)
     # db.drop_all()
     # db.create_all()
     # db.session.add(user2)
     # uu1.username = 'bsk'
     # db.session.add_all([user1,user2])
     # db.session.commit()
     # user4 = User(username='k5',password='k5123')
     # db.session.add(user4)
     # db.session.commit()
     # uu1 = User.query.all()
     # for u in uu1:
     #     print(u.username)
     #


     # k is not None
     # kk = User.query.get(1)

















