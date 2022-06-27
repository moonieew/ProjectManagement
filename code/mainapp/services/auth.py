import hashlib

from mainapp.models import *


def authValidate(request):  # xacminhtaikhoan

    type = 1
    email = request.form.get('email')
    password = request.form.get('password')
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    fp = Forgotpass.query.filter(Forgotpass.mail == email).first()
    if fp:
        hs = Student.query.filter(Student.email == email.strip()).first()
        if hs:
            if fp.password == password:
                hs.password = password
                db.session.add(hs)
                db.session.commit()
                user = Student.query.filter(Student.email == email.strip(),
                                            Student.password == password).first()
                return user, "Login success as student", type
    isEmailMatched = Student.query.filter(Student.email == email.strip()).first()
    if not isEmailMatched:
        type = 2
        isEmailMatched = Teacher.query.filter(Teacher.email == email.strip()).first()
        if not isEmailMatched:
            type = 3
            isEmailMatched = BGH.query.filter(BGH.email == email.strip()).first()
            if not isEmailMatched:
                return None, "Login error", type

    if type == 1:
        isPasswordMatched = Student.query.filter(Student.password == password, Student.email == email.strip()).first()

        if not isPasswordMatched or not isEmailMatched:
            return None, "Login student error", type
        else:
            if not Student.query.filter(Student.password == password, Student.email == email.strip(),
                                        Student.active == True).first():
                return None, "Your account is blocked", type
            user = Student.query.filter(Student.email == email.strip(),
                                        Student.password == password).first()
            return user, "Login success as student", type
    if type == 2:
        isPasswordMatched = Teacher.query.filter(Teacher.password == password, Teacher.email == email.strip(),
                                                 Teacher.active == True).first()
        if not isPasswordMatched and not isEmailMatched:
            return None, "Login teacher error", type
        else:
            user = Teacher.query.filter(Teacher.email == email.strip(),
                                        Teacher.password == password).first()
            return user, "Login success as teacher", type
    if type == 3:
        isPasswordMatched = BGH.query.filter(BGH.password == password, BGH.email == email.strip(),
                                             BGH.active == True).first()
        if not isPasswordMatched and not isEmailMatched:
            return None, "Login Admin error", type
        else:
            user = BGH.query.filter(BGH.email == email.strip(),
                                        BGH.password == password).first()
            return user, "Login success as Admin", type

    return None, "Login error", type


def authValidateAdmin(request):  # xacminhtaikhoan_admin

    email = request.form.get('email')

    isEmailMatched = BGH.query.filter(BGH.email == email).first()

    password = request.form.get('password')
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    isPasswordMatched = BGH.query.filter(BGH.password == password, BGH.email == email).first()

    if not isPasswordMatched or not isEmailMatched:
        return None, "Login error"

    user = BGH.query.filter(BGH.email == email.strip(),
                            BGH.password == password).first()

    return user, "True"


def contactValidate(request):
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    return name, email, message
