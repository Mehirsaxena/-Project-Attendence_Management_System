from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# Initialize Database
def init_db():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE,
            total_classes INTEGER,
            attended_classes INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Get Attendance Details
@app.route('/attendance/<student_id>', methods=['GET'])
def get_attendance(student_id):
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attendance WHERE student_id=?", (student_id,))
    data = cursor.fetchone()
    conn.close()

    if data:
        attendance_percentage = (data[3] / data[2]) * 100 if data[3] > 0 else 0
        return jsonify({
            "student_id": data[1],
            "total_classes": data[2],
            "attended_classes": data[3],
            "attendance_percentage": round(attendance_percentage, 2)
        })
    return jsonify({"message": "Student not found"}), 404

# Update Attendance
@app.route('/attendance/update', methods=['POST'])
def update_attendance():
    data = request.json
    student_id = data["student_id"]
    total_classes = data["total_classes"]
    attended_classes = data["attended_classes"]

    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attendance WHERE student_id=?", (student_id,))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("UPDATE attendance SET total_classes=?, attended_classes=? WHERE student_id=?",
                       (total_classes, attended_classes, student_id))
    else:
        cursor.execute("INSERT INTO attendance (student_id, total_classes, attended_classes) VALUES (?, ?, ?)",
                       (student_id, total_classes, attended_classes))

    conn.commit()
    conn.close()
    return jsonify({"message": "Attendance updated successfully"}), 200

# **✅ NEW: Suggest Safe Leave Days**
@app.route('/attendance/suggestions/<student_id>', methods=['GET'])
def leave_suggestions(student_id):
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute("SELECT total_classes, attended_classes FROM attendance WHERE student_id=?", (student_id,))
    data = cursor.fetchone()
    conn.close()

    if not data:
        return jsonify({"message": "Student not found"}), 404

    total_classes, attended_classes = data
    if total_classes == 0:
        return jsonify({"message": "No attendance data available"}), 400

    current_attendance = (attended_classes / total_classes) * 100

    # Calculate the maximum safe leaves
    safe_leave_days = 0
    while ((attended_classes / (total_classes + safe_leave_days + 1)) * 100) >= 75:
        safe_leave_days += 1

    return jsonify({
        "student_id": student_id,
        "current_attendance": round(current_attendance, 2),
        "safe_leave_days": safe_leave_days
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
