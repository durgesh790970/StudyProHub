"""
QUICK REFERENCE GUIDE - SQLite Database Functions
Fast lookup for all database operations

Use this as a quick cheat sheet for common operations.
"""

# ============================================================================
# IMPORT STATEMENTS
# ============================================================================

# Import what you need at the top of your file:
from db import (
    initialize_db,              # Initialize database (one-time)
    
    # Student operations
    add_student,                # Add new student
    get_student,                # Get one student
    get_all_students,           # Get all students
    update_student,             # Update student info
    delete_student,             # Delete student
    
    # Course operations
    add_course,                 # Add new course
    get_course,                 # Get one course
    get_all_courses,            # Get all courses
    
    # Enrollment operations
    enroll_student,             # Enroll in course
    get_student_courses,        # Get student's courses
    update_grade,               # Update course grade
    
    # Submission operations
    add_submission,             # Record submission
    get_student_submissions,    # Get submissions
    get_submission,             # Get one submission
    
    # Utility
    get_student_statistics,     # Get stats for student
)


# ============================================================================
# INITIALIZATION
# ============================================================================

# Initialize database (call once at startup)
initialize_db()


# ============================================================================
# STUDENT OPERATIONS
# ============================================================================

# CREATE: Add a new student
student_id = add_student(
    name='John Doe',              # Required
    email='john@example.com',     # Required, must be unique
    cgpa=9.5,                     # Optional (default: 0.0)
    phone='9876543210'            # Optional
)

# READ: Get one student
student = get_student(1)
if student:
    print(f"Name: {student['name']}")
    print(f"Email: {student['email']}")
    print(f"CGPA: {student['cgpa']}")
    print(f"Phone: {student['phone']}")
    print(f"Status: {student['status']}")
    print(f"Enrolled: {student['enrollment_date']}")

# READ: Get all students
all_students = get_all_students()
for student in all_students:
    print(f"{student['name']} - {student['email']} - CGPA: {student['cgpa']}")

# UPDATE: Modify student info
update_student(
    student_id=1,
    name='John Doe',              # Optional
    email='john.doe@example.com', # Optional
    cgpa=9.8,                     # Optional
    phone='9876543211',           # Optional
    status='inactive'             # Optional
)

# DELETE: Remove student (cascades to enrollments and submissions)
success = delete_student(1)
if success:
    print("Student deleted")


# ============================================================================
# COURSE OPERATIONS
# ============================================================================

# CREATE: Add a new course
course_id = add_course(
    course_code='CS101',          # Required, unique
    course_name='Data Structures',# Required
    credits=3,                    # Optional (default: 3)
    semester=1                    # Optional (default: 1)
)

# READ: Get one course
course = get_course(1)
if course:
    print(f"Code: {course['course_code']}")
    print(f"Name: {course['course_name']}")
    print(f"Credits: {course['credits']}")
    print(f"Semester: {course['semester']}")

# READ: Get all courses
all_courses = get_all_courses()
for course in all_courses:
    print(f"{course['course_code']} - {course['course_name']}")


# ============================================================================
# ENROLLMENT OPERATIONS
# ============================================================================

# CREATE: Enroll student in course
enrollment_id = enroll_student(
    student_id=1,
    course_id=5
)

# READ: Get all courses for a student
courses = get_student_courses(student_id=1)
for course in courses:
    print(f"{course['course_name']}")
    print(f"Grade: {course['grade']}")
    print(f"Enrolled: {course['enrollment_date']}")

# UPDATE: Assign grade
update_grade(
    student_id=1,
    course_id=5,
    grade='A+'  # Possible values: A+, A, B+, B, C+, C, D, F
)


# ============================================================================
# SUBMISSION OPERATIONS
# ============================================================================

# CREATE: Record a submission
submission_id = add_submission(
    student_id=1,
    course_id=5,
    assignment_name='Assignment 1',  # Required
    marks_obtained=85,               # Required
    total_marks=100                  # Optional (default: 100)
)

# READ: Get all submissions for a student
submissions = get_student_submissions(student_id=1)
for sub in submissions:
    print(f"Assignment: {sub['assignment_name']}")
    print(f"Marks: {sub['marks_obtained']}/{sub['total_marks']}")
    print(f"Date: {sub['submission_date']}")

# READ: Get submissions for a specific course
submissions = get_student_submissions(
    student_id=1,
    course_id=5
)

# READ: Get one submission
submission = get_submission(submission_id=1)
if submission:
    print(f"Assignment: {submission['assignment_name']}")
    print(f"Marks: {submission['marks_obtained']}/{submission['total_marks']}")


# ============================================================================
# STATISTICS & REPORTS
# ============================================================================

# Get comprehensive statistics for a student
stats = get_student_statistics(student_id=1)
print(f"Name: {stats['student_name']}")
print(f"Email: {stats['student_email']}")
print(f"Total Courses: {stats['total_courses']}")
print(f"CGPA: {stats['current_cgpa']}")
print(f"Average Score: {stats['average_score']:.2f}%")
print(f"Status: {stats['status']}")


# ============================================================================
# COMMON WORKFLOWS
# ============================================================================

# WORKFLOW 1: Register new student and enroll in courses
print("\n=== WORKFLOW 1: Register & Enroll ===")
student_id = add_student('Alice Kumar', 'alice@example.com', 9.3)
enroll_student(student_id, 1)  # Enroll in course 1
enroll_student(student_id, 2)  # Enroll in course 2

# WORKFLOW 2: Record assignment and give grade
print("\n=== WORKFLOW 2: Assignment & Grading ===")
add_submission(student_id, 1, 'Assignment 1', 92, 100)
update_grade(student_id, 1, 'A+')

