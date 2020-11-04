from app.exts import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.Text)
    ip_type = db.Column(db.String(50), nullable=False)

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
    sc_name = db.Column(db.String(50), nullable=False)
    concurrency = db.Column(db.String(50), nullable=False)
    strategy = db.Column(db.String(50), nullable=False)
    con_praameter = db.Column(db.String(255), nullable=False)
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return 'filename:%s  file_type:%s' % self.filename, self.file_type


class Function(db.Model):
    __tablename__ = 'function'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    func_name = db.Column(db.String(50), nullable=False)
    port_name = db.Column(db.String(255), nullable=False)
    request_type = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return 'func_id:%s func_name:%s port_name:%s request_type:%s' % self.id, self.func_name, self.port_name, self.request_type


class Group(db.Model):
    __tablename__ = 'group'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_name = db.Column(db.String(50), nullable=False)
    project_id = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return 'group_name:%s' % self.group_name


class Envip(db.Model):
    __tablename__ = 'envip'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ip_name = db.Column(db.String(255), nullable=False)
    ip_type = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return 'ip_name:%s ip_type:%s' % self.ip_name, self.ip_type


class GroupUser(db.Model):
    __tablename__ = 'group_user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, nullable=False)
    uid = db.Column(db.Integer, nullable=False)


    def __repr__(self):
        return 'group_id:%s uid:%s' % self.group_id, self.uid


class GroupFunc(db.Model):
    __tablename__ = 'group_func'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, nullable=False)
    tree_id = db.Column(db.Integer, nullable=False)
    func_id = db.Column(db.String, nullable=True)

    def __repr__(self):
        return 'group_id:%s tree_id:%s func_id:%s' % self.group_id, self.tree_id, self.func_id


class UserFunc(db.Model):
    __tablename__ = 'user_func'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.Integer, nullable=False)
    tree_id = db.Column(db.Integer, nullable=False)
    func_id = db.Column(db.String, nullable=True)

    def __repr__(self):
        return 'uid:%s tree_id:%s func_id:%s' % self.uid, self.tree_id, self.func_id


class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_name = db.Column(db.String, nullable=False)

    def __repr__(self):
        return 'id:%s project:%s' % self.id, self.project_name

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
