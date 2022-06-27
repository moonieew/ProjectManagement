# from os import environ
# from flask_wtf import FlaskForm
import json
import smtplib
import paypalrestsdk
from paypalrestsdk import configure

from mainapp.utils import *
from mainapp.admin_module import *
from flask_login import login_user, login_required, current_user
from mainapp import app, utils, mail, db, login_manager
from math import ceil
from mainapp.services.auth import authValidate, contactValidate, authValidateAdmin
from mainapp.models import *
from functools import wraps
# from flask_mail import Message
from mainapp.admin_module import *
from flask import render_template, request, redirect, jsonify, session, current_app, flash

login_manager.login_view = 'login'
from random import sample




@login_manager.user_loader  # load user
def userLoad(userId):
    if (session['type'] == 1):
        return Student.query.get(userId)
    if (session['type'] == 2):
        return Teacher.query.get(userId)
    if (session['type'] == 3):
        return BGH.query.get(userId)


@app.route("/stnotice")
@login_required
def stnotice():
    if session['type'] != 1:
        return render_template('dashboard/index.html', type=session['type'])
    return render_template("dashboard/Student/mynotice.html", type=session['type'])


@app.route("/index")
@app.route("/")  # index
def index():
    session['idclassselected'] = 0
    session['defaultsemester'] = 1
    session['defaultgradee'] = 1
    session['idclass'] = 1
    # print(session)
    if ('type' in session):
        if session['type'] == 1:
            return render_template('dashboard/Student/index.html', type=session['type'])
        if session['type'] == 2:
            return render_template('dashboard/Teacher/index.html', type=session['type'])
        if session['type'] == 3:
            return redirect("/admin")
    else:
        session['type'] = 0
        return render_template('dashboard/index.html', type=session['type'])
    return render_template('dashboard/index.html', type=session['type'])


@app.route("/thongbao", methods=['POST', 'GET'])  # gửi thông báo
@login_required
def thongbao():
    err = ''
    if session['type'] != 2:
        return render_template('dashboard/index.html', type=session['type'])
    list_classid, teacher = utils.classnotify(current_user.id)

    if request.method == "POST":
        name = request.form.get('name')
        classto = request.form.get('toclass')
        content = request.form.get('content')
        rs = utils.notify(name, classto, content)
        if rs is True:
            err = "Gửi thành công"
        else:
            err = "Gửi thất bại "
    return render_template("dashboard/Teacher/thongbao.html", type=session['type'], list_classid=list_classid,
                           teacher=teacher, err=err)


@app.route("/chunhiem", methods=['POST', 'GET'])  # load danh sách lớp chủ nhiệm
@login_required
def chunhiem():
    if session['type'] != 2:
        return render_template('dashboard/index.html', type=session['type'])
    liHs = load_class(session['_user_id'])
    return render_template('dashboard/teacher/chunhiem.html', lisths=liHs,
                           type=session['type'])


@app.route("/updateteacherinformation", methods=['POST'])  # cập nhật thông tin học sin
@login_required
def updateteacherinformation():
    if session['type'] != 2:
        return render_template('dashboard/index.html', type=session['type'])
    idhs = request.form['hiddenid']
    address = request.form['address']
    phonehs = request.form['phonehs']
    phoneph = request.form['phoneph']
    utils_update_information_student(idhs, address, phonehs, phoneph)
    datainfor, classnamestudent, phone = load_studentinformation(idhs)
    return render_template('dashboard/Teacher/teacherinformation.html', hs=datainfor, cl=classnamestudent, pnhs=phonehs,
                           pnph=phoneph)


