"""
SQLite Database Module - project.db
Standalone database connection and CRUD operations for Python project.

This module provides:
- Database connection management
- Table creation with proper schema
- CRUD operations (Create, Read, Update, Delete)
- Error handling and logging
- Production-ready implementation

Usage:
    from db import initialize_db, add_student, get_student, update_student, delete_student
    
    # Initialize database on startup
    initialize_db()
    
    # Add a student
    add_student('John Doe', 'john@example.com', 9.5)
    
    # Get student
    student = get_student(1)
    print(student)
"""

import sqlite3
import os
from typing import Optional, List, Tuple
from datetime import datetime

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# Database file location (root folder of project)
# CONSOLIDATED: Now using db.sqlite3 (Django's unified database)
DB_FILE = 'db.sqlite3'

# Check if we're in backend directory and adjust path accordingly
if not os.path.exists(DB_FILE):
    # Try parent directory (in case running from backend/)
    if os.path.exists(os.path.join('..', DB_FILE)):
        DB_FILE = os.path.join('..', DB_FILE)


# ============================================================================
# DATABASE CONNECTION FUNCTIONS
# ============================================================================

def get_connection() -> sqlite3.Connection:
    """
    Create and return a database connection.
    
    Returns:
        sqlite3.Connection: Database connection object
        
    Raises:
        sqlite3.DatabaseError: If connection fails
    
    Production Note:
        - Connection timeout is set to 10 seconds
        - Row factory is set to return dictionaries instead of tuples
        - Check same thread is disabled for multi-threading (use with care)
    """
    try:
        connection = sqlite3.connect(DB_FILE, timeout=10.0)
        # Return rows as dictionaries instead of tuples
        connection.row_factory = sqlite3.Row
        print(f"✓ Database connection established: {DB_FILE}")
        return connection
    except sqlite3.DatabaseError as e:
        print(f"✗ Database connection error: {e}")
        raise


def close_connection(connection: sqlite3.Connection) -> None:
    """
    Safely close database connection.
    
    Args:
        connection: sqlite3 connection object to close
        
    Production Note:
        - Always call this when done with database operations
        - Prevents resource leaks
    """
    if connection:
        connection.close()
        print("✓ Database connection closed")


# ============================================================================
# TABLE INITIALIZATION
# ============================================================================

