from flask import url_for, request
from flask_admin import BaseView, expose
from flask_login import logout_user, current_user
from werkzeug.utils import redirect
from mainapp.utils import *
from mainapp import admin, db
from mainapp.models import BGH, Student, Teacher
from flask_admin.contrib.sqla import ModelView
from flask import render_template, request, redirect, jsonify, session, current_app
import smtplib
class AuthenticatedView(ModelView):
    can_export = True
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

class CustomAuthenticatedView(BaseView):

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))


class aboutUsView(CustomAuthenticatedView):
    @expose('/')
    def index(self):
        return self.render('Admin/about-us.html')




class editstudent(CustomAuthenticatedView):
    @expose('/')
    def index(self):
        return self.render('Admin/editstudent.html')

    def render(self, template, **kwargs):

        if template == 'Admin/editstudent.html':
            rs = getlisthsunknown()
            rsclass = getclassavailable()
            if(rs is not None and rsclass is not None):
                kwargs['data'] = rs
                kwargs['classes'] = rsclass
                return super(editstudent, self).render(template, **kwargs)
            return super(editstudent, self).render(template, **kwargs)


class chartClass(CustomAuthenticatedView):
    @expose('/')
    def index(self):
        return self.render('Admin/chartclass.html')

class sendmail(CustomAuthenticatedView):
    @expose('/')
    def index(self):
        return self.render('Admin/sendmail.html')

    def render(self, template, **kwargs):
        self.extra_js = [url_for("static", filename="js/chartadmin.js")]
        if template == 'Admin/sendmail.html':
            rs = getlisthsunpayment()
            if (rs is not None ):
                kwargs['data'] = rs

                return super(sendmail, self).render(template, **kwargs)
            return super(sendmail, self).render(template, **kwargs)

class chartSemester(CustomAuthenticatedView):
    @expose('/')
    def index(self):
        rs= listclass()
        return self.render('Admin/chartsemester.html', classes=rs)

class logoutView(CustomAuthenticatedView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('logout')


class userView(AuthenticatedView):
    form_excluded_columns = ['password', 'account_type','scores']
    column_exclude_list = ['password','account_type' ]
    column_filters = ['email', 'firstname', 'lastname', 'classid', 'Payment']
class teacherView(AuthenticatedView):
    column_filters= ['email', 'firstname', 'lastname', 'classid']
    column_exclude_list = ['password','account_type' ]
    can_delete = False
class BGHView(AuthenticatedView):
    column_filters= ['email', 'firstname', 'lastname']
    column_exclude_list = ['password','account_type' ]
    can_delete = False

admin.add_view(BGHView(BGH, db.session))
#BGH.add_view(AuthenticatedView(class, db.session))

admin.add_view(userView(Student,db.session, name='Học sinh'))
admin.add_view(ModelView(Policy,db.session,name='Quy định'))
admin.add_view(teacherView(Teacher,db.session,name='Giáo viên'))
admin.add_view(sendmail(name='Thông báo'))
admin.add_view(chartSemester(name='Thống kê học kì'))
admin.add_view(editstudent(name='Thêm học sinh vào lớp'))
admin.add_view(logoutView(name='Logout'))

