from flask import Flask, request, redirect, jsonify, Blueprint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import JSON
from sqlalchemy.ext.mutable import MutableList
from vars.database import db
from vars.port import port_number
import requests
from routes.utils.functions import checkUniqueness
from routes.courses import addInstructor, removeInstructor
from werkzeug.security import generate_password_hash, check_password_hash

instructors_blueprint = Blueprint('instructors', __name__)

class Instructors(db.Model):
    id = db.Column(db.Integer, primary_key=True) #INT FOR ID
    username = db.Column(db.String(50), nullable=False) #USERNAME FOR INSTRUCTOR
    password = db.Column(db.String(5000), nullable=False) #PASSWORD FOR INSTRUCTOR
    first_name = db.Column(db.String(50), nullable=False) #STRING FOR FIRST NAME
    last_name = db.Column(db.String(50), nullable=False) #STRING FOR LAST NAME
    assigned_courses = db.Column(MutableList.as_mutable(JSON), default=list) #ARRAY OF COURSES ASSIGNED TO THIS INSTRUCTOR
    status = db.Column(db.String(5), nullable=False, default="TEACH") #CHECK ACCOUNT STATUS

    def to_dict(self):
        return {"id": self.id, "status": self.status, "username": self.username, "password": self.password, "first_name": self.first_name, "last_name": self.last_name, "assigned_courses": self.assigned_courses}

#GET
@instructors_blueprint.route('/instructors', methods=['GET'])
def GetInstructors():
    list = Instructors.query.all()
    return jsonify([i.to_dict() for i in list])

#GET BY ID
@instructors_blueprint.route('/instructors/<int:id>', methods=['GET'])
def GetInstructorById(id):
    instructor = Instructors.query.get_or_404(id)
    return jsonify(instructor.to_dict())

#POST
@instructors_blueprint.route('/instructors', methods=['POST'])
def Create():
    x = request.json
    # Hash the password before storing
    hashed_password = generate_password_hash(x['password'])
    data = Instructors(username=x['username'], password=hashed_password, first_name=x['first_name'], last_name=x['last_name'])
    #ARRAY OF BOOLS TO STORE VALUES FROM EACH USERNAME CHECK
    repeatedUser = checkUniqueness(data.username)
    if not repeatedUser:
        db.session.add(data)
        db.session.commit()
        return jsonify(data.to_dict())
    else:
        return {'message': "username already exists"}

#PUT
@instructors_blueprint.route('/instructors/<int:id>', methods=['PUT'])
def Change(id):
    updateData = Instructors.query.get_or_404(id)
    x = request.json
    #OVERWRITE DATA
    if 'username' in x:
        updateData.username = x['username']
    if 'password' in x:
        # Hash the password if it's being updated
        updateData.password = generate_password_hash(x['password'])
    #ARRAY OF BOOLS TO STORE VALUES FROM EACH USERNAME CHECK
    repeatedUser = checkUniqueness(updateData.username)
    if not repeatedUser:
        db.session.commit()
        return jsonify(updateData.to_dict())
    else:
        return {'message': "username already exists"}
    

#ADD INSTRUCTOR TO COURSE
@instructors_blueprint.route('/instructors/<int:id>/courses/<string:unique_id>', methods=['PUT'])
def AddStudentToCourse(id, unique_id):
    instructor = Instructors.query.get_or_404(id)
    if unique_id in instructor.assigned_courses:
        return jsonify({'message': 'Instructor is already teaching this course'})
    else:
        instructor.assigned_courses.append(unique_id)
        db.session.commit()
        name = instructor.first_name + " " + instructor.last_name
        addInstructor(unique_id, name)
        print({'message': 'Instructor is assigned to course'})
        return jsonify(instructor.to_dict())

#REMOVE INSTRUCTOR FROM COURSE
@instructors_blueprint.route('/instructors/<int:id>/courses/<string:unique_id>', methods=['DELETE'])
def RemoveStudentFromCourse(id, unique_id):
    instructor = Instructors.query.get_or_404(id)
    if unique_id in instructor.assigned_courses:
        instructor.assigned_courses.remove(unique_id)
        db.session.commit()
        name = instructor.first_name + " " + instructor.last_name
        removeInstructor(unique_id, name)
        return jsonify(instructor.to_dict())
    else:
        return jsonify({'message': 'Instructor is not teaching course'})

#DELETE INSTRUCTOR
@instructors_blueprint.route('/instructors/<int:id>', methods=['DELETE'])
def Delete(id):
    remove = Instructors.query.get_or_404(id)
    db.session.delete(remove)
    db.session.commit()
    return jsonify({'message': 'deleted'})