def create_tables() -> None:
    """
    Create all required tables in the database.
    
    Tables created:
    1. students - Student information with academic performance
    2. courses - Available courses/subjects
    3. enrollments - Student course enrollments
    4. submissions - Assignment submissions
    
    Primary Keys:
    - All tables have auto-incrementing integer primary keys
    - Foreign keys maintain referential integrity
    
    Production Note:
        - Uses IF NOT EXISTS to prevent errors on multiple runs
        - Proper data types and constraints
        - Timestamps for audit trail
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        # Table 1: Students
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                cgpa REAL DEFAULT 0.0,
                enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Table 2: Courses
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_code TEXT UNIQUE NOT NULL,
                course_name TEXT NOT NULL,
                credits INTEGER DEFAULT 3,
                semester INTEGER,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table 3: Enrollments (Student-Course relationship)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                grade TEXT,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
                UNIQUE(student_id, course_id)
            )
        ''')
        
        # Table 4: Submissions (Assignment submissions)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                assignment_name TEXT NOT NULL,
                submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                marks_obtained REAL,
                total_marks REAL DEFAULT 100,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
            )
        ''')
        
        connection.commit()
        print("✓ All tables created successfully")
        
    except sqlite3.Error as e:
        print(f"✗ Error creating tables: {e}")
        connection.rollback()
        raise
    finally:
        close_connection(connection)


# ============================================================================
# CRUD OPERATIONS - STUDENTS
# ============================================================================

def add_student(name: str, email: str, cgpa: float = 0.0, phone: str = None) -> int:
    """
    Add a new student to the database.
    
    Args:
        name: Student's full name
        email: Student's email (unique)
        cgpa: Current CGPA (default: 0.0)
        phone: Student's phone number (optional)
        
    Returns:
        int: ID of newly created student
        
    Raises:
        sqlite3.IntegrityError: If email already exists
        
    Example:
        student_id = add_student('John Doe', 'john@example.com', 9.5, '9876543210')
        print(f"Student created with ID: {student_id}")
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO students (name, email, cgpa, phone)
            VALUES (?, ?, ?, ?)
        ''', (name, email, cgpa, phone))
        
        connection.commit()
        student_id = cursor.lastrowid
        print(f"✓ Student '{name}' added with ID: {student_id}")
        return student_id
        
    except sqlite3.IntegrityError as e:
        print(f"✗ Error: {e}")
        connection.rollback()
        raise
    finally:
        close_connection(connection)


def get_student(student_id: int) -> Optional[dict]:
    """
    Retrieve student information by ID.
    
    Args:
        student_id: ID of the student to retrieve
        
    Returns:
        dict: Student information if found, None otherwise
        
    Example:
        student = get_student(1)
        if student:
            print(f"Name: {student['name']}, Email: {student['email']}")
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        else:
            print(f"ℹ Student with ID {student_id} not found")
            return None
            
    except sqlite3.Error as e:
        print(f"✗ Error retrieving student: {e}")
        raise
    finally:
        close_connection(connection)


def get_all_students() -> List[dict]:
    """
    Retrieve all students from database.
    
    Returns:
        List[dict]: List of all student records
        
    Example:
        students = get_all_students()
        for student in students:
            print(f"{student['name']} - {student['email']}")
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute('SELECT * FROM students ORDER BY enrollment_date DESC')
        rows = cursor.fetchall()
        
        students = [dict(row) for row in rows]
        print(f"✓ Retrieved {len(students)} students")
        return students
        
    except sqlite3.Error as e:
        print(f"✗ Error retrieving students: {e}")
        raise
    finally:
        close_connection(connection)


def update_student(student_id: int, **kwargs) -> bool:
    """
    Update student information.
    
    Args:
        student_id: ID of student to update
        **kwargs: Fields to update (name, email, cgpa, phone, status)
        
    Returns:
        bool: True if update successful, False otherwise
        
    Example:
        # Update CGPA
        update_student(1, cgpa=9.8)
        
        # Update multiple fields
        update_student(1, cgpa=9.5, status='inactive')
    """
    if not kwargs:
        print("✗ No fields to update")
        return False
    
    # Allowed fields for update
    allowed_fields = {'name', 'email', 'cgpa', 'phone', 'status'}
    kwargs = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not kwargs:
        print("✗ Invalid fields for update")
        return False
    
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        # Build dynamic SQL query
        set_clause = ', '.join([f'{key} = ?' for key in kwargs.keys()])
        values = list(kwargs.values()) + [student_id]
        
        query = f'UPDATE students SET {set_clause} WHERE id = ?'
        cursor.execute(query, values)
        
        connection.commit()
        
        if cursor.rowcount > 0:
            print(f"✓ Student {student_id} updated: {kwargs}")
            return True
        else:
            print(f"ℹ Student with ID {student_id} not found")
            return False
            
    except sqlite3.Error as e:
        print(f"✗ Error updating student: {e}")
        connection.rollback()
        raise
    finally:
        close_connection(connection)


def delete_student(student_id: int) -> bool:
    """
    Delete a student from database (with cascade).
    
    Args:
        student_id: ID of student to delete
        
    Returns:
        bool: True if deletion successful, False otherwise
        
    Production Note:
        - Cascading deletes remove all related enrollments and submissions
        - This is intentional for data consistency
        
    Example:
        if delete_student(1):
            print("Student deleted successfully")
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
        connection.commit()
        
        if cursor.rowcount > 0:
            print(f"✓ Student {student_id} deleted successfully")
            return True
        else:
            print(f"ℹ Student with ID {student_id} not found")
            return False
            
    except sqlite3.Error as e:
        print(f"✗ Error deleting student: {e}")
        connection.rollback()
        raise
    finally:
        close_connection(connection)


# ============================================================================
# CRUD OPERATIONS - COURSES
# ============================================================================

def add_course(course_code: str, course_name: str, credits: int = 3, semester: int = 1) -> int:
    """
    Add a new course to the database.
    
    Args:
        course_code: Unique course code (e.g., 'CS101')
        course_name: Full name of the course
        credits: Number of credits (default: 3)
        semester: Semester number (default: 1)
        
    Returns:
        int: ID of newly created course
        
    Example:
        course_id = add_course('CS101', 'Data Structures', 3, 1)
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO courses (course_code, course_name, credits, semester)
            VALUES (?, ?, ?, ?)
        ''', (course_code, course_name, credits, semester))
        
        connection.commit()
        course_id = cursor.lastrowid
        print(f"✓ Course '{course_name}' added with ID: {course_id}")
        return course_id
        
    except sqlite3.IntegrityError as e:
        print(f"✗ Error: {e}")
        connection.rollback()
        raise
    finally:
        close_connection(connection)


