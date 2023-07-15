import cv2
import dlib
import numpy as np
import psycopg2
import time
from tkinter import messagebox

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    database="fastapi-login",
    user="postgres",
    password="jaibalayya",
    host="localhost",
    port="5432"
)

# Create a table to store attendance records
create_table_query = """
    CREATE TABLE IF NOT EXISTS attendance (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        timestamp TIMESTAMP NOT NULL
    );
"""
with conn.cursor() as cursor:
    cursor.execute(create_table_query)
conn.commit()

# Initialize the face detector, facial landmarks predictor, and face recognition model
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")
facerec = dlib.face_recognition_model_v1("models/dlib_face_recognition_resnet_model_v1.dat")

# Function to extract face embeddings from an image
def get_face_embeddings(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    face_embeddings = []
    for face in faces:
        landmarks = predictor(gray, face)
        embedding = np.array(facerec.compute_face_descriptor(image, landmarks))
        face_embeddings.append(embedding)
    return face_embeddings

# Function to compute L2 distance between two embeddings
def compute_distance(embedding1, embedding2):
    return np.linalg.norm(embedding1 - embedding2)

# Function to check if a face exists in the database and return the name if found
def check_attendance(embedding):
    with conn.cursor() as cursor:
        select_query = "SELECT name, embedding FROM face_embeddings"
        cursor.execute(select_query)
        existing_faces = cursor.fetchall()
        
        # Compare the captured embedding with all existing embeddings
        for (name, existing_embedding) in existing_faces:
            distance = compute_distance(embedding, np.array(existing_embedding))
            if distance < 0.6:  # Adjust the threshold as needed
                return name
        
        return None

# Function to mark attendance in the database
def mark_attendance(name):
    with conn.cursor() as cursor:
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        insert_query = "INSERT INTO attendance (name, timestamp) VALUES (%s, %s)"
        cursor.execute(insert_query, (name, current_time))
    conn.commit()

# Function to view attendance records
def view_attendance():
    with conn.cursor() as cursor:
        select_query = "SELECT name, timestamp FROM attendance"
        cursor.execute(select_query)
        attendance_records = cursor.fetchall()

        if len(attendance_records) == 0:
            messagebox.showinfo("Attendance Records", "No attendance records found.")
        else:
            attendance_text = "Attendance Records:\n"
            for record in attendance_records:
                name, timestamp = record
                attendance_text += f"Name: {name} | Timestamp: {timestamp}\n"
            messagebox.showinfo("Attendance Records", attendance_text)

# Load the face cascade for face detection (optional)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Function to capture an image from the webcam and mark attendance
def capture_image_and_mark_attendance():
    video_capture = cv2.VideoCapture(0)

    if not video_capture.isOpened():
        messagebox.showerror("Error", "Failed to open webcam.")
        return

    start_time = time.time()
    captured_image = None
    
    while True:
        ret, frame = video_capture.read()

        if not ret:
            messagebox.showerror("Error", "Failed to capture video frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the frame
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # Draw rectangles around the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # Display the resulting frame
        cv2.imshow('Video', frame)

        # Check if the timer has elapsed
        elapsed_time = time.time() - start_time
        if elapsed_time >= 10:
            captured_image = frame
            break

        # Wait for the 'q' key to be pressed to capture the image
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture object
    video_capture.release()
    cv2.destroyAllWindows()

    # Extract face embeddings from the captured image
    face_embeddings = get_face_embeddings(captured_image)

    # Check if a face exists in the database and mark attendance
    if len(face_embeddings) > 0:
        name = check_attendance(face_embeddings[0])  # Assuming only one face is captured
        if name is not None:
            messagebox.showinfo("Attendance Marked", f"Hi {name}, your attendance has been marked.")
            mark_attendance(name)
        else:
            messagebox.showinfo("Unknown Face", "Your face is not recognized.")

# Capture an image from the webcam and mark attendance
capture_image_and_mark_attendance()

# View attendance records
view_attendance()

# Close the database connection
conn.close()
