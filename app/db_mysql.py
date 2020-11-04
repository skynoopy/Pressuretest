from app.exts import db
from datetime import datetime




class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.Text)
    role = db.Column(db.Integer, nullable=False)
    # ip_type = db.Column(db.String(50), nullable=False)
    posts = db.relationship('Post', backref='users')
    trees = db.relationship('Tree', backref='users')

    def __repr__(self):
        return 'User:%s' % self.username










class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    title = db.Column(db.String(50),index=True, nullable=False)
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


    # def __repr__(self):
    #     return 'group_id:{group_id} uid:{uid}'.format(group_id=self.group_id, uid=self.uid)


class GroupFunc(db.Model):
    __tablename__ = 'group_func'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, nullable=False)
    tree_id = db.Column(db.Integer, nullable=False)
    func_id = db.Column(db.String(255), nullable=True)
    project_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return 'group_id:%s tree_id:%s func_id:%s project_id:%s' % \
               self.group_id, self.tree_id, self.func_id, self.project_id


class UserFunc(db.Model):
    __tablename__ = 'user_func'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.Integer, nullable=False)
    tree_id = db.Column(db.Integer, nullable=False)
    func_id = db.Column(db.String(255), nullable=True)
    project_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return 'uid:%s tree_id:%s func_id:%s project_id:%s' % \
               self.uid, self.tree_id, self.func_id, self.project_id


class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_name = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return 'id:%s project:%s' % self.id, self.project_name


class TestCase(db.Model):
    __tablename__ = 'test_case'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    case_id = db.Column(db.Integer, nullable=False)
    module_name = db.Column(db.String(255), nullable=True)
    test_item = db.Column(db.String(6000), nullable=True)
    precondition = db.Column(db.String(6000), nullable=True)
    test_process = db.Column(db.Text(60000), nullable=True)
    expected_result = db.Column(db.Text(60000), nullable=True)
    test_note = db.Column(db.Text(60000), nullable=True)
    develop_result = db.Column(db.Integer, nullable=True)
    test_result = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return 'id:%s case_id:%s module_name:%s' % self.id, self.case_id, self.module_name


#
#
class ReportLog(db.Model):
    __tablename__ = 'report_log'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tree_id = db.Column(db.Integer, nullable=False)
    tree_name = db.Column(db.String(255), nullable=False)
    report_name = db.Column(db.String(255), nullable=False)
    report_info = db.Column(db.String(50000), nullable=False)
    uid = db.Column(db.Integer, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
