from flask import Flask, request, redirect, jsonify, Blueprint, render_template, url_for
from flask_cors import CORS
from vars.database import db
from vars.port import port_number
from routes.courses import courses_blueprint, Courses
from routes.students import students_blueprint, Students
from routes.instructors import instructors_blueprint, Instructors
from routes.admin import admin_blueprint, Admin as AdminUser
from routes.login import login_blueprint

from flask_admin import Admin as FlaskAdmin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)

#avoids error
app.secret_key = 'super secret key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///records.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
CORS(app)

admin_ui = FlaskAdmin(
    app,
    name="Cool University Admin",
    url="/admin",
)
admin_ui.add_view(ModelView(Students, db.session, endpoint="students_admin"))
admin_ui.add_view(ModelView(Courses, db.session, endpoint="courses_admin"))
admin_ui.add_view(ModelView(Instructors, db.session, endpoint="instructors_admin"))
admin_ui.add_view(ModelView(AdminUser, db.session, endpoint="admin_user"))

#render login page
@app.route("/", methods=["GET"])
def index():
    return render_template("login.html")

@app.route("/student")
def student_dashboard():
    return render_template("student.html")

@app.route("/instructor")
def instructor_dashboard():
    return render_template("instructor.html")

@app.route("/instructor/course/<string:uid>")
def instructor_course(uid):
    return render_template("instructor_class.html", course_uid=uid)

###############################################################
#           PATHS
###############################################################
#http://localhost:{port_number}/students
#http://localhost:{port_number}/instructors
#http://localhost:{port_number}/courses
#http://localhost:{port_number}/admin

app.register_blueprint(login_blueprint)
app.register_blueprint(courses_blueprint)
app.register_blueprint(students_blueprint)
app.register_blueprint(instructors_blueprint)
app.register_blueprint(admin_blueprint, url_prefix="/api")

#CREATE DATABASE FILE AND COLUMNS
# with app.app_context():
#     db.create_all()

if __name__ == "__main__":
    app.run(port=port_number, debug=True)
