"""
Main Application File - Project Demo
Shows how to use the database module (db.py) for CRUD operations.

This is a complete example for a college project demonstrating:
- Database initialization
- CRUD operations
- Error handling
- Data retrieval and manipulation
- Real-world usage patterns

Production Note:
- This can be run standalone: python main.py
- Or imported in Django views/management commands
- All database operations are wrapped in try-except for safety

Author: Your Name
Date: 2026-02-01
"""

import sys
from db import (
    initialize_db,
    add_student,
    add_course,
    enroll_student,
    add_submission,
    get_student,
    get_all_students,
    get_student_courses,
    get_student_submissions,
    update_student,
    update_grade,
    delete_student,
    get_student_statistics,
    get_all_courses,
)


# ============================================================================
# MAIN APPLICATION CLASS
# ============================================================================

class UniversityManagementSystem:
    """
    University Management System - Demonstrates complete database usage.
    
    Methods handle:
    - Student management
    - Course management
    - Enrollment management
    - Submission tracking
    - Report generation
    """
    
    def __init__(self):
        """Initialize the system and database."""
        print("\n" + "="*70)
        print("UNIVERSITY MANAGEMENT SYSTEM")
        print("="*70)
        
        # Initialize database
        try:
            initialize_db()
            print("✓ System initialized successfully\n")
        except Exception as e:
            print(f"✗ Failed to initialize system: {e}")
            sys.exit(1)
    
    # ========================================================================
    # STUDENT MANAGEMENT
    # ========================================================================
    
    def register_student(self, name: str, email: str, cgpa: float = 0.0, phone: str = None) -> int:
        """
        Register a new student in the system.
        
        Args:
            name: Student's full name
            email: Student's email (must be unique)
            cgpa: Current CGPA (optional)
            phone: Student's phone number (optional)
            
        Returns:
            int: Student ID if successful, None otherwise
            
        Example:
            student_id = system.register_student('Raj Kumar', 'raj@example.com', 9.2)
        """
        try:
            print(f"\n→ Registering student: {name}")
            student_id = add_student(name, email, cgpa, phone)
            return student_id
            
        except Exception as e:
            print(f"✗ Failed to register student: {e}")
            return None
    
    def view_student(self, student_id: int):
        """
        View detailed information of a student.
        
        Args:
            student_id: ID of student to view
        """
        try:
            student = get_student(student_id)
            
            if student:
                print(f"\n📋 Student Details (ID: {student_id})")
                print(f"  Name: {student['name']}")
                print(f"  Email: {student['email']}")
                print(f"  Phone: {student['phone']}")
                print(f"  CGPA: {student['cgpa']}")
                print(f"  Status: {student['status']}")
                print(f"  Enrolled: {student['enrollment_date']}")
            else:
                print(f"ℹ Student with ID {student_id} not found")
                
        except Exception as e:
            print(f"✗ Error retrieving student: {e}")
    
    def list_all_students(self):
        """List all registered students."""
        try:
            print(f"\n📚 All Registered Students")
            print("-" * 70)
            
            students = get_all_students()
            
            if students:
                print(f"{'ID':<5} {'Name':<20} {'Email':<25} {'CGPA':<8} {'Status':<10}")
                print("-" * 70)
                
                for student in students:
                    print(f"{student['id']:<5} {student['name']:<20} {student['email']:<25} "
                          f"{student['cgpa']:<8.2f} {student['status']:<10}")
            else:
                print("ℹ No students registered yet")
                
        except Exception as e:
            print(f"✗ Error listing students: {e}")
    
    def update_student_info(self, student_id: int, **kwargs):
        """
        Update student information.
        
        Args:
            student_id: ID of student to update
            **kwargs: Fields to update (name, email, cgpa, phone, status)
            
        Example:
            system.update_student_info(1, cgpa=9.5, phone='1234567890')
        """
        try:
            print(f"\n→ Updating student {student_id}")
            success = update_student(student_id, **kwargs)
            
            if success:
                print(f"✓ Student information updated")
            else:
                print(f"✗ Failed to update student")
                
        except Exception as e:
            print(f"✗ Error updating student: {e}")
    
    # ========================================================================
    # COURSE MANAGEMENT
    # ========================================================================
    
    def add_course_to_system(self, course_code: str, course_name: str, 
                            credits: int = 3, semester: int = 1) -> int:
        """
        Add a new course to the system.
        
        Args:
            course_code: Unique course code (e.g., 'CS101')
            course_name: Full course name
            credits: Credit hours (default: 3)
            semester: Semester number (default: 1)
            
        Returns:
            int: Course ID
            
        Example:
            course_id = system.add_course_to_system('CS101', 'Data Structures', 3, 1)
        """
        try:
            print(f"\n→ Adding course: {course_code}")
            course_id = add_course(course_code, course_name, credits, semester)
            return course_id
            
        except Exception as e:
            print(f"✗ Failed to add course: {e}")
            return None
    
    def list_all_courses(self):
        """List all available courses."""
        try:
            print(f"\n📖 All Available Courses")
            print("-" * 70)
            
            courses = get_all_courses()
            
            if courses:
                print(f"{'ID':<5} {'Code':<10} {'Course Name':<30} {'Credits':<8} {'Semester':<8}")
                print("-" * 70)
                
                for course in courses:
                    print(f"{course['id']:<5} {course['course_code']:<10} "
                          f"{course['course_name']:<30} {course['credits']:<8} {course['semester']:<8}")
            else:
                print("ℹ No courses added yet")
                
        except Exception as e:
            print(f"✗ Error listing courses: {e}")
    
    # ========================================================================
    # ENROLLMENT MANAGEMENT
    # ========================================================================
    
    def enroll_in_course(self, student_id: int, course_id: int):
        """
        Enroll a student in a course.
        
        Args:
            student_id: ID of student
            course_id: ID of course
            
        Example:
            system.enroll_in_course(1, 3)
        """
        try:
            print(f"\n→ Enrolling student {student_id} in course {course_id}")
            enrollment_id = enroll_student(student_id, course_id)
            print(f"✓ Enrollment successful (ID: {enrollment_id})")
            
        except Exception as e:
            print(f"✗ Failed to enroll student: {e}")
    
    def view_student_courses(self, student_id: int):
        """
        View all courses a student is enrolled in.
        
        Args:
            student_id: ID of student
            
        Example:
            system.view_student_courses(1)
        """
        try:
            print(f"\n📚 Courses for Student {student_id}")
            print("-" * 70)
            
            courses = get_student_courses(student_id)
            
            if courses:
                print(f"{'Course':<30} {'Credits':<8} {'Grade':<8}")
                print("-" * 70)
                
                for course in courses:
                    print(f"{course['course_name']:<30} {course['credits']:<8} "
                          f"{course['grade'] or 'Not Graded':<8}")
            else:
                print("ℹ Student not enrolled in any courses")
                
        except Exception as e:
            print(f"✗ Error retrieving student courses: {e}")
    
    def assign_grade(self, student_id: int, course_id: int, grade: str):
        """
        Assign a grade to a student in a course.
        
        Args:
            student_id: ID of student
            course_id: ID of course
            grade: Grade (e.g., 'A', 'A+', 'B', etc.)
            
        Example:
            system.assign_grade(1, 3, 'A+')
        """
        try:
            print(f"\n→ Assigning grade to student {student_id} in course {course_id}")
            success = update_grade(student_id, course_id, grade)
            
            if success:
                print(f"✓ Grade '{grade}' assigned successfully")
            else:
                print(f"✗ Failed to assign grade (invalid enrollment)")
                
        except Exception as e:
            print(f"✗ Error assigning grade: {e}")
    
    # ========================================================================
    # SUBMISSION MANAGEMENT
    # ========================================================================
    
    def record_submission(self, student_id: int, course_id: int, 
                         assignment_name: str, marks_obtained: float, 
                         total_marks: float = 100):
        """
        Record an assignment submission.
        
        Args:
            student_id: ID of student
            course_id: ID of course
            assignment_name: Name of assignment
            marks_obtained: Marks scored
            total_marks: Total marks (default: 100)
            
        Example:
            system.record_submission(1, 3, 'Assignment 1', 85, 100)
        """
        try:
            print(f"\n→ Recording submission for student {student_id}")
            submission_id = add_submission(student_id, course_id, assignment_name, 
                                          marks_obtained, total_marks)
            print(f"✓ Submission recorded (ID: {submission_id})")
            
        except Exception as e:
            print(f"✗ Failed to record submission: {e}")
    
    def view_student_submissions(self, student_id: int, course_id: int = None):
        """
        View submissions of a student (optionally for a specific course).
        
        Args:
            student_id: ID of student
            course_id: Optional - specific course ID
            
        Example:
            system.view_student_submissions(1, 3)
        """
        try:
            if course_id:
                print(f"\n📝 Submissions for Student {student_id} in Course {course_id}")
            else:
                print(f"\n📝 All Submissions for Student {student_id}")
            
            print("-" * 80)
            
            submissions = get_student_submissions(student_id, course_id)
            
            if submissions:
                print(f"{'Assignment':<25} {'Marks':<10} {'Date Submitted':<20}")
                print("-" * 80)
                
                for sub in submissions:
                    marks_str = f"{sub['marks_obtained']:.1f}/{sub['total_marks']:.1f}"
                    print(f"{sub['assignment_name']:<25} {marks_str:<10} "
                          f"{sub['submission_date']:<20}")
            else:
                print("ℹ No submissions found")
                
        except Exception as e:
            print(f"✗ Error retrieving submissions: {e}")
    
    # ========================================================================
    # REPORTING & ANALYTICS
    # ========================================================================
    
    def generate_student_report(self, student_id: int):
        """
        Generate a comprehensive report for a student.
        
        Args:
            student_id: ID of student
            
        Example:
            system.generate_student_report(1)
        """
        try:
            print(f"\n📊 STUDENT REPORT")
            print("=" * 70)
            
            # Basic info
            student = get_student(student_id)
            if not student:
                print(f"✗ Student {student_id} not found")
                return
            
            # Statistics
            stats = get_student_statistics(student_id)
            
            print(f"\nBasic Information:")
            print(f"  Name: {student['name']}")
            print(f"  Email: {student['email']}")
            print(f"  Phone: {student['phone']}")
            print(f"  Status: {student['status']}")
            
            print(f"\nAcademic Statistics:")
            print(f"  Current CGPA: {stats['current_cgpa']:.2f}")
            print(f"  Total Courses: {stats['total_courses']}")
            print(f"  Average Score: {stats['average_score']:.2f}%")
            
            print(f"\nEnrolled Courses:")
            courses = get_student_courses(student_id)
            if courses:
                for course in courses:
                    print(f"  • {course['course_name']} - Grade: {course['grade'] or 'Pending'}")
            else:
                print("  No courses enrolled")
            
            print(f"\nRecent Submissions:")
            submissions = get_student_submissions(student_id)
            if submissions:
                for sub in submissions[:5]:  # Show last 5
                    percentage = (sub['marks_obtained']/sub['total_marks']*100)
                    print(f"  • {sub['assignment_name']}: {sub['marks_obtained']}/{sub['total_marks']} "
                          f"({percentage:.1f}%)")
            else:
                print("  No submissions")
            
            print("\n" + "=" * 70)
            
        except Exception as e:
            print(f"✗ Error generating report: {e}")
    
    def generate_course_report(self, course_id: int):
        """
        Generate a report for a course.
        
        Args:
            course_id: ID of course
        """
        try:
            from db import get_course
            
            print(f"\n📊 COURSE REPORT")
            print("=" * 70)
            
            course = get_course(course_id)
            if not course:
                print(f"✗ Course {course_id} not found")
                return
            
            print(f"Course: {course['course_name']}")
            print(f"Code: {course['course_code']}")
            print(f"Credits: {course['credits']}")
            print(f"Semester: {course['semester']}")
            
            # TODO: Add enrolled students count and statistics
            
            print("=" * 70)
            
        except Exception as e:
            print(f"✗ Error generating course report: {e}")