# WORKFLOW 3: View complete student profile
print("\n=== WORKFLOW 3: Student Profile ===")
student = get_student(student_id)
print(f"Student: {student['name']}")
print(f"CGPA: {student['cgpa']}")

courses = get_student_courses(student_id)
print(f"Enrolled in {len(courses)} courses:")
for course in courses:
    print(f"  - {course['course_name']} (Grade: {course['grade']})")

submissions = get_student_submissions(student_id)
print(f"Submissions: {len(submissions)}")

stats = get_student_statistics(student_id)
print(f"Average Score: {stats['average_score']:.2f}%")


# ============================================================================
# ERROR HANDLING
# ============================================================================

import sqlite3

# Safe database operation
try:
    student_id = add_student('John', 'john@example.com', 9.5)
    print(f"✓ Student created: {student_id}")
    
except sqlite3.IntegrityError as e:
    print(f"✗ Data error: {e}")
    print("  (Email might already exist)")
    
except sqlite3.Error as e:
    print(f"✗ Database error: {e}")
    
except Exception as e:
    print(f"✗ Unexpected error: {e}")


# ============================================================================
# RETURN VALUES & TYPES
# ============================================================================

# Functions that return IDs (int)
student_id: int = add_student(...)
course_id: int = add_course(...)
enrollment_id: int = enroll_student(...)
submission_id: int = add_submission(...)

# Functions that return single record (dict or None)
student: dict = get_student(1)
course: dict = get_course(1)
submission: dict = get_submission(1)

# Functions that return lists (list[dict])
students: list = get_all_students()
courses: list = get_all_courses()
enrollments: list = get_student_courses(1)
submissions: list = get_student_submissions(1)

# Functions that return boolean (bool)
success: bool = update_student(1, cgpa=9.8)
success: bool = delete_student(1)
success: bool = update_grade(1, 5, 'A+')

# Functions that return statistics (dict)
stats: dict = get_student_statistics(1)


# ============================================================================
# DATA TYPES IN DATABASE
# ============================================================================

# String fields (TEXT)
name: str
email: str
phone: str
course_code: str
course_name: str
assignment_name: str
grade: str
status: str

# Numeric fields (INTEGER)
id: int
credits: int
semester: int
marks_obtained: float
total_marks: float
cgpa: float

# Date/Time fields (TIMESTAMP)
enrollment_date: str  # "2024-02-01 10:30:45"
created_date: str
submission_date: str


# ============================================================================
# FIELD CONSTRAINTS
# ============================================================================

# Students.email - UNIQUE (no duplicates)
# Students.id - PRIMARY KEY (auto-increment)
# Courses.course_code - UNIQUE
# Courses.id - PRIMARY KEY
# Enrollments.student_id, course_id - UNIQUE combination
# All IDs - AUTO-INCREMENT (don't pass when creating)


# ============================================================================
# EXAMPLES FOR COLLEGE PROJECT
# ============================================================================

# Example 1: Simple student lookup and display
from db import get_student

def display_student_info(student_id):
    """Display student information nicely"""
    student = get_student(student_id)
    if not student:
        print(f"Student {student_id} not found")
        return
    
    print(f"""
    Student Information
    ====================
    Name: {student['name']}
    Email: {student['email']}
    CGPA: {student['cgpa']:.2f}
    Status: {student['status']}
    """)

# Example 2: List students by CGPA
from db import get_all_students

def list_toppers(min_cgpa=9.0):
    """List all students with CGPA above minimum"""
    students = get_all_students()
    toppers = [s for s in students if s['cgpa'] >= min_cgpa]
    
    for student in toppers:
        print(f"{student['name']}: {student['cgpa']}")

# Example 3: Check course load
from db import get_student_courses

def student_course_load(student_id):
    """Check total credits for a student"""
    courses = get_student_courses(student_id)
    total_credits = sum(c['credits'] for c in courses)
    return total_credits

# Example 4: Average score in a course
from db import get_student_submissions

def average_assignment_score(student_id, course_id):
    """Calculate average submission score"""
    submissions = get_student_submissions(student_id, course_id)
    
    if not submissions:
        return 0
    
    scores = [
        (s['marks_obtained'] / s['total_marks'] * 100)
        for s in submissions
    ]
    
    return sum(scores) / len(scores)


# ============================================================================
# TIPS & TRICKS
# ============================================================================

# Tip 1: Always check if record exists before using
if student := get_student(1):  # Python 3.8+ walrus operator
    print(student['name'])

# Tip 2: Use list comprehension for filtering
students = get_all_students()
active_students = [s for s in students if s['status'] == 'active']

# Tip 3: Batch operations
courses = [
    ('CS101', 'Data Structures', 3, 1),
    ('CS102', 'Algorithms', 3, 1),
    ('CS201', 'Databases', 4, 2),
]
for code, name, credits, semester in courses:
    add_course(code, name, credits, semester)

# Tip 4: Use f-strings for display
student = get_student(1)
print(f"{student['name']} ({student['email']}) - CGPA: {student['cgpa']:.2f}")

# Tip 5: Handle exceptions appropriately
try:
    add_student('John', 'john@example.com')
except sqlite3.IntegrityError:
    print("Email already exists - skipping")


# ============================================================================
# KEY POINTS
# ============================================================================

"""
✓ Always call initialize_db() once at startup
✓ Always close connections (our functions handle this)
✓ Check if record exists before using it
✓ Use our functions, don't access database directly
✓ Handle exceptions in try-except blocks
✓ Use meaningful variable names
✓ Comment your code
✓ Test with sample data before production

Remember:
- Tables: students, courses, enrollments, submissions
- Unique fields: students.email, courses.course_code
- Foreign keys: student_id and course_id in enrollments/submissions
- Auto-increment: All IDs (don't pass when creating)
"""
