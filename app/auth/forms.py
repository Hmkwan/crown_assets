from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User, AccountRequest


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')


class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    employee_no = StringField('工号', validators=[DataRequired()])
    full_name = StringField('姓名', validators=[DataRequired()])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    department = SelectField('所属部门', choices=[], coerce=int, validators=[DataRequired()])
    role_requested = SelectField('申请角色', choices=[
        ('user', '普通用户'),
        ('technician', '技术员'),
        ('department_head', '部门负责人')
    ], validators=[DataRequired()], default='user')
    reason = TextAreaField('申请说明（可选）')
    password = PasswordField('密码', validators=[DataRequired()])
    password2 = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('提交申请')
    
    def validate_username(self, username):
        username_value = username.data.strip()
        if User.query.filter_by(username=username_value).first():
            raise ValidationError('该用户名已被使用，请选择其他用户名。')
        existing = AccountRequest.query.filter_by(username=username_value, status='pending').first()
        if existing:
            raise ValidationError('该用户名的申请正在审核中，请耐心等待处理。')
            
    def validate_email(self, email):
        email_value = email.data.strip()
        if User.query.filter_by(email=email_value).first():
            raise ValidationError('该邮箱已被使用，请选择其他邮箱。')
        existing = AccountRequest.query.filter_by(email=email_value, status='pending').first()
        if existing:
            raise ValidationError('该邮箱已提交申请，请等待管理员审批。')