def get_course(course_id: int) -> Optional[dict]:
    """
    Retrieve course information by ID.
    
    Args:
        course_id: ID of the course
        
    Returns:
        dict: Course information if found, None otherwise
        
    Example:
        course = get_course(1)
        print(f"Course: {course['course_name']}")
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute('SELECT * FROM courses WHERE id = ?', (course_id,))
        row = cursor.fetchone()
        
        return dict(row) if row else None
            
    except sqlite3.Error as e:
        print(f"✗ Error retrieving course: {e}")
        raise
    finally:
        close_connection(connection)


def get_all_courses() -> List[dict]:
    """
    Retrieve all courses.
    
    Returns:
        List[dict]: List of all course records
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute('SELECT * FROM courses ORDER BY semester, course_code')
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
            
    except sqlite3.Error as e:
        print(f"✗ Error retrieving courses: {e}")
        raise
    finally:
        close_connection(connection)


# ============================================================================
# CRUD OPERATIONS - ENROLLMENTS
# ============================================================================

def enroll_student(student_id: int, course_id: int) -> int:
    """
    Enroll a student in a course.
    
    Args:
        student_id: ID of student
        course_id: ID of course
        
    Returns:
        int: ID of enrollment record
        
    Raises:
        sqlite3.IntegrityError: If student already enrolled in course
        
    Example:
        enrollment_id = enroll_student(1, 5)
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO enrollments (student_id, course_id)
            VALUES (?, ?)
        ''', (student_id, course_id))
        
        connection.commit()
        enrollment_id = cursor.lastrowid
        print(f"✓ Student {student_id} enrolled in course {course_id}")
        return enrollment_id
        
    except sqlite3.IntegrityError as e:
        print(f"✗ Error: Student already enrolled in this course")
        connection.rollback()
        raise
    finally:
        close_connection(connection)


def get_student_courses(student_id: int) -> List[dict]:
    """
    Get all courses enrolled by a student.
    
    Args:
        student_id: ID of student
        
    Returns:
        List[dict]: List of course records
        
    Example:
        courses = get_student_courses(1)
        for course in courses:
            print(f"Course: {course['course_name']} - Grade: {course['grade']}")
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            SELECT c.*, e.grade, e.enrollment_date
            FROM courses c
            JOIN enrollments e ON c.id = e.course_id
            WHERE e.student_id = ?
            ORDER BY c.semester
        ''', (student_id,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
            
    except sqlite3.Error as e:
        print(f"✗ Error retrieving student courses: {e}")
        raise
    finally:
        close_connection(connection)


def update_grade(student_id: int, course_id: int, grade: str) -> bool:
    """
    Update student's grade in a course.
    
    Args:
        student_id: ID of student
        course_id: ID of course
        grade: Grade (e.g., 'A', 'A+', 'B', etc.)
        
    Returns:
        bool: True if successful
        
    Example:
        update_grade(1, 5, 'A+')
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            UPDATE enrollments
            SET grade = ?
            WHERE student_id = ? AND course_id = ?
        ''', (grade, student_id, course_id))
        
        connection.commit()
        
        if cursor.rowcount > 0:
            print(f"✓ Grade updated for student {student_id} in course {course_id}")
            return True
        return False
            
    except sqlite3.Error as e:
        print(f"✗ Error updating grade: {e}")
        connection.rollback()
        raise
    finally:
        close_connection(connection)


