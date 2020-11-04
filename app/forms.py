
from flask_wtf import  FlaskForm
from wtforms import (StringField ,SubmitField,PasswordField,validators,BooleanField, FileField, FloatField, IntegerField
                     ,SelectField, SelectMultipleField, DateField,RadioField,SelectField,TextAreaField)
from wtforms.validators import DataRequired, Length, Email

from flask import  Blueprint,render_template,request,redirect,url_for,flash
from werkzeug.security import check_password_hash,generate_password_hash
from app.db_mysql import  db,User


#登录表单
class LoginForm(FlaskForm):
          username = StringField(u'用户名',validators=[DataRequired(message=u'用户名不能为空'),Length(1,24)])
          password = PasswordField(u'密码',validators=[DataRequired(message=u'密码不能为空'),Length(6,24)])
          remember = BooleanField('remember me')
          submit = SubmitField(u'登录')



#注册表单
class RegistrationForm(FlaskForm):
      username = StringField(u'用户名', [validators.Length(min=4, max=25),DataRequired(message=u'用户名不能为空')])
      password = PasswordField(u'登录密码', [validators.DataRequired(message=u'密码不能为空'), validators.EqualTo('confirm', message='Passwords must match')])
      confirm = PasswordField('确认密码')
      accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])
      submit = SubmitField(u'登录')




#首页脚本生成表单
class  ScriptForm(FlaskForm):
       hostip = StringField(u'被压测主机ip:',  validators = [DataRequired(message='ip不可为空')])
       hostpath = StringField(u'压测路径:', validators = [DataRequired(message='路径不可为空')])
       parameter = StringField(u'自定义参数:', validators = [DataRequired(message='参数不可为空')])
       submit = SubmitField(u'生成脚本')

#首页执行脚本表单
class ExecuteScriptForm(FlaskForm):
    Filename = StringField(u'要执行的脚本名称',validators=[DataRequired(message='脚本名称不可为空')])
    Concurrent = IntegerField(u'并发数', validators=[DataRequired(message='并发数不可为空')])
    Dx = SelectField(u'下拉',choices=[("-t",'执行时间'),("-l",'循环数')], validators=[DataRequired()])
    Xz = StringField(u'参数',validators=[DataRequired(message='参数不可为空')])
    Ip = StringField(u'IP或域名', validators=[DataRequired(message='ip或域名不可为空')])
    submit2 = SubmitField(u'脚本执行')


    # Cycle= IntegerField(u'循环数', validators=[DataRequired(message='循环数不可为空')])
    # ExecuteTime = IntegerField(u'执行时间', validators=[DataRequired(message='执行时间不可为空')])
    # t1 = RadioField(u'单选框', choices=[('m','male'),('f','kk')],validators=[DataRequired()])
    # t2 = SelectField(u'下拉',choices=[('teacher','T'),('doctor','D'),('engin','E')],validators=[DataRequired()])
    # t3 = FileField(u'文件上传',validators=[DataRequired()])
    # t4 = SelectMultipleField('Hobby',choices=[('swin','Swinm'),('skate','Skating'),('hike','Hiking')])
    # t5 = BooleanField('i accept the terms',default='checked',validators=[DataRequired()])




wtf = Blueprint('wtf',__name__,url_prefix='/wtf')

@wtf.route('/', methods=['GET','POST'])
def basic():
    form = ScriptForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        flash('welcome {username}'.format(username=username))
        return redirect(url_for('index'))
    return render_template('auth/formtest.html', form=form)

