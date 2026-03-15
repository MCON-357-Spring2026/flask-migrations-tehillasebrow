from datetime import date
from flask import Blueprint, jsonify, request
from .extensions import db
from .models import Student, Assignment, Grade

api = Blueprint("main", __name__)


@api.get("/")
def home():
    return {
        "message": "Flask migrations lesson app",
        "endpoints": [
            "GET /exercises/students",
            "POST /exercises/students",
            "GET /exercises/assignments",
            "POST /exercises/assignments",
            "GET /exercises/grades",
            "POST /exercises/grades",
        ],
    }


@api.get("/students")
def get_students():
    students = Student.query.order_by(Student.id).all()
    return jsonify([student.to_dict() for student in students])


@api.post("/students")
def create_student():
    data = request.get_json() or {}

    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"error": "name and email are required"}), 400

    student = Student(name=name, email=email)

    if hasattr(Student, "cohort"):
        student.cohort = data.get("cohort")

    db.session.add(student)
    db.session.commit()
    return jsonify(student.to_dict()), 201


@api.get("/assignments")
def get_assignments():
    assignments = Assignment.query.order_by(Assignment.id).all()
    return jsonify([assignment.to_dict() for assignment in assignments])


@api.post("/assignments")
def create_assignment():
    data = request.get_json() or {}

    title = data.get("title")
    max_score = data.get("max_score")

    # Grab the due date string
    due_date_str = data.get("due_date")

    if not title or max_score is None:
        return jsonify({"error": "title and max_score are required"}), 400

    # Validate and parse the date to satisfy test_post_assignment_invalid_due_date_rejected
    parsed_date = None
    if due_date_str:
        try:
            parsed_date = date.fromisoformat(due_date_str)
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    # Add due_date to the Assignment creation
    assignment = Assignment(title=title, max_score=max_score, due_date=parsed_date)
    db.session.add(assignment)
    db.session.commit()
    return jsonify(assignment.to_dict()), 201


@api.get("/grades")
def get_grades():
    grades = Grade.query.order_by(Grade.id).all()
    return jsonify([grade.to_dict() for grade in grades])


@api.post("/grades")
def create_grade():
    data = request.get_json() or {}

    score = data.get("score")
    student_id = data.get("student_id")
    assignment_id = data.get("assignment_id")

    # Grab the comment string
    comment = data.get("comment")

    if score is None or student_id is None or assignment_id is None:
        return jsonify({"error": "score, student_id, and assignment_id are required"}), 400

    # Using db.session.get to fix the deprecation warnings in your Pytest output!
    student = db.session.get(Student, student_id)
    assignment = db.session.get(Assignment, assignment_id)

    if student is None:
        return jsonify({"error": "student not found"}), 404
    if assignment is None:
        return jsonify({"error": "assignment not found"}), 404

    # Add comment to the Grade creation
    grade = Grade(score=score, student_id=student_id, assignment_id=assignment_id, comment=comment)
    db.session.add(grade)
    db.session.commit()
    return jsonify(grade.to_dict()), 201