import streamlit as st
import requests

API_URL = "http://127.0.0.1:5000/attendance"

st.title("Attendance Management System")

# Student ID Input
student_id = st.text_input("Enter Student ID", "12345")

if st.button("Get Attendance"):
    response = requests.get(f"{API_URL}/{student_id}")
    if response.status_code == 200:
        data = response.json()
        st.write(f"Total Classes: {data['total_classes']}")
        st.write(f"Attended Classes: {data['attended_classes']}")
        st.write(f"Attendance Percentage: {data['attendance_percentage']}%")
    else:
        st.error("Student not found!")

st.subheader("Update Attendance")
total_classes = st.number_input("Total Classes", min_value=0, value=10, step=1)
attended_classes = st.number_input("Attended Classes", min_value=0, value=8, step=1)

if st.button("Update Attendance"):
    payload = {
        "student_id": student_id,
        "total_classes": total_classes,
        "attended_classes": attended_classes
    }
    response = requests.post(f"{API_URL}/update", json=payload)
    if response.status_code == 200:
        st.success("Attendance updated successfully!")
    else:
        st.error("Error updating attendance")

if st.button("Get Leave Suggestions"):
    response = requests.get(f"{API_URL}/suggestions/{student_id}")
    if response.status_code == 200:
        data = response.json()
        st.write(f"You can take {data['safe_leave_days']} days off while maintaining 75% attendance.")
    else:
        st.error("Student not found!")