# ============================================================================
# DEMONSTRATION MENU
# ============================================================================

def show_menu():
    """Display the main menu."""
    print("\n" + "="*70)
    print("MENU OPTIONS")
    print("="*70)
    print("1. Register a new student")
    print("2. View student details")
    print("3. List all students")
    print("4. Update student information")
    print("5. Add a course")
    print("6. List all courses")
    print("7. Enroll student in course")
    print("8. View student's courses")
    print("9. Assign grade")
    print("10. Record submission")
    print("11. View student submissions")
    print("12. Generate student report")
    print("13. Run demo (auto-populate data)")
    print("0. Exit")
    print("="*70)


def run_demo(system: UniversityManagementSystem):
    """
    Run a demo with sample data.
    
    This shows a complete workflow of the system.
    """
    print("\n" + "="*70)
    print("RUNNING DEMO - AUTO-POPULATING SAMPLE DATA")
    print("="*70)
    
    try:
        # Add sample courses
        print("\n[STEP 1] Adding courses...")
        c1 = system.add_course_to_system('CS101', 'Data Structures', 3, 1)
        c2 = system.add_course_to_system('CS102', 'Web Development', 3, 1)
        c3 = system.add_course_to_system('CS201', 'Database Systems', 4, 2)
        
        # Add sample students
        print("\n[STEP 2] Registering students...")
        s1 = system.register_student('Rahul Kumar', 'rahul@example.com', 9.2, '9876543210')
        s2 = system.register_student('Priya Singh', 'priya@example.com', 9.5, '9876543211')
        s3 = system.register_student('Amit Patel', 'amit@example.com', 8.8, '9876543212')
        
        # Enroll students
        print("\n[STEP 3] Enrolling students in courses...")
        system.enroll_in_course(s1, c1)
        system.enroll_in_course(s1, c2)
        system.enroll_in_course(s2, c1)
        system.enroll_in_course(s2, c3)
        system.enroll_in_course(s3, c1)
        
        # Record submissions
        print("\n[STEP 4] Recording submissions...")
        system.record_submission(s1, c1, 'Assignment 1', 85, 100)
        system.record_submission(s1, c2, 'Assignment 1', 92, 100)
        system.record_submission(s2, c1, 'Assignment 1', 88, 100)
        system.record_submission(s3, c1, 'Assignment 1', 78, 100)
        
        # Assign grades
        print("\n[STEP 5] Assigning grades...")
        system.assign_grade(s1, c1, 'A')
        system.assign_grade(s2, c1, 'A+')
        system.assign_grade(s3, c1, 'B+')
        
        # Display results
        print("\n[STEP 6] Displaying results...")
        system.list_all_students()
        system.list_all_courses()
        
        # Generate reports
        print("\n[STEP 7] Generating reports...")
        system.generate_student_report(s1)
        
        print("\n✓ Demo completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Demo failed: {e}")