@app.route("/editscore", methods=['POST', 'GET'])  # chỉnh sửa điểm học sinh
@login_required
def editscore():
    if session['type'] != 2:
        return render_template('dashboard/index.html', type=session['type'])
    if request.method == "GET":
        listscore_and_hs, classes, listtype = load_hs(session['idclassselected'], session['_user_id'])
        print('here')
        print(session)
        return render_template('dashboard/Teacher/editscore.html', listscore_and_hs=listscore_and_hs, classes=classes,
                               listtype=listtype, type=session['type'])
    elif request.method == "POST":
        classid = request.form['idSelected']

        listscore_and_hs, classes, listtype = load_hs(classid, session['_user_id'])
        return render_template('dashboard/Teacher/editscore.html', listscore_and_hs=listscore_and_hs, classes=classes,
                               listtype=listtype, type=session['type'])
    else:
        pass


@app.route("/addcolumn", methods=['POST'])  # thêm cột điểm
@login_required
def addcolumn():
    if session['type'] != 2:
        return render_template('dashboard/index.html', type=session['type'])
    Name = request.form['listype']
    session['idclassselected'] = request.form['name']
    listscore_and_hs, classes, listtype = load_hs(session['idclassselected'], session['_user_id'])
    addcolumnscorestudents(Name, listscore_and_hs)
    return redirect('editscore')


@app.route("/hsscore", methods=['POST', 'GET'])  # điểm học sinh

def hsscore():
    if session['type'] != 1:
        return render_template('dashboard/index.html', type=session['type'])
    if request.method == "GET":

        ListStudentScoreSubject = load_score_hs(session['_user_id'])
        tbm = []
        for item in ListStudentScoreSubject:
            rs = dtb(session['_user_id'], item.subject.id)
            tbm.append(rs)
        return render_template('dashboard/Student/hsscore.html', ListStudentScoreSubject=ListStudentScoreSubject,
                               type=session['type'], tbm=tbm)
    elif request.method == "POST":
        classid = request.form['idSelected']

        ListStudentScoreSubject = load_score_hs(session['_user_id'])
        tbm = []
        for item in ListStudentScoreSubject :
            rs= dtb(session['_user_id'],item.subject.id)




        return render_template('dashboard/Student/hsscore.html', ListStudentScoreSubject=ListStudentScoreSubject,
                               type=session['type'], tbm= tbm)
    else:
        pass


@app.route("/studentinformation", methods=['POST', 'GET'])  # load học sinh
@login_required
def studentinformation():
    if session['type'] != 1:
        return render_template('dashboard/index.html', type=session['type'])

    hs, cl, pnhs, pnph = load_studentinformation(current_user.id)

    return render_template('dashboard/Student/studentinformation.html', hs=hs, cl=cl, pnhs=pnhs, pnph=pnph,
                           type=session['type'])


@app.route("/updatestudentinformation", methods=['POST'])  # cập nhật thông tin học sinh
@login_required
def updatestudentinformation():
    if session['type'] != 1:
        return render_template('dashboard/index.html', type=session['type'])
    idhs = request.form['hiddenid']
    address = request.form['address']
    phonehs = request.form['phonehs']
    phoneph = request.form['phoneph']
    utils_update_information_student(idhs, address, phonehs, phoneph)
    datainfor, classnamestudent, phone = load_studentinformation(idhs)
    return render_template('dashboard/Student/studentinformation.html', hs=datainfor, cl=classnamestudent, pnhs=phonehs,
                           pnph=phoneph)


@app.route("/updatestudenpassword", methods=['POST'])  # học sinh đổi mật khẩu
@login_required
def updatestudenpassword():
    if session['type'] != 1:
        return render_template('dashboard/index.html', type=session['type'])
    idhs = request.form['hiddenid']
    oldpass = request.form['passwordold']
    newpass = request.form['passwordnew']

    rs = util_supdate_pass_student(idhs, oldpass, newpass)
    if rs is None:
        hs, cl, pnhs, phph = load_studentinformation(idhs)
        return render_template('dashboard/Student/studentinformation.html', hs=hs, cl=cl, pnhs=pnhs, phph=phph,
                               error="1")
    hs, cl, pnhs, phph = load_studentinformation(idhs)
    return render_template('dashboard/Student/studentinformation.html', hs=hs, cl=cl, pnhs=pnhs, phph=phph, success="1")


