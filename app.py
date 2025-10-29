from flask import Flask, request, redirect, jsonify, Blueprint
from flask_cors import CORS
from database import db
from vars.port import port_number
from routes.courses import courses_blueprint
from routes.students import students_blueprint
from routes.instructors import instructors_blueprint
from routes.admin import admin_blueprint


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///records.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
CORS(app)

###############################################################
#           PATHS
###############################################################
#http://localhost:{port_number}/students
#http://localhost:{port_number}/instructors
#http://localhost:{port_number}/courses
#http://localhost:{port_number}/admin

app.register_blueprint(courses_blueprint)
app.register_blueprint(students_blueprint)
app.register_blueprint(instructors_blueprint)
app.register_blueprint(admin_blueprint)

#CREATE DATABASE FILE AND COLUMNS
# with app.app_context():
#     db.create_all()

if __name__ == "__main__":
    app.run(port=port_number, debug=True)