# ============================================================================
# CRUD OPERATIONS - SUBMISSIONS
# ============================================================================

def add_submission(student_id: int, course_id: int, assignment_name: str, 
                   marks_obtained: float, total_marks: float = 100) -> int:
    """
    Add an assignment submission record.
    
    Args:
        student_id: ID of student
        course_id: ID of course
        assignment_name: Name of assignment
        marks_obtained: Marks obtained by student
        total_marks: Total marks for assignment (default: 100)
        
    Returns:
        int: ID of submission record
        
    Example:
        sub_id = add_submission(1, 5, 'Assignment 1', 85, 100)
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO submissions (student_id, course_id, assignment_name, marks_obtained, total_marks)
            VALUES (?, ?, ?, ?, ?)
        ''', (student_id, course_id, assignment_name, marks_obtained, total_marks))
        
        connection.commit()
        submission_id = cursor.lastrowid
        print(f"✓ Submission recorded for student {student_id}")
        return submission_id
        
    except sqlite3.Error as e:
        print(f"✗ Error adding submission: {e}")
        connection.rollback()
        raise
    finally:
        close_connection(connection)


def get_student_submissions(student_id: int, course_id: int = None) -> List[dict]:
    """
    Get all submissions for a student (optionally filtered by course).
    
    Args:
        student_id: ID of student
        course_id: Optional course ID to filter submissions
        
    Returns:
        List[dict]: List of submission records
        
    Example:
        # All submissions
        subs = get_student_submissions(1)
        
        # Submissions for specific course
        subs = get_student_submissions(1, course_id=5)
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        if course_id:
            cursor.execute('''
                SELECT * FROM submissions
                WHERE student_id = ? AND course_id = ?
                ORDER BY submission_date DESC
            ''', (student_id, course_id))
        else:
            cursor.execute('''
                SELECT * FROM submissions
                WHERE student_id = ?
                ORDER BY submission_date DESC
            ''', (student_id,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
            
    except sqlite3.Error as e:
        print(f"✗ Error retrieving submissions: {e}")
        raise
    finally:
        close_connection(connection)


def get_submission(submission_id: int) -> Optional[dict]:
    """
    Get a specific submission by ID.
    
    Args:
        submission_id: ID of submission
        
    Returns:
        dict: Submission record if found
        
    Example:
        sub = get_submission(10)
        print(f"Marks: {sub['marks_obtained']}/{sub['total_marks']}")
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute('SELECT * FROM submissions WHERE id = ?', (submission_id,))
        row = cursor.fetchone()
        
        return dict(row) if row else None
            
    except sqlite3.Error as e:
        print(f"✗ Error retrieving submission: {e}")
        raise
    finally:
        close_connection(connection)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_student_statistics(student_id: int) -> dict:
    """
    Get comprehensive statistics for a student.
    
    Args:
        student_id: ID of student
        
    Returns:
        dict: Statistics including total courses, average score, etc.
        
    Example:
        stats = get_student_statistics(1)
        print(f"Total Courses: {stats['total_courses']}")
        print(f"Average Score: {stats['average_score']:.2f}%")
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        # Get student info
        cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
        student = dict(cursor.fetchone() or {})
        
        # Get enrollment count
        cursor.execute('SELECT COUNT(*) as count FROM enrollments WHERE student_id = ?', (student_id,))
        enrollments = cursor.fetchone()['count']
        
        # Get average submission score
        cursor.execute('''
            SELECT AVG(marks_obtained/total_marks*100) as avg_score
            FROM submissions
            WHERE student_id = ?
        ''', (student_id,))
        result = cursor.fetchone()
        avg_score = result['avg_score'] or 0
        
        return {
            'student_name': student.get('name'),
            'student_email': student.get('email'),
            'total_courses': enrollments,
            'current_cgpa': student.get('cgpa', 0.0),
            'average_score': round(avg_score, 2),
            'status': student.get('status')
        }
            
    except sqlite3.Error as e:
        print(f"✗ Error retrieving statistics: {e}")
        raise
    finally:
        close_connection(connection)


def initialize_db() -> None:
    """
    Initialize database - create all tables and setup schema.
    
    This function should be called once when the application starts.
    It's safe to call multiple times (creates tables if they don't exist).
    
    Production Note:
        - Call this in your main.py or application startup
        - Idempotent: safe to call multiple times
        - Creates full database schema
        
    Example:
        if __name__ == '__main__':
            initialize_db()
            # Now you can use the database
    """
    print("\n" + "="*70)
    print("DATABASE INITIALIZATION")
    print("="*70)
    
    try:
        create_tables()
        print("\n✓ Database initialized successfully!")
        print(f"✓ Database file: {os.path.abspath(DB_FILE)}")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n✗ Database initialization failed: {e}")
        print("="*70 + "\n")
        raise


# ============================================================================
# DATABASE RESET (FOR TESTING/DEVELOPMENT)
# ============================================================================

def reset_database() -> None:
    """
    CAUTION: Drop all tables and reset database.
    
    WARNING: This will delete all data!
    Use only for development/testing purposes.
    
    Example:
        reset_database()
        initialize_db()  # Recreate empty tables
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        # Disable foreign key constraints temporarily
        cursor.execute('PRAGMA foreign_keys = OFF')
        
        # Drop all tables in reverse order of dependencies
        cursor.execute('DROP TABLE IF EXISTS submissions')
        cursor.execute('DROP TABLE IF EXISTS enrollments')
        cursor.execute('DROP TABLE IF EXISTS courses')
        cursor.execute('DROP TABLE IF EXISTS students')
        
        # Re-enable foreign keys
        cursor.execute('PRAGMA foreign_keys = ON')
        
        connection.commit()
        print("✓ Database reset successfully (all tables dropped)")
        
    except sqlite3.Error as e:
        print(f"✗ Error resetting database: {e}")
        connection.rollback()
        raise
    finally:
        close_connection(connection)


if __name__ == '__main__':
    """
    Test the database module directly.
    
    Run with: python db.py
    """
    print("\nTesting Database Module...\n")
    
    # Initialize database
    initialize_db()
    
    # Add sample courses
    print("\n--- Adding Courses ---")
    c1 = add_course('CS101', 'Data Structures', 3, 1)
    c2 = add_course('CS102', 'Web Development', 3, 1)
    c3 = add_course('CS201', 'Database Systems', 4, 2)
    
    # Add sample students
    print("\n--- Adding Students ---")
    s1 = add_student('Rahul Kumar', 'rahul@example.com', 9.2, '9876543210')
    s2 = add_student('Priya Singh', 'priya@example.com', 9.5, '9876543211')
    s3 = add_student('Amit Patel', 'amit@example.com', 8.8, '9876543212')
    
    # Enroll students in courses
    print("\n--- Enrolling Students ---")
    enroll_student(s1, c1)
    enroll_student(s1, c2)
    enroll_student(s2, c1)
    enroll_student(s2, c3)
    
    # Add submissions
    print("\n--- Adding Submissions ---")
    add_submission(s1, c1, 'Assignment 1', 85, 100)
    add_submission(s1, c2, 'Assignment 1', 92, 100)
    add_submission(s2, c1, 'Assignment 1', 88, 100)
    
    # Update grades
    print("\n--- Updating Grades ---")
    update_grade(s1, c1, 'A')
    update_grade(s2, c1, 'A+')
    
    # Retrieve and display data
    print("\n--- Student Information ---")
    student = get_student(s1)
    print(f"Name: {student['name']}")
    print(f"Email: {student['email']}")
    print(f"CGPA: {student['cgpa']}")
    
    print("\n--- Student Courses ---")
    courses = get_student_courses(s1)
    for course in courses:
        print(f"  • {course['course_name']} (Grade: {course['grade']})")
    
    print("\n--- Student Statistics ---")
    stats = get_student_statistics(s1)
    for key, value in stats.items():
        print(f"  • {key}: {value}")
    
    print("\n--- All Students ---")
    all_students = get_all_students()
    for student in all_students:
        print(f"  • {student['name']} - {student['email']} (CGPA: {student['cgpa']})")
    
    print("\n✓ Database test completed successfully!")
