# Changelog - Course Registration System

## Summary of All Changes Made

This document lists all the changes and enhancements made to the Course Registration System.

---

## 🔐 1. Password Hashing & Security

### What Changed:
- **All passwords are now securely hashed** using Werkzeug's password hashing (scrypt/pbkdf2:sha256)
- Passwords are never stored in plain text
- Backward compatible: existing plain-text passwords auto-upgrade on first login

### Files Modified:
- `routes/utils/functions.py` - Updated `LoginCheck()` function
- `routes/students.py` - Added password hashing on create/update
- `routes/instructors.py` - Added password hashing on create/update
- `routes/admin.py` - Added password hashing on create/update

### Key Changes:
```python
# Before: Plain text storage
password = request.json['password']

# After: Hashed storage
hashed_password = generate_password_hash(request.json['password'])
password = hashed_password
```

### Bug Fix:
- Fixed issue where `scrypt:` hashes weren't recognized (only checked for `pbkdf2:sha256:`)
- Now properly recognizes both hash formats and doesn't re-hash already hashed passwords

---

## ✅ 2. Course Capacity Checking

### What Changed:
- **Backend validation** prevents registration when course is at full capacity
- Returns clear error messages: "Course is at full capacity"
- Prevents race conditions by checking capacity at registration time

### Files Modified:
- `routes/utils/functions.py` - Added `checkCourseCapacity()` function
- `routes/students.py` - Integrated capacity check in `AddStudentToCourse()`

### Implementation:
```python
# Before: No capacity check
student.registered_courses.update({unique_id: 0})

# After: Capacity validation
has_capacity, message = checkCourseCapacity(unique_id)
if not has_capacity:
    return jsonify({'message': message}), 400
```

---

## 📅 3. Schedule Conflict Detection

### What Changed:
- **Intelligent schedule conflict detection** prevents overlapping course registrations
- Checks for:
  - Same days of the week (Mon-Fri)
  - Overlapping time ranges (e.g., 5:00PM-7:15PM conflicts with 6:00PM-8:00PM)
- Returns specific error messages indicating which course conflicts

### Files Modified:
- `routes/utils/functions.py` - Added `checkScheduleConflict()` and `times_overlap()` functions
- `routes/students.py` - Integrated conflict check in course registration

### Implementation:
```python
# Checks if new course conflicts with existing courses
no_conflict, message = checkScheduleConflict(student_id, new_course_unique_id)
if not no_conflict:
    return jsonify({'message': message}), 400
```

### Example:
- Student registered in: "CSE108" on "T Th" at "5:00PM-7:15PM"
- Trying to register: "MATH101" on "T Th" at "6:00PM-8:00PM"
- Result: ❌ "Schedule conflict with CSE108 (CSE108)"

---

## 🗑️ 4. Drop Course Functionality

### What Changed:
- **Drop course button** (red "−" icon) added to student's "Your Courses" table
- Confirmation dialog before dropping
- Properly updates course enrollment counts
- Backend DELETE route already existed and works correctly

### Files Modified:
- `static/student.js` - Added `dropCourse()` function and UI button
- `templates/student.html` - Added "Drop" column header

### Implementation:
```javascript
// User clicks drop button → Confirmation → DELETE request
async function dropCourse(uniqueId) {
    const res = await fetch(`/students/${studentId}/courses/${uniqueId}`, {
        method: "DELETE"
    });
    // Updates enrollment count automatically
}
```

---

## 📆 5. Enhanced Days & Dates Display

### What Changed:
- Added `start_date` and `end_date` fields to Courses model
- Days of week displayed clearly: **M T W Th F** (bold, larger text)
- Start and end dates shown: `Start: 01/15/2025 | End: 05/15/2025` (blue text)
- Improved visual hierarchy and readability

### Files Modified:
- `routes/courses.py` - Added `start_date` and `end_date` columns to Courses model
- `static/student.js` - Added `formatDays()` and `formatDateRange()` functions
- `static/instructor.js` - Same formatting functions
- `templates/student.html` - Updated column header to "Days / Dates"
- `templates/instructor.html` - Updated column header

### Database Changes:
- Added `start_date VARCHAR(50)` column
- Added `end_date VARCHAR(50)` column
- Migration executed automatically

### Display Format:
```
Days / Dates Column:
┌─────────────────────────┐
│ M T W Th F              │  ← Bold, larger text
│ Start: 01/15/2025       │  ← Blue, medium text
│ End: 05/15/2025         │
└─────────────────────────┘
```

---

## 📁 6. New Files Created

### Documentation:
- `PROJECT_DOCUMENTATION.md` - Comprehensive project documentation
- `CHANGELOG.md` - This file (summary of changes)
- `requirements.txt` - Python dependencies list
- `.gitignore` - Git ignore file for Python projects

### Configuration:
- `.gitignore` - Excludes `__pycache__`, `.DS_Store`, database files, etc.

---

## 🔧 7. Bug Fixes

### Password Hashing Recognition:
- **Fixed**: Code now recognizes both `scrypt:` and `pbkdf2:sha256:` hash formats
- **Fixed**: Passwords are no longer re-hashed if already hashed
- **Result**: Login works correctly without modifying existing hashed passwords

### Database Schema:
- **Fixed**: Added missing `start_date` and `end_date` columns to existing database
- **Fixed**: Migration script executed to update schema

---

## 📊 Summary Statistics

### Files Modified: 10
- `routes/utils/functions.py`
- `routes/students.py`
- `routes/instructors.py`
- `routes/admin.py`
- `routes/courses.py`
- `static/student.js`
- `static/instructor.js`
- `templates/student.html`
- `templates/instructor.html`

### Files Created: 4
- `PROJECT_DOCUMENTATION.md`
- `CHANGELOG.md`
- `requirements.txt`
- `.gitignore`

### Features Added: 5
1. ✅ Password Hashing & Security
2. ✅ Course Capacity Checking
3. ✅ Schedule Conflict Detection
4. ✅ Drop Course Functionality
5. ✅ Enhanced Days & Dates Display

### Bug Fixes: 2
1. ✅ Password hash format recognition
2. ✅ Database schema migration

---

## 🎯 Before vs After

### Before:
- ❌ Passwords stored in plain text
- ❌ No capacity checking
- ❌ No schedule conflict detection
- ❌ No way to drop courses from UI
- ❌ Only time displayed, no days or dates
- ❌ Basic error messages

### After:
- ✅ Passwords securely hashed
- ✅ Capacity validation on registration
- ✅ Intelligent schedule conflict detection
- ✅ Drop course button with confirmation
- ✅ Clear days and dates display
- ✅ Detailed error messages

---

## 🚀 Testing

All features have been tested and verified:
- ✅ Password hashing works correctly
- ✅ Capacity checking prevents over-enrollment
- ✅ Schedule conflicts are detected
- ✅ Drop course updates enrollment counts
- ✅ Days and dates display correctly
- ✅ All existing credentials still work

---

## 📝 Notes

- All changes are backward compatible
- Existing users can still login with their original passwords
- Database migrations are automatic
- No breaking changes to API endpoints

---

**Last Updated**: January 2025  
**Version**: 2.0 (Enhanced)