def run_interactive_mode(system: UniversityManagementSystem):
    """Run the system in interactive mode."""
    while True:
        show_menu()
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == '0':
            print("\n✓ Thank you for using the system. Goodbye!")
            break
        
        elif choice == '1':
            name = input("Enter student name: ").strip()
            email = input("Enter email: ").strip()
            cgpa = float(input("Enter CGPA (default 0.0): ") or 0.0)
            phone = input("Enter phone (optional): ").strip() or None
            system.register_student(name, email, cgpa, phone)
        
        elif choice == '2':
            try:
                student_id = int(input("Enter student ID: ").strip())
                system.view_student(student_id)
            except ValueError:
                print("✗ Invalid student ID")
        
        elif choice == '3':
            system.list_all_students()
        
        elif choice == '4':
            try:
                student_id = int(input("Enter student ID: ").strip())
                print("Enter new values (press Enter to skip):")
                updates = {}
                
                name = input("Name: ").strip()
                if name:
                    updates['name'] = name
                
                cgpa = input("CGPA: ").strip()
                if cgpa:
                    updates['cgpa'] = float(cgpa)
                
                phone = input("Phone: ").strip()
                if phone:
                    updates['phone'] = phone
                
                if updates:
                    system.update_student_info(student_id, **updates)
                else:
                    print("ℹ No updates provided")
                    
            except ValueError:
                print("✗ Invalid input")
        
        elif choice == '5':
            code = input("Enter course code: ").strip()
            name = input("Enter course name: ").strip()
            credits = int(input("Enter credits (default 3): ") or 3)
            semester = int(input("Enter semester (default 1): ") or 1)
            system.add_course_to_system(code, name, credits, semester)
        
        elif choice == '6':
            system.list_all_courses()
        
        elif choice == '7':
            try:
                student_id = int(input("Enter student ID: ").strip())
                course_id = int(input("Enter course ID: ").strip())
                system.enroll_in_course(student_id, course_id)
            except ValueError:
                print("✗ Invalid input")
        
        elif choice == '8':
            try:
                student_id = int(input("Enter student ID: ").strip())
                system.view_student_courses(student_id)
            except ValueError:
                print("✗ Invalid student ID")
        
        elif choice == '9':
            try:
                student_id = int(input("Enter student ID: ").strip())
                course_id = int(input("Enter course ID: ").strip())
                grade = input("Enter grade: ").strip()
                system.assign_grade(student_id, course_id, grade)
            except ValueError:
                print("✗ Invalid input")
        
        elif choice == '10':
            try:
                student_id = int(input("Enter student ID: ").strip())
                course_id = int(input("Enter course ID: ").strip())
                assignment = input("Enter assignment name: ").strip()
                marks = float(input("Enter marks obtained: ").strip())
                total = float(input("Enter total marks (default 100): ") or 100)
                system.record_submission(student_id, course_id, assignment, marks, total)
            except ValueError:
                print("✗ Invalid input")
        
        elif choice == '11':
            try:
                student_id = int(input("Enter student ID: ").strip())
                system.view_student_submissions(student_id)
            except ValueError:
                print("✗ Invalid student ID")
        
        elif choice == '12':
            try:
                student_id = int(input("Enter student ID: ").strip())
                system.generate_student_report(student_id)
            except ValueError:
                print("✗ Invalid student ID")
        
        elif choice == '13':
            run_demo(system)
        
        else:
            print("✗ Invalid choice. Please try again.")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """
    Main entry point of the application.
    
    Production Note:
        - This is the entry point for the standalone application
        - Can also be imported and used with Django
        - Database is initialized on startup
    """
    try:
        # Initialize system
        system = UniversityManagementSystem()
        
        # Run interactive mode
        run_interactive_mode(system)
        
    except KeyboardInterrupt:
        print("\n\n✗ Application interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
