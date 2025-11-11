from vars.database import db
from flask import jsonify

#CHECK IF USERNAME IS UNIQUE AMONG ALL TABLES
def checkUniqueness(name):
    from routes.students import Students
    from routes.instructors import Instructors
    from routes.admin import Admin

    #DEFINE AN ARRAY THAT STORES BOOLS FROM EACH USER ROUTE
    repeatedUser = []
    repeatedUser.append(db.session.query(Instructors.query.filter_by(username=name).exists()).scalar())
    repeatedUser.append(db.session.query(Students.query.filter_by(username=name).exists()).scalar())
    repeatedUser.append(db.session.query(Admin.query.filter_by(username=name).exists()).scalar())

    if not any(repeatedUser):
        return False
    else:
        return True
    

#CHECK LOGIN AND PASSWORD
def LoginCheck(username, password):
    from routes.students import Students
    from routes.instructors import Instructors
    from routes.admin import Admin

    instructor = Instructors.query.filter_by(username=username).first()
    student = Students.query.filter_by(username=username).first()
    admin = Admin.query.filter_by(username=username).first()

    if instructor and instructor.password == password:
        return jsonify(instructor.to_dict())
    elif student and student.password == password:
        return jsonify(student.to_dict())
    elif admin and admin.password == password:
        return jsonify(admin.to_dict())
    else:
        return jsonify({"message": "Wrong Username or Password"}), 401