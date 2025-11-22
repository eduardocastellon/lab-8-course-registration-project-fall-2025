from flask import Flask, request, redirect, jsonify, Blueprint
from sqlalchemy.types import JSON
from vars.database import db
import random
import string


courses_blueprint = Blueprint('courses', __name__)

#GENERATE RANDOM 5 PLACE ASCII UNIQUE ID PER EACH COURSE //USE CASE: DUPLICATE COURSES WITH SAME NAME, DIFFERENT INSTRUCTOR
def GenerateUniqueID():
    while(1):
        uniqueID = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))
        isUnique = db.session.query(Courses.query.filter_by(unique_id=uniqueID).exists()).scalar()
        if not isUnique:
            break
    return uniqueID

#COURSES CLASS
class Courses(db.Model):
    id = db.Column(db.Integer, primary_key=True) #INT FOR ID
    unique_id = db.Column(db.String(5), nullable=False, default=GenerateUniqueID)
    course_id = db.Column(db.String(10), nullable=False) #COURSE ID
    course_name = db.Column(db.String(100), nullable=False) #COURSE NAME
    subject = db.Column(db.String(50), nullable=False) #SUBJECT
    instructor = db.Column(db.String(50), nullable=False, default="TBD") #ASSIGNED INSTRUCTOR
    dates = db.Column(JSON, nullable=False) #DAYS OF INSTRUCTION
    time = db.Column(db.String(50), nullable=False) #TIMES OF INSTRUCTION
    start_date = db.Column(db.String(50), nullable=True) #START DATE (MM/DD/YYYY)
    end_date = db.Column(db.String(50), nullable=True) #END DATE (MM/DD/YYYY)
    registered_students = db.Column(db.Integer, nullable=False, default=0) #AMOUNT OF STUNDENTS REGISTERED
    capacity = db.Column(db.Integer, nullable=False) #CLASS SIZE
    description = db.Column(db.String(500), nullable=False) #COURSE DESCRIPTION

    def to_dict(self):
        return {"id": self.id, "unique_id": self.unique_id, "course_id": self.course_id, "course_name": self.course_name, "subject": self.subject, "instructor": self.instructor, "dates": self.dates, "time": self.time, "start_date": self.start_date, "end_date": self.end_date, "registered_students": self.registered_students, "capacity": self.capacity, "description": self.description}
    

#GET
@courses_blueprint.route('/courses', methods=['GET'])
def GetCourses():
    list = Courses.query.all()
    return jsonify([i.to_dict() for i in list])

@courses_blueprint.route('/courses/<int:id>', methods=['GET'])
def GetCourseById(id):
    list = Courses.query.get_or_404(id)
    return jsonify(list.to_dict())

#POST
@courses_blueprint.route('/courses', methods=['POST'])
def Create():
    x = request.json
    data = Courses(
        unique_id=GenerateUniqueID(), 
        course_id=x['course_id'], 
        course_name=x['course_name'], 
        subject=x['subject'], 
        dates=x['dates'], 
        time=x['time'], 
        start_date=x.get('start_date'),
        end_date=x.get('end_date'),
        capacity=x['capacity'], 
        description=x['description']
    )
    db.session.add(data)
    db.session.commit()
    return jsonify(data.to_dict())

#PUT
@courses_blueprint.route('/courses/<int:id>', methods=['PUT'])
def Change(id):
    updateData = Courses.query.get_or_404(id)
    x = request.json
    #OVERWRITE DATA
    updateData.instructor = x.get('instructor', updateData.instructor)
    updateData.course_id = x.get('course_id', updateData.course_id)
    updateData.course_name = x.get('course_name', updateData.course_name)
    updateData.dates = x.get('dates', updateData.dates)
    updateData.time = x.get('time', updateData.time)
    updateData.start_date = x.get('start_date', updateData.start_date)
    updateData.end_date = x.get('end_date', updateData.end_date)
    updateData.capacity = x.get('capacity', updateData.capacity)
    updateData.description = x.get('description', updateData.description)

    db.session.commit()
    return jsonify(updateData.to_dict())

#INCREASE THE AMOUNT OF REGISTERED STUDENTS
@courses_blueprint.route('/courses/<string:uid>/size', methods=['PUT'])
def updateClassSizeUp(uid):
    course = Courses.query.filter_by(unique_id=uid).first_or_404()
    course.registered_students += 1
    db.session.commit()
    course.to_dict()
    return jsonify({'message': 'Class size has increased'})

#DECREASE THE AMOUNT OF REGISTERED STUDENTS
@courses_blueprint.route('/courses/<string:uid>/size', methods=['DELETE'])
def updateClassSizeDown(uid):
    course = Courses.query.filter_by(unique_id=uid).first_or_404()
    course.registered_students -= 1
    db.session.commit()
    return jsonify({'message': 'Class size has decreased'})

#ASSIGN COURSE TO INSTRUCTOR
@courses_blueprint.route('/courses/<string:uid>/instructor/<string:name>', methods=['PUT'])
def addInstructor(uid, name):
    course = Courses.query.filter_by(unique_id=uid).first_or_404()
    if (course.instructor == "TBD"):
        course.instructor =  name
        db.session.commit()
        course.to_dict()
        return jsonify({'message': f'{name} is now teaching the class'})
    else:
        return jsonify({'message': f'{course.instructor} is already teaching the class. Remove this instructor first before adding a new one'})

#REMOVE INSTRUCTOR FROM COURSE
@courses_blueprint.route('/courses/<string:uid>/instructor/<string:name>', methods=['DELETE'])
def removeInstructor(uid, name):
    course = Courses.query.filter_by(unique_id=uid).first_or_404()
    existingName = course.instructor
    if (existingName == name):
        course.instructor = "TBD"
        db.session.commit()
        return jsonify({'message': f'{name} is no longer teaching this course'})
    else:
        return jsonify({'message': f'Error: {name} cannot be removed since {name} was never teaching this course to begin with'})

#DELETE COURSE
@courses_blueprint.route('/courses/<int:id>', methods=['DELETE'])
def Delete(id):
    remove = Courses.query.get_or_404(id)
    db.session.delete(remove)
    db.session.commit()
    return jsonify({'message': 'Course deleted'})