@app.route("/teacherinformation", methods=['POST', 'GET'])  # load gv
@login_required
def teacherinformation():
    if session['type'] != 2:
        return render_template('dashboard/index.html', type=session['type'])

    te = load_teacherinformation(current_user.id)

    return render_template('dashboard/Teacher/teacherinformation.html', te=te,
                           type=session['type'])


@app.route("/updateteacherpassword", methods=['POST'])  # gv đổi mật khẩu
@login_required
def updateteacherpassword():
    if session['type'] != 2:
        return render_template('dashboard/index.html', type=session['type'])
    idteacher = request.form['hiddenid']
    oldpass = request.form['passwordold']
    newpass = request.form['passwordnew']

    rs = util_update_pass_teacher(idteacher, oldpass, newpass)
    if rs is None:
        te = load_teacherinformation(idteacher)
        return render_template('dashboard/Teacher/teacherinformation.html', te=te, error="1")
    te = load_teacherinformation(idteacher)
    return render_template('dashboard/Teacher/teacherinformation.html', te=te, success="1")


@app.route("/chonlop", methods=['POST', 'GET'])  # @login_required
@login_required
def index2():
    return render_template('dashboard/index.html')


@app.route("/forgotpassword", methods=['POST'])  # @login_required
def forgotpassword():
    email = request.form['email']
    util_supdate_pass_student_forgot(email)
    return render_template('dashboard/index.html', send="1")


@app.route("/scorechart", methods=['POST', 'GET'])
@login_required
def scorechart():
    if session['type'] != 2:
        return render_template('dashboard/index.html', type=session['type'])
    if request.method == "GET":
        print(session)
        classes = load_listclass(session['_user_id'])
        return render_template('dashboard/Teacher/scorechart.html', classes=classes, type=session['type'])
    elif request.method == "POST":
        classes = load_listclass(session['_user_id'])
        return render_template('dashboard/Teacher/scorechart.html', classes=classes, type=session['type'])
    else:
        pass

@app.route("/scorechart2", methods=['POST', 'GET'])
@login_required
def scorechart2():
    if session['type'] != 2:
        return render_template('dashboard/index.html', type=session['type'])
    if request.method == "GET":
        classes=[]
        print(session)

        te= Teacher.query.filter(Teacher.id== current_user.id).first()
        classes.append(te.classid)
        return render_template('dashboard/Teacher/scorechart2.html', classes=classes, type=session['type'])
    elif request.method == "POST":
        classes = load_listclass(session['_user_id'])
        return render_template('dashboard/Teacher/scorechart2.html', classes=classes, type=session['type'])
    else:
        pass

@app.route("/thanhtoan")
@login_required
def thanhtoan():
    if session['type'] != 1:
        return render_template('dashboard/index.html', type=session['type'])
    idhs = session['_user_id']
    hs = geths(idhs)

    print(hs.Payment)
    return render_template('dashboard/Student/thanhtoan.html', hs=hs, type=session['type'])


@app.route('/payment', methods=['POST'])
@login_required
def payment():
    paypalrestsdk.configure({
        "mode": "sandbox",  # sandbox or live
        "client_id": "AY6Y5njJ3HBABdNhIpDHhLIQPZMmVfZ_sZ0OJa0CPu38RIkXIVQTf4R6cjfTaERMeSSCbtvfvZPlBB4J",
        "client_secret": "EPU6W2hz8bBiG_ZOb5xrgTMhDF8U50nviYVrXJ2XxF_7wEWPKJSt8dHxtsMxoGiACcf5iHpZDyPFKhZc"})

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "http://127.0.0.1:5000/thanhtoan",
            "cancel_url": "http://127.0.0.1:5000/thanhtoan"},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "Payment Fee",
                    "sku": "12345",
                    "price": "500.00",
                    "currency": "USD",
                    "quantity": 1}]},
            "amount": {
                "total": "500.00",
                "currency": "USD"},
            "description": "This is the payment transaction description."}]})

    if payment.create():
        print('Payment success!')
    else:
        print(payment.error)

    return jsonify({'paymentID': payment.id})


