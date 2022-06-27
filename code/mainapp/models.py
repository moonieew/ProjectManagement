# import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import Column, Integer, Float, String, Date, Boolean, ForeignKey, CheckConstraint, PrimaryKeyConstraint, \
    true
from sqlalchemy import Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from mainapp import Admin, db
from datetime import date
from datetime import datetime
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask_login import logout_user, current_user
from werkzeug.utils import redirect
from flask import url_for, request

Base = declarative_base()


class Account(db.Model):
    __tablename__ = "Account"
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(50), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    firstname = Column(String(50), nullable=False)
    lastname = Column(String(50), nullable=False)
    address = Column(String(100), nullable=True)
    account_type = Column(String(50))
    age = Column(Integer)
    sex = Column(Enum('Male', 'Female', 'Other'))
    active = Column(Boolean, default=True)  # 1: online, 0:offine
    birthday = Column(Date)
    role = Column(Integer, default=3)  # 1: BGH, 2: Teacher, 3:Student


class Teacher(Account, UserMixin):
    __tablename__ = 'Teacher'
    # __table_args__ = {'extend_existing': True}
    subjectid = Column(Integer, ForeignKey("subject.id"))
    classid = Column(Integer, ForeignKey("class.id"))

    def __init__(self, firstname, password, email, active, role):
        self.firstname = firstname
        self.password = password
        self.email = email
        self.active = active
        self.role = role

    def get_id(self):
        return self.id

    def is_active(self):
        return self.active

    def get_email(self):
        return self.email

    def get_role(self):
        return self.role


class Student(Account, UserMixin):
    __tablename__ = 'Student'
    classid = Column(Integer, ForeignKey("Class.id"))
    Payment = Column(Enum('1', '2', '3'))  # 1=Dathanhtoan,2=Dathanhtoan1phan,3=Chuathanhtoan
    Class = relationship("Class", back_populates="studentt")
    scores = relationship("Score", back_populates="studentt")
    def __init__(self, firstname, password, email, active, role):
        self.firstname = firstname
        self.password = password
        self.email = email
        self.active = active
        self.role = role

    def get_id(self):
        return self.id

    def is_active(self):
        return self.active

    def get_email(self):
        return self.email

    def get_role(self):
        return self.role

    # __table_args__ = {'extend_existing': True}


class BGH(Account, UserMixin):
    __tablename__ = 'bgh'

    # __table_args__ = {'extend_existing': True}
    def __init__(self, firstname, password, email, active, role):
        self.firstname = firstname
        self.password = password
        self.email = email
        self.active = active
        self.role = role

    def get_id(self):
        return self.id

    def is_active(self):
        return self.active

    def get_email(self):
        return self.email

    def get_role(self):
        return self.role


class Grade(db.Model):
    __tablename__ = 'grade'
    # __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    name = Column(String(50))


class Class(db.Model):
    __tablename__ = 'Class'
    # __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    quantity = Column(Integer, CheckConstraint('quantity >20 and quantity <=40'))
    gradeid = Column(Integer, ForeignKey("grade.id"))
    studentt = relationship("Student", back_populates="Class")
    def __str__(self):
        return self.name


class Semester(db.Model):
    __tablename__ = 'semester'
    # __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    schoolyear = Column(String(50))
    from_date = Column(Date)
    to_date = Column(Date)

    def __str__(self):
        return self.name



class Score(db.Model, Base):
    __tablename__ = 'Score'
    # __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    semester = Column(Integer, ForeignKey("semester.id"))
    student = Column(Integer, ForeignKey("Student.id"))
    subject_id = Column(Integer, ForeignKey("subject.id"))
    studentt = relationship("Student", back_populates="scores")
    scrdetail = relationship("ScoreDetail", back_populates="scoress")

class Subject(db.Model, Base):
    __tablename__ = 'subject'
    # __table_args__ = {'extend_existing': True}
    id = Column(Integer, unique=True, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=False)
    sessions = Column(Integer)

    def __str__(self):
        return self.name


class ScoreDetail(db.Model, Base):
    __tablename__ = 'scoredetail'
    # __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=False)
    value = Column(Float, nullable=True)
    score = Column(Integer, ForeignKey("Score.id"))
    scoress = relationship("Score", back_populates="scrdetail")
    def __str__(self):
        return self.name


class Phone(db.Model):
    __tablename__ = 'Phone'
    # __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Integer)  # 1=hocsinh,2=phuhuynh
    name = Column(String(50), nullable=False, unique=False)
    value = Column(String(20), nullable=True)
    student_id = Column(Integer, ForeignKey(Student.id), nullable=False)


class grade_subject_table(db.Model, UserMixin):
    __tablename__ = 'grade_subject'

    grade_id = Column(Integer, ForeignKey("grade.id"))
    subject_id = Column(Integer, ForeignKey("subject.id"))
    __table_args__ = (
        PrimaryKeyConstraint('grade_id', 'subject_id'), {}
    )


class teacher_class_table(db.Model, UserMixin):
    __tablename__ = 'teacher_class'
    teacher_id = Column(Integer, ForeignKey("Teacher.id"))
    class_id = Column(Integer, ForeignKey("Class.id"))
    __table_args__ = (
        PrimaryKeyConstraint('teacher_id', 'class_id'), {},
    )


class Policy(db.Model):
    __tablename__ = 'Policy'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True)
    value = Column(Integer)

class Forgotpass(db.Model):
    __tablename__ = 'Passwordtemp'
    id = Column(Integer, primary_key=True, autoincrement=True)
    mail = Column(String(50), unique=True)
    password = Column(String(50))


class Notice(db.Model):
    id= Column(Integer, primary_key=True, autoincrement=True)
    name=Column(String(50))
    content= Column(String(1000))
    classid=Column(Integer, ForeignKey(Class.id), nullable= False)



if __name__ == "__main__":
    db.create_all()
