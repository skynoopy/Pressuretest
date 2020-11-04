import os
from flask import Flask,render_template
from app import auth, forms, Home_page, blog
import configs
from app.exts import db
from flask_bootstrap import Bootstrap
from app.forms import LoginForm
from app.auth import login_required
from app.Restful import RestfulApi, User_permissions_api, AuthorityApi, Tree_api,AuxiliaryFunction,Upload_file
from flask_cors import CORS


bootstrap = Bootstrap()

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)

    bootstrap.init_app(app)
    app.config.from_object(configs)

    #restful显示中文
    app.config.update(RESTFUL_JSON=dict(ensure_ascii=False))
    app.config['JSON_AS_ASCII'] = False



    with app.app_context():
         db.init_app(app) #初始化db
         # auth.init_app(app) #初始化httpauth
         # user1 = User(username='k1', password='k1@123')
         # user2 = User(username='k2', password='123456')
         # db.session.add_all([user1,user2])
         # db.session.commit()
         # db.drop_all()
         # db.create_all()

    # app.app_context().push()
    # with app.app_context():
    #      db.init_app(app)
    #      db.create_all()


    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'Flask-QA.sqlite'),
    )


    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    # # a simple page that says hello

    @app.route('/')
    def index():

        return render_template('dist/index.html')

    app.register_blueprint(auth.rz)
    app.register_blueprint(forms.wtf)
    app.register_blueprint(Home_page.home_page)
    app.register_blueprint(blog.blog)
    app.register_blueprint(RestfulApi.RestfulApi)
    app.register_blueprint(User_permissions_api.user_permissions)
    app.register_blueprint(AuthorityApi.AuthorityApi)
    app.register_blueprint(AuxiliaryFunction.AuxiliaryFunction)
    app.register_blueprint(Tree_api.OperationTree)
    app.register_blueprint(Upload_file.RestfulFile)
    app.app_context().push()
    # app.add_url_rule('/', endpoint='dist')
    return app


# if __name__ == '__main__':
#     create_app().run(processes=4)