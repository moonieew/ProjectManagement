import string
import hashlib

#from passwordgenerator import PasswordGenerator
from sqlalchemy import engine, create_engine, update, delete, insert
from werkzeug.datastructures import TypeConversionDict
import smtplib

from mainapp.models import *

from sqlalchemy.orm import sessionmaker, scoped_session

Session = scoped_session(sessionmaker(bind=engine))
session = Session()



class Hs():
    def __init__(self, Student, phonehs, phoneph):
        self.student= Student
        self.phonehs = phonehs
        self.phoneph = phoneph
class Hsscore():
    def __init__(self, Student, Listscore):
        self.student = Student
        self.listscore = Listscore


class StudentScoreSubject():
    def __init__(self, Subject, Score):
        self.subject = Subject
        self.score = Score

class ChartDataClassSubject():
    def __init__(self, SubjectName, Percentage):
        self.subjectname = SubjectName
        self.percentage = Percentage


class SchoolYear_Semester():
    def __init__(self, SchoolYear, Semester):
        self.schoolYear = SchoolYear
        self.semester = Semester

#lấy danh sách lớp
def listclass():
    return Class.query.all()

 #lấy list học sinh ở lớp tạm
def getlisthsunknown():
    idclassunknown = Class.query.filter(Class.name == 'Lớp tạm').first()
    if idclassunknown is None:
        print("unknownisnone")
        return None
    liststudent = Student.query.filter(Student.classid == idclassunknown.id).all()
    if (liststudent is None or len(liststudent) == 0):
        return None
    return liststudent


#lấy list học sinh chưa thanh toán học phí
def getlisthsunpayment():
    listhsunpayment = Student.query.filter(Student.Payment != '1').all()
    if listhsunpayment is None:
        print("unknownisnone")
        return None
    return listhsunpayment




#thanh toán : payment -> 1
def paymentt(idhs):
    hs = Student.query.filter(Student.id == idhs).first()
    hs.Payment = '1'
    db.session.add(hs)
    db.session.commit()

#lấy 1 học sinh theo ID
def geths(idhs):
    return Student.query.filter(Student.id == idhs).first()

#lấy 1 giáo viên theo ID
def getgv(idgv):
    return Teacher.query.filter(Teacher.id == idgv).first();

#thêm 1 học sinh vào lớp ( thêm thông tin học sinh vào bảng học sinh, thêm điểm vào điểm)
def addstudentintoclass(idhs, idclass):
    hs = Student.query.filter(Student.id == idhs).first()
    hs.classid = idclass
    hs.password = str(hashlib.md5('123'.encode('utf-8')).hexdigest())
    db.session.add(hs)
    db.session.commit()
    listsjb = Subject.query.all()
    listtests = Policy.query.filter(Policy.name.contains('Số bài kiểm tra')).all()

    for sjb in listsjb:
        scr = Score()
        scr.student = idhs
        scr.subject_id = sjb.id
        scr.semester = 1
        db.session.add(scr)
        db.session.commit()
        scrid = Score.query.filter(Score.student == scr.student, Score.semester == scr.semester,
                                   Score.subject_id == scr.subject_id).first()
        for tests in listtests:
            testtype = tests.name.replace('Số bài kiểm tra ', '')
            print(testtype)
            for i in range(tests.value):
                scrdetail = ScoreDetail()
                scrdetail.score = scrid.id
                scrdetail.value = 0
                scrdetail.name = testtype
                db.session.add(scrdetail)
                db.session.commit()

# lấy list lớp còn trống ( sỉ số nhỏ hơn quy định)
def getclassavailable():
    quidinh = Policy.query.filter(Policy.name.contains('Sỉ số')).first()
    listclassavailable = Class.query.filter(Class.quantity < quidinh.value).all()
    return listclassavailable

