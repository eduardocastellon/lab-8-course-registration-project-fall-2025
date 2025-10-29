from flask import Flask, request, redirect, jsonify, Blueprint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import JSON
from sqlalchemy.ext.mutable import MutableList
from database import db
from vars.port import port_number
import requests

instructors_blueprint = Blueprint('instructors', __name__)

class Instructors(db.Model):
    id = db.Column(db.Integer, primary_key=True) #INT FOR ID
    username = db.Column(db.String(50), nullable=False) #USERNAME FOR INSTRUCTOR
    password = db.Column(db.String(50), nullable=False) #PASSWORD FOR INSTRUCTOR
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
    data = Instructors(username=x['username'], password=x['password'], first_name=x['first_name'], last_name=x['last_name'])
    repeatedUser = db.session.query(Instructors.query.filter_by(username=data.username).exists()).scalar()
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
    #CHECK IF USERNAME IS ALREADY EXISTS
    repeatedUser = db.session.query(Instructors.query.filter_by(username=updateData.username).exists()).scalar()
    if not repeatedUser:
        updateData.username = x.get('username', updateData.username)
        updateData.password = x.get('password', updateData.password)
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
        requests.put(f"http://localhost:{port_number}/courses/{unique_id}/instructor/{name}")
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
        requests.delete(f"http://localhost:{port_number}/courses/{unique_id}/instructor/{name}")
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
