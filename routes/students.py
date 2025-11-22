from flask import Flask, request, redirect, jsonify, Blueprint
from vars.database import db
from vars.port import port_number
from sqlalchemy.types import JSON
from sqlalchemy.ext.mutable import MutableDict
import requests
from routes.utils.functions import checkUniqueness, checkCourseCapacity, checkScheduleConflict
from routes.courses import updateClassSizeUp, updateClassSizeDown
from werkzeug.security import generate_password_hash, check_password_hash

students_blueprint = Blueprint('students', __name__)

class Students(db.Model):
    id = db.Column(db.Integer, primary_key=True) #INT FOR ID
    username = db.Column(db.String(50), nullable=False) #USERNAME FOR STUDENT
    password = db.Column(db.String(5000), nullable=False) #PASSWORD FOR STUDENT
    first_name = db.Column(db.String(50), nullable=False) #STRING FOR FIRST NAME
    last_name = db.Column(db.String(50), nullable=False) #STRING FOR LAST NAME
    registered_courses = db.Column(MutableDict.as_mutable(JSON), nullable=False, default=dict) #STORES ARRAY OF COURSES BY ID, EX: [1, 2, 5 ,7 ,9]
    status = db.Column(db.String(5), nullable=False, default="STUDT") #CHECK ACCOUNT STATUS

    def to_dict(self):
        return {"id": self.id, "status": self.status, "username":self.username, "password":self.password, "first_name": self.first_name, "last_name": self.last_name, "registered_courses": self.registered_courses}


#GET
@students_blueprint.route('/students', methods=['GET'])
def GetStudents():
    list = Students.query.all()
    return jsonify([i.to_dict() for i in list])

#GET BY ID
@students_blueprint.route('/students/<int:id>', methods=['GET'])
def GetStudentById(id):
    student = Students.query.get_or_404(id)
    return jsonify(student.to_dict())

#POST
@students_blueprint.route('/students', methods=['POST'])
def Create():
    x = request.json
    # Hash the password before storing
    hashed_password = generate_password_hash(x['password'])
    data = Students(username=x['username'], password=hashed_password, first_name=x['first_name'], last_name=x['last_name'])
    #CHECK IF USERNAME IS UNIQUE
    repeatedUser = checkUniqueness(data.username)
    if not repeatedUser:
        db.session.add(data)
        db.session.commit()
        return jsonify(data.to_dict())
    else:
        return {'message': "username already exists"}
    

#PUT
@students_blueprint.route('/students/<int:id>', methods=['PUT'])
def Change(id):
    updateData = Students.query.get_or_404(id)
    x = request.json
    #OVERWRITE DATA
    if 'username' in x:
        updateData.username = x['username']
    if 'password' in x:
        # Hash the password if it's being updated
        updateData.password = generate_password_hash(x['password'])
    repeatedUser = checkUniqueness(updateData.username)
    if not repeatedUser:
        db.session.commit()
        return jsonify(updateData.to_dict())
    else:
        return {'message': "username already exists"}

#ADD A COURSE TO A STUDENT
@students_blueprint.route('/students/<int:id>/courses/<string:unique_id>', methods=['PUT'])
def AddStudentToCourse(id, unique_id):
    student = Students.query.get_or_404(id)
    
    # Check if already registered
    if unique_id in student.registered_courses:
        return jsonify({'message': 'Student is already registered in this course'}), 400
    
    # Check course capacity
    has_capacity, capacity_message = checkCourseCapacity(unique_id)
    if not has_capacity:
        return jsonify({'message': capacity_message}), 400
    
    # Check for schedule conflicts
    no_conflict, conflict_message = checkScheduleConflict(id, unique_id)
    if not no_conflict:
        return jsonify({'message': conflict_message}), 400
    
    # All checks passed, add the course
    student.registered_courses.update({unique_id: 0})
    db.session.commit()
    updateClassSizeUp(unique_id)
    print({'message': 'student added to course'})
    return jsonify(student.to_dict())
    
#CHANGE A GRADE
@students_blueprint.route('/students/<int:id>/courses/<string:unique_id>/grades/<int:value>', methods=['PUT'])
def ChangeGrade(id, unique_id, value):
    student = Students.query.get_or_404(id)
    if unique_id in student.registered_courses:
        student.registered_courses[unique_id] = value
        db.session.commit()
        return jsonify(student.to_dict())
    return {'message': 'Student is not registered in this course'}

#REMOVE COURSE FROM STUDENT
@students_blueprint.route('/students/<int:id>/courses/<string:unique_id>', methods=['DELETE'])
def RemoveStudentFromCourse(id, unique_id):
    student = Students.query.get_or_404(id)
    if unique_id in student.registered_courses:
        del student.registered_courses[unique_id]
        db.session.commit()
        updateClassSizeDown(unique_id)
        return jsonify(student.to_dict())
    else:
        return jsonify({'message': 'Student is not in course'})

#DELETE STUDENT
@students_blueprint.route('/students/<int:id>', methods=['DELETE'])
def Delete(id):
    remove = Students.query.get_or_404(id)
    db.session.delete(remove)
    db.session.commit()
    return jsonify({'message': 'Student deleted'})
