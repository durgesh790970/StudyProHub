"""
Test Script - Validate SQLite Database Setup
Run this to verify everything is working correctly

Usage: python test_database.py
"""

import sys
import os
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
    get_student_statistics,
)
import sqlite3


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_section(title):
    """Print a section header"""
    print(f"\n→ {title}")
    print("-" * 70)


def test_database_connection():
    """Test 1: Database connection and initialization"""
    print_section("Test 1: Database Connection & Initialization")
    
    try:
        initialize_db()
        print("✓ Database initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def test_student_crud():
    """Test 2: Student CRUD operations"""
    print_section("Test 2: Student CRUD Operations")
    
    try:
        # CREATE
        print("  Testing CREATE...")
        sid = add_student('Test Student', 'test@example.com', 9.5, '1234567890')
        print(f"  ✓ Created student with ID: {sid}")
        
        # READ
        print("  Testing READ...")
        student = get_student(sid)
        assert student is not None, "Failed to retrieve student"
        assert student['name'] == 'Test Student', "Student name mismatch"
        assert student['email'] == 'test@example.com', "Student email mismatch"
        print(f"  ✓ Retrieved student: {student['name']}")
        
        # UPDATE
        print("  Testing UPDATE...")
        update_student(sid, cgpa=9.8, phone='0987654321')
        student = get_student(sid)
        assert student['cgpa'] == 9.8, "CGPA not updated"
        assert student['phone'] == '0987654321', "Phone not updated"
        print(f"  ✓ Updated student - CGPA: {student['cgpa']}")
        
        # LIST ALL
        print("  Testing LIST ALL...")
        all_students = get_all_students()
        assert len(all_students) > 0, "No students found"
        print(f"  ✓ Found {len(all_students)} students in database")
        
        return True, sid
        
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False, None


def test_course_crud(student_id):
    """Test 3: Course CRUD operations"""
    print_section("Test 3: Course CRUD Operations")
    
    try:
        # CREATE
        print("  Testing CREATE...")
        cid1 = add_course('TEST101', 'Test Course 1', 3, 1)
        cid2 = add_course('TEST102', 'Test Course 2', 4, 1)
        print(f"  ✓ Created courses with IDs: {cid1}, {cid2}")
        
        return True, cid1, cid2
        
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False, None, None


def test_enrollment_crud(student_id, course_id1, course_id2):
    """Test 4: Enrollment and Grade operations"""
    print_section("Test 4: Enrollment & Grade Operations")
    
    try:
        # ENROLL
        print("  Testing ENROLL...")
        eid1 = enroll_student(student_id, course_id1)
        eid2 = enroll_student(student_id, course_id2)
        print(f"  ✓ Enrolled in courses with enrollment IDs: {eid1}, {eid2}")
        
        # GET COURSES
        print("  Testing GET COURSES...")
        courses = get_student_courses(student_id)
        assert len(courses) >= 2, "Not all enrollments retrieved"
        print(f"  ✓ Retrieved {len(courses)} enrolled courses")
        
        # UPDATE GRADE
        print("  Testing UPDATE GRADE...")
        update_grade(student_id, course_id1, 'A+')
        update_grade(student_id, course_id2, 'A')
        courses = get_student_courses(student_id)
        grades = {c['id']: c['grade'] for c in courses}
        assert grades[course_id1] == 'A+', "Grade not updated"
        print(f"  ✓ Grades assigned: TEST101 = A+, TEST102 = A")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def test_submission_crud(student_id, course_id1, course_id2):
    """Test 5: Submission operations"""
    print_section("Test 5: Submission Operations")
    
    try:
        # ADD SUBMISSIONS
        print("  Testing ADD SUBMISSIONS...")
        sub1 = add_submission(student_id, course_id1, 'Assignment 1', 92, 100)
        sub2 = add_submission(student_id, course_id2, 'Assignment 1', 88, 100)
        sub3 = add_submission(student_id, course_id1, 'Assignment 2', 95, 100)
        print(f"  ✓ Created submissions with IDs: {sub1}, {sub2}, {sub3}")
        
        # GET SUBMISSIONS
        print("  Testing GET SUBMISSIONS...")
        subs = get_student_submissions(student_id)
        assert len(subs) >= 3, "Not all submissions retrieved"
        print(f"  ✓ Retrieved {len(subs)} total submissions")
        
        # GET BY COURSE
        print("  Testing GET BY COURSE...")
        subs_course1 = get_student_submissions(student_id, course_id1)
        assert len(subs_course1) >= 2, "Not all course submissions retrieved"
        print(f"  ✓ Course 1 has {len(subs_course1)} submissions")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def test_statistics(student_id):
    """Test 6: Statistics function"""
    print_section("Test 6: Statistics & Reporting")
    
    try:
        print("  Testing GET STATISTICS...")
        stats = get_student_statistics(student_id)
        
        print(f"  Student: {stats['student_name']}")
        print(f"  Email: {stats['student_email']}")
        print(f"  Total Courses: {stats['total_courses']}")
        print(f"  Current CGPA: {stats['current_cgpa']}")
        print(f"  Average Score: {stats['average_score']:.2f}%")
        print(f"  Status: {stats['status']}")
        
        assert stats['total_courses'] >= 2, "Course count mismatch"
        assert stats['average_score'] > 0, "Average score calculation error"
        print("  ✓ Statistics calculated correctly")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def test_error_handling():
    """Test 7: Error handling"""
    print_section("Test 7: Error Handling")
    
    try:
        print("  Testing DUPLICATE EMAIL...")
        add_student('Student 1', 'duplicate@example.com', 9.0)
        
        try:
            add_student('Student 2', 'duplicate@example.com', 8.5)
            print("  ✗ Should have raised IntegrityError")
            return False
        except sqlite3.IntegrityError:
            print("  ✓ Correctly caught duplicate email error")
        
        print("  Testing INVALID REFERENCE...")
        try:
            enroll_student(99999, 99999)  # Non-existent IDs
            print("  ✗ Should have raised foreign key error")
            return False
        except sqlite3.IntegrityError:
            print("  ✓ Correctly caught foreign key error")
        
        print("  Testing MISSING RECORD...")
        result = get_student(99999)
        assert result is None, "Should return None for missing record"
        print("  ✓ Correctly returned None for missing record")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def test_data_types():
    """Test 8: Data types and constraints"""
    print_section("Test 8: Data Types & Constraints")
    
    try:
        print("  Testing STRING fields...")
        student = add_student('String Test', 'string@test.com', 9.0)
        s = get_student(student)
        assert isinstance(s['name'], str), "Name should be string"
        assert isinstance(s['email'], str), "Email should be string"
        print("  ✓ String fields working correctly")
        
        print("  Testing NUMERIC fields...")
        assert isinstance(s['cgpa'], (int, float)), "CGPA should be numeric"
        assert s['cgpa'] == 9.0, "CGPA value incorrect"
        print("  ✓ Numeric fields working correctly")
        
        print("  Testing TIMESTAMP fields...")
        assert isinstance(s['enrollment_date'], str), "Timestamp should be string"
        print("  ✓ Timestamp fields working correctly")
        
        print("  Testing UNIQUE constraint...")
        course = add_course('UNIQUE001', 'Unique Test', 3, 1)
        try:
            add_course('UNIQUE001', 'Duplicate Code', 3, 1)
            print("  ✗ Should have raised unique constraint error")
            return False
        except sqlite3.IntegrityError:
            print("  ✓ Unique constraint working correctly")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def run_all_tests():
    """Run all tests and report results"""
    print_header("SQLite DATABASE SETUP TEST SUITE")
    
    results = {
        'Test 1: Database Initialization': test_database_connection(),
    }
    
    if results['Test 1: Database Initialization']:
        test2_result, sid = test_student_crud()
        results['Test 2: Student CRUD'] = test2_result
        
        if test2_result:
            test3_result, cid1, cid2 = test_course_crud(sid)
            results['Test 3: Course CRUD'] = test3_result
            
            if test3_result:
                results['Test 4: Enrollment & Grades'] = test_enrollment_crud(sid, cid1, cid2)
                results['Test 5: Submissions'] = test_submission_crud(sid, cid1, cid2)
                results['Test 6: Statistics'] = test_statistics(sid)
    
    results['Test 7: Error Handling'] = test_error_handling()
    results['Test 8: Data Types'] = test_data_types()
    
    # Print summary
    print_header("TEST RESULTS SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:<40} {status}")
    
    print("-" * 70)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "=" * 70)
        print("  🎉 ALL TESTS PASSED! DATABASE IS WORKING CORRECTLY!")
        print("=" * 70)
        return True
    else:
        print("\n" + "=" * 70)
        print("  ⚠️  SOME TESTS FAILED! CHECK ERRORS ABOVE")
        print("=" * 70)
        return False


if __name__ == '__main__':
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n✗ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