@app.route('/execute', methods=['POST'])
@login_required
def execute():
    success = False

    payment = paypalrestsdk.Payment.find(request.form['paymentID'])

    if payment.execute({'payer_id': request.form['payerID']}):
        flash('Execute success!')
        success = True
        idhs = session['_user_id']
        paymentt(idhs)
    else:
        print(payment.error)

    return redirect('thanhtoan')


@app.errorhandler(404)  # @login_required
@login_required
def notFound(e):
    return render_template('dashboard/404.html'), 404


@app.route('/login')
@app.route('/dashboard/index.html')
def login():
    session['type'] = 0
    error = 'none'
    return render_template('dashboard/index.html')


@app.route('/login', methods=['POST'])  # đăng nhập
def login_post():
    user = request.form
    user, error, type = authValidate(request)
    if not user:
        return render_template('dashboard/index.html', error=error)
    session['type'] = type
    login_user(user=user)
    return redirect('index')


@app.route('/signup')  # @login_required
def signup():
    return render_template('dashboard/register.html')


@app.route('/logout')  # đăng xuất
def logout():
    logout_user()
    return render_template('dashboard/index.html')



@app.route('/login-admin', methods=['POST', 'GET'])
def login_admin():
    session['type'] = 3
    session['idclassselected'] = 0
    session['defaultsemester'] = 1
    session['defaultgradee'] = 1
    if request.method == 'GET':
        return redirect('/admin/')
    if request.method == 'POST':
        user, error = authValidateAdmin(request)
        if not user:
            return "error"

    login_user(user=user)
    return redirect('/admin/')



@app.route('/api/data_id_score', methods=['POST'])
@login_required
def data_id_score():
    dataidscrore = json.loads(request.data)
    print(dataidscrore)
    update_all_scoredetail(dataidscrore)
    return jsonify(dataidscrore)


@app.route('/data', methods=['POST', 'GET'])
@login_required
def dataSubjectAndScore():
    if request.method == "GET":
        data = load_data_chart_class(session['idclass'])
        return jsonify(data)
    elif request.method == "POST":
        rqdata = json.loads(request.data)
        session['idclass'] = int(rqdata['idclass'])
        return "sth"
    else:
        pass


@app.route('/data2', methods=['POST', 'GET'])
@login_required
def dataSemesterGradeSubject():
    if request.method == "GET":
        data = load_data_chart_class()
        return jsonify(data)
    elif request.method == "POST":
        rqdata = json.loads(request.data)

        return "sth"
    else:
        pass


# @app.route('/semester')
# def dataSemesterGradeSubjectt():
#     data = load_semester()
#
#     return jsonify(data)
#
#
# @app.route('/grade')
# def dataGrade():
#     data = load_grade()
#     return jsonify(data)


@app.route("/sendmail", methods=['POST'])
@login_required
def sendmail():
    rs = getlisthsunpayment()
    mes = request.form['msg']
    sever = smtplib.SMTP("smtp.gmail.com", 587)
    sever.starttls()
    sever.login("giakhuong0225@gmail.com", "0125884994678")
    for item in rs:
        sever.sendmail("giakhuong0225@gmail.com", item.email, mes)
    return redirect('admin/sendmail/')


@app.route("/addstudentclass", methods=['POST'])
@login_required
def addstudentclass():
    idhs = request.form['hiddenid']
    classid = request.form['selectclass']
    addstudentintoclass(idhs, classid)
    return redirect('admin/editstudent/')


@app.route('/admin/editstudent')
@login_required
def returndata():
    render_template('Admin/index.html', data=2)


@app.route("/admin")  # admin
@login_required
def index_admin():
    return render_template("admin/index.html")


if __name__ == "__main__":
    from mainapp.admin_module import *

    app.run(debug=True)
