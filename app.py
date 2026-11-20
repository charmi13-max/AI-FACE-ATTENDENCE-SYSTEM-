from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, url_for

from utils.database import add_student, get_attendance, get_students, init_db, mark_attendance
from utils.face_recognition import recognize_face_from_bytes, train_face_encodings

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__)
app.config["SECRET_KEY"] = "face-attendance-secret"


@app.route("/")
def index():
    students = get_students()
    attendance = get_attendance(limit=20)
    return render_template("index.html", students=students, attendance=attendance)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip()
        name = request.form.get("name", "").strip()
        course = request.form.get("course", "").strip()
        files = request.files.getlist("photos")

        if not student_id or not name or not course or not files:
            return render_template("register.html", error="Please complete all fields and upload at least one face photo.")

        student_dir = BASE_DIR / "face_data" / student_id
        student_dir.mkdir(parents=True, exist_ok=True)

        for file in files:
            if file.filename == "":
                continue
            file_path = student_dir / file.filename
            file.save(file_path)

        add_student(student_id, name, course)
        train_face_encodings()
        return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/attendance")
def attendance():
    students = get_students()
    return render_template("attendance.html", students=students)


@app.route("/attendance/mark", methods=["POST"])
def mark_attendance_route():
    if "image" not in request.files:
        return jsonify({"status": "error", "message": "No image was sent."}), 400

    image_file = request.files["image"]
    if image_file.filename == "":
        return jsonify({"status": "error", "message": "No image selected."}), 400

    image_bytes = image_file.read()
    match = recognize_face_from_bytes(image_bytes)

    if match is None:
        return jsonify({"status": "error", "message": "Face not recognized. Please try again."}), 400

    student_id = match["student_id"]
    status = mark_attendance(student_id)

    if status == "already_marked":
        return jsonify({
            "status": "info",
            "student_id": student_id,
            "message": "Attendance already marked for today.",
            "confidence": match["confidence"],
        })

    return jsonify({
        "status": "success",
        "student_id": student_id,
        "message": "Attendance marked successfully.",
        "confidence": match["confidence"],
    })


@app.route("/reports")
def reports():
    attendance = get_attendance(limit=100)
    return render_template("reports.html", attendance=attendance)


if __name__ == "__main__":
    init_db()
    train_face_encodings()
    app.run(debug=True, host="0.0.0.0", port=5000)