#load bảng điểm học sinh theo lớp bộ môn
def load_hs(classstt, idteacher):
    listscore_and_hs = []
    list_score = []
    teacher = Teacher.query.filter(Teacher.id == idteacher).first()
    subjectid = teacher.subjectid
    classes = teacher_class_table.query.filter(teacher_class_table.teacher_id == idteacher).all()

    list_classid = []
    for class_item in classes:
        list_classid.append(Class.query.filter(Class.id == class_item.class_id).first())
    if (classstt == 0):
        lisths = load_lisths(list_classid[0].id)
    else:
        lisths = load_lisths(classstt)

    for i in lisths:
        id = i
        listscore = load_listscore_hs(i.id, teacher.subjectid, 1)
        if listscore is not None:
            listscore_and_hs.append(Hsscore(id, listscore))
    listtype = Policy.query.filter(Policy.name.contains('Điểm')).all()
    print(listtype)
    return listscore_and_hs, list_classid, listtype

# lấy list lớp mà giáo viên dạy
def load_listclass(idteacher):
    classes = teacher_class_table.query.filter(teacher_class_table.teacher_id == idteacher).all()
    list_classid = []
    for class_item in classes:
        list_classid.append(Class.query.filter(Class.id == class_item.class_id).first())
    return list_classid

#load danh sách lớp của gvcn
def load_class(idteacher):
    teacher = Teacher.query.filter(Teacher.id == idteacher).first()
    listhocsinh = load_lisths(teacher.classid)
    liHs=[]
    for item in listhocsinh:
        s =Hs(item,Phone.query.filter(Phone.student_id == item.id, Phone.name == "SĐT HS").first(),
           Phone.query.filter(Phone.student_id == item.id, Phone.name == "SĐT PH").first())
        liHs.append(s)
    return liHs

# lấy list học sinh theo lớp
def load_lisths(idclass):
    listhocsinh = Student.query.filter(Student.classid == idclass).all()
    return listhocsinh

#lấy list điểm của học sinh theo môn học, học kì
def load_listscore_hs(idhs, idsubject, idsemester):
    score = Score.query.filter(Score.semester == idsemester, Score.student == idhs,
                               Score.subject_id == idsubject).first()
    if score is None:
        return None
    listscore = ScoreDetail.query.filter(ScoreDetail.score == score.id).all()
    return listscore

def dtb(idhs, idsubject):
    ls= load_listscore_hs(idhs, idsubject,1)
    rs =diemTB(ls)
    return rs

#cập nhật điểm
def update_scoredetail(data):
    s = ScoreDetail.query.filter(ScoreDetail.id == data['id']).first()
    s.value = data['value']
    db.session.add(s)
    db.session.commit()

#cập nhật list điểm
def update_all_scoredetail(listdata):
    for item in listdata:
        update_scoredetail(item)

#cập nhật chi tiết học sinh
def update_studentdetail(data):
    s = Student.query.filter(Student.id == data['id']).first()
    s.value = data['value']
    db.session.add(s)
    db.session.commit()

#cập nhật chi tiết học sinh
def update_all_studentdetail(listdata):
    for item in listdata:
        update_studentdetail(item)


#load điểm học sinh
def load_score_hs(idhs):
    idsemester = 1
    data = []
    hs = Student.query.filter(Student.id == idhs).first()
    listScore = Score.query.filter(Score.student == hs.id, Score.semester == idsemester).all()
    ListStudentScoreSubject = []
    for i in listScore:
        scoredetail = ScoreDetail.query.filter(ScoreDetail.score == i.id).all()

        s = StudentScoreSubject((Subject.query.filter(Subject.id == i.subject_id)).first(), scoredetail)
        ListStudentScoreSubject.append(s)


    return ListStudentScoreSubject



#so sánh với quy định
def check_quidinh():
    rs = Policy.query.filter(Policy.name == 'Tren trung binh').first()
    return rs.value

#kiểm tra hệ số điểm
def check_heso(scoretype):
    str = "Điểm "
    str += scoretype
    rs = Policy.query.filter(Policy.name.contains(str)).first()
    if rs is None:
        return None
    return rs.value

#kiểm tra dtb
def check_diemtb(diem):
    if diem >= check_quidinh():
        return 1
    return 0




