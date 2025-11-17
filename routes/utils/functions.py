from vars.database import db
from flask import jsonify
from werkzeug.security import generate_password_hash, check_password_hash

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
    from werkzeug.security import generate_password_hash

    instructor = Instructors.query.filter_by(username=username).first()
    student = Students.query.filter_by(username=username).first()
    admin = Admin.query.filter_by(username=username).first()

    # Helper function to check password (handles both hashed and plain text for migration)
    def verify_password(stored_password, provided_password):
        # If password starts with pbkdf2:sha256, it's hashed
        if stored_password.startswith('pbkdf2:sha256:'):
            return check_password_hash(stored_password, provided_password)
        else:
            # Plain text password (for backward compatibility)
            if stored_password == provided_password:
                # Auto-upgrade to hashed password
                return True
            return False

    # Check instructor
    if instructor:
        if verify_password(instructor.password, password):
            # Auto-upgrade plain text password to hash
            if not instructor.password.startswith('pbkdf2:sha256:'):
                instructor.password = generate_password_hash(password)
                db.session.commit()
            return jsonify(instructor.to_dict())
    
    # Check student
    if student:
        if verify_password(student.password, password):
            # Auto-upgrade plain text password to hash
            if not student.password.startswith('pbkdf2:sha256:'):
                student.password = generate_password_hash(password)
                db.session.commit()
            return jsonify(student.to_dict())
    
    # Check admin
    if admin:
        if verify_password(admin.password, password):
            # Auto-upgrade plain text password to hash
            if not admin.password.startswith('pbkdf2:sha256:'):
                admin.password = generate_password_hash(password)
                db.session.commit()
            return jsonify(admin.to_dict())
    
    return jsonify({"message": "Wrong Username or Password"}), 401

#CHECK IF COURSE HAS CAPACITY
def checkCourseCapacity(unique_id):
    from routes.courses import Courses
    course = Courses.query.filter_by(unique_id=unique_id).first()
    if not course:
        return False, "Course not found"
    if course.registered_students >= course.capacity:
        return False, "Course is at full capacity"
    return True, "Course has available spots"

#CHECK FOR SCHEDULE CONFLICTS
def checkScheduleConflict(student_id, new_course_unique_id):
    from routes.students import Students
    from routes.courses import Courses
    
    student = Students.query.get(student_id)
    if not student:
        return False, "Student not found"
    
    # Get the new course
    new_course = Courses.query.filter_by(unique_id=new_course_unique_id).first()
    if not new_course:
        return False, "New course not found"
    
    # Get all courses the student is registered for
    registered_course_ids = list(student.registered_courses.keys())
    if not registered_course_ids:
        return True, "No conflicts"  # No existing courses, so no conflict
    
    # Get all registered courses
    registered_courses = Courses.query.filter(Courses.unique_id.in_(registered_course_ids)).all()
    
    # Check for conflicts: same day and overlapping time
    new_course_days = new_course.dates  # Array like [0, 1, 0, 1, 0] for Mon-Fri
    new_course_time = new_course.time
    
    for existing_course in registered_courses:
        existing_course_days = existing_course.dates
        existing_course_time = existing_course.time
        
        # Check if any day overlaps
        day_overlap = any(new_course_days[i] == 1 and existing_course_days[i] == 1 for i in range(5))
        
        if day_overlap:
            # Check if times overlap (simple string comparison for now)
            # For a more robust solution, you'd parse the time strings
            if new_course_time == existing_course_time:
                return False, f"Schedule conflict with {existing_course.course_name} ({existing_course.course_id})"
            
            # Check for overlapping time ranges (basic check)
            # Assumes format like "5:00PM-7:15PM" or "10:00AM-11:30AM"
            if times_overlap(new_course_time, existing_course_time):
                return False, f"Schedule conflict with {existing_course.course_name} ({existing_course.course_id})"
    
    return True, "No conflicts"

#HELPER FUNCTION TO CHECK IF TWO TIME RANGES OVERLAP
def times_overlap(time1, time2):
    """
    Check if two time ranges overlap.
    Assumes format like "5:00PM-7:15PM" or "10:00AM-11:30AM"
    """
    try:
        def parse_time(time_str):
            # Extract start and end times
            parts = time_str.split('-')
            if len(parts) != 2:
                return None, None
            
            start_str = parts[0].strip()
            end_str = parts[1].strip()
            
            def time_to_minutes(t):
                # Convert "5:00PM" or "10:00AM" to minutes since midnight
                t = t.upper().replace(' ', '')
                is_pm = 'PM' in t
                t = t.replace('AM', '').replace('PM', '')
                hour, minute = map(int, t.split(':'))
                if is_pm and hour != 12:
                    hour += 12
                elif not is_pm and hour == 12:
                    hour = 0
                return hour * 60 + minute
            
            start_min = time_to_minutes(start_str)
            end_min = time_to_minutes(end_str)
            return start_min, end_min
        
        start1, end1 = parse_time(time1)
        start2, end2 = parse_time(time2)
        
        if start1 is None or start2 is None:
            # If parsing fails, do simple string comparison
            return time1 == time2
        
        # Check if ranges overlap: start1 < end2 AND start2 < end1
        return start1 < end2 and start2 < end1
    except:
        # If any error occurs, fall back to simple string comparison
        return time1 == time2