#tính điểm trung bình của 1 list điểm
def diemTB(listscore):
    sum = 0
    total = 0
    for i in listscore:
        heso = check_heso(i.name)
        if heso is None:
            return None
        total += heso
        sum += (i.value * heso)
    rs = sum / total
    return rs

#load thông tin học sinh
def load_studentinformation(idhs):
    hs = Student.query.filter(Student.id == idhs).first()
    cl = Class.query.filter(Class.id == hs.classid).first()
    p1 = Phone.query.filter(Phone.student_id == idhs, Phone.name == "SĐT HS").first()
    p2 = Phone.query.filter(Phone.student_id == idhs, Phone.name == "SĐT PH").first()
    if p1:
        pnhs = p1.value
    else:
        pnhs = ''
    if p2:
        pnph = p2.value
    else:
        pnph = ''
    return hs, cl, pnhs, pnph

#cập nhật thông tin hs
def utils_update_information_student(idhs, address, phone1, phone2):
    hs = Student.query.filter(Student.id == idhs).first()
    hs.address = address
    p1 = Phone.query.filter(Phone.student_id == hs.id, Phone.name == "SĐT HS").first()
    p2 = Phone.query.filter(Phone.student_id == hs.id, Phone.name == "SĐT PH").first()
    db.session.add(hs)
    if p1:
        p1.value = phone1
        db.session.add(p1)
    if p2:
        p2.value = phone2
        db.session.add(p2)
    db.session.commit()

#cập nhật password học sinh
def util_supdate_pass_student(idhs, oldpass, newpass):
    hs = Student.query.filter(Student.id == idhs).first()
    if hs.password == str(hashlib.md5(oldpass.strip().encode('utf-8')).hexdigest()):
        hs.password = str(hashlib.md5(newpass.strip().encode('utf-8')).hexdigest())
        db.session.add(hs)
        db.session.commit()
        return True
    else:
        return None

#load thông tin gv
def load_teacherinformation(idteacher):
    te = Teacher.query.filter(Teacher.id == idteacher).first()
    return te

#cập nhật password gv
def util_update_pass_teacher(idteacher, oldpass, newpass):
    te = Teacher.query.filter(Teacher.id == idteacher).first()
    if te.password == str(hashlib.md5(oldpass.strip().encode('utf-8')).hexdigest()):
        te.password = str(hashlib.md5(newpass.strip().encode('utf-8')).hexdigest())
        db.session.add(te)
        db.session.commit()
        return True
    else:
        return None


def util_supdate_pass_student_forgot(email):
    hs = Student.query.filter(Student.email == email).first()
    temppass = Forgotpass.query.filter(Forgotpass.mail == email).first()
    if temppass is None:
        temppass = Forgotpass()
        temppass.mail = email
    pw ='123'
    temppass.password = str(hashlib.md5(pw.strip().encode('utf-8')).hexdigest())
    mes = pw
    sever = smtplib.SMTP("smtp.gmail.com", 587)
    sever.starttls()
    sever.login("giakhuong0225@gmail.com", "0125884994678")
    sever.sendmail("giakhuong0225@gmail.com", email, mes)
    db.session.add(temppass)
    db.session.commit()

#lấy list lớp mà gv có thể gửi tb
def classnotify(idteacher):
    teacher = Teacher.query.filter(Teacher.id == idteacher).first()
    subjectid = teacher.subjectid
    classes = teacher_class_table.query.filter(teacher_class_table.teacher_id == idteacher).all()
    list_classid = []
    for class_item in classes:
        list_classid.append(Class.query.filter(Class.id == class_item.class_id).first())
    cl = Class.query.filter(Class.id == Teacher.classid).first()
    if not cl in list_classid:
        list_classid.append(cl)
    return list_classid, teacher

#gửi thông báo
def notify(name,classto, content):
    cl= Class.query.filter(Class.name== classto).first()
    classid= cl.id
    notic = Notice(name=name, classid=classid, content=content)
    db.session.add(notic)
    try:
        db.session.commit()
        return True
    except:
        return False




def load_data_chart_class(idclass):
    lop = Class.query.filter(Class.id == idclass).first()
    lisths = load_lisths(lop.id)
    listsubject = Subject.query.all()
    totalstudent = len(lisths)
    datasubject = dict()
    for subject in listsubject:
        count_tren_tb = 0
        for hs in lisths:
            result = load_listscore_hs(hs.id, subject.id, 1)
            if result is not None:
                diemtb = diemTB(result)
                if diemtb is not None:
                    rs = check_diemtb(diemtb)
                    count_tren_tb += rs
        Percentage = Percentagecheck(totalstudent, count_tren_tb)
        datasubject[subject.name] = Percentage
    data = dict()
    data['data'] = datasubject
    data['quiqinh'] = check_quidinh()
    print(data)
    return data

def load_data_chart():
    lisths = Student.query.all()
    listsubject = Subject.query.all()
    totalstudent = len(lisths)
    datasubject = dict()
    for subject in listsubject:
        count_tren_tb = 0
        for hs in lisths:
            result = load_listscore_hs(hs.id, subject.id, 1)
            if result is not None:
                diemtb = diemTB(result)
                if diemtb is not None:
                    rs = check_diemtb(diemtb)
                    count_tren_tb += rs
        Percentage = Percentagecheck(totalstudent, count_tren_tb)
        datasubject[subject.name] = Percentage
    data = dict()
    data['data'] = datasubject
    data['quiqinh'] = check_quidinh()
    print(data)
    return data


def addcolumnscorestudents(name, listscoreid):
    for item in listscoreid:
        addcolumnscore(name, item.listscore[0].score)


def addcolumnscore(Name, idscore):
    name = Name
    sc = ScoreDetail()
    sc.name = name
    sc.value = 0
    sc.score = idscore
    db.session.add(sc)
    db.session.commit()





# def load_data_chart_semester(idGrade, idSemester):
#     semester = Semester.query.filter(Semester.id == idSemester).first()
#     grade = Grade.query.filter(Grade.id == idGrade).first()
#     if grade is None:
#         print(idGrade)
#     listclass = Class.query.filter(Class.gradeid == grade.id).all()
#     listsubject = Subject.query.all()
#     lisths = []
#     for classitem in listclass:
#         lisths.append(Student.query.filter(Student.classid == classitem.id).all())
#
#     data = dict()
#
#     for subject in listsubject:
#         diemtbsubject = 0
#         count = 0
#         for lhs in lisths:
#             count += len(lhs)
#             for hs in lhs:
#                 rs = load_listscore_hs(hs.id, subject.id, idSemester)
#                 if rs is not None:
#                     diemtb = diemTB(rs)
#                     diemtbsubject += diemtb
#         tb = float(diemtbsubject) / count
#         data[subject.name] = round(tb, 2)
#     print(data)
#     return data
#
#
# def load_semester():
#     listsemester = Semester.query.all()
#     listSchoolYear_Semester = dict()
#     mem = listsemester[0].schoolyear
#     lists = []
#     for i in range(len(listsemester)):
#
#         if listsemester[i].schoolyear == mem:
#             a = dict()
#             a.clear()
#             a[listsemester[i].name] = listsemester[i].id
#             lists.append(a)
#         else:
#             listSchoolYear_Semester[mem] = lists.copy()
#             lists.clear()
#             mem = listsemester[i].schoolyear
#             a = dict()
#             a.clear()
#             a[listsemester[i].name] = listsemester[i].id
#             lists.append(a)
#         if i + 1 == len(listsemester):
#             listSchoolYear_Semester[mem] = lists
#     print(listSchoolYear_Semester)
#     return listSchoolYear_Semester
#
#
# def load_grade():
#     listgrade = Grade.query.all()
#     data = dict()
#     for item in listgrade:
#         data[item.id] = item.name
#     return data
#
#


def getlisths():
    return BGH.query.order_by()


def getlisthstest():
    return BGH.query.filter(BGH.id == 1).first()

def Percentagecheck(tong, tongdiemtrentb):
    rs = float(tongdiemtrentb) / tong
    rs = rs * 100
    return round(rs)