import cv2
import dlib
import numpy as np
from sqlalchemy.orm import Session
from src.user_registration.model import Users
import base64

class FaceRecognition:
    def __init__(self, db: Session):
        self.db = db
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("src/ml_model/face_related/face_models/shape_predictor_68_face_landmarks.dat")
        self.facerec = dlib.face_recognition_model_v1("src/ml_model/face_related/face_models/dlib_face_recognition_resnet_model_v1.dat")
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    def get_face_embeddings(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray)
        face_embeddings = []
        for face in faces:
            landmarks = self.predictor(gray, face)
            embedding = np.array(self.facerec.compute_face_descriptor(image, landmarks))
            face_embeddings.append(embedding)
        return face_embeddings

    def compute_distance(self, embedding1, embedding2):
        return np.linalg.norm(embedding1 - embedding2)

    def face_exists(self, embedding):
        users = self.db.query(Users).all()

        for user in users:
            existing_embedding = np.array(user.embedding)
            distance = self.compute_distance(embedding, existing_embedding)
            if distance < 0.6:
                return True, user.username

        return False, None

    def store_face_embeddings(self, name, embeddings):
        # Compute the average embedding
        avg_embedding = np.mean(embeddings, axis=0)
        avg_embedding_list = avg_embedding.tolist()

        exists, existing_name = self.face_exists(avg_embedding)
        if exists:
            print(f"Error: User '{existing_name}' already exists in the database.")
            return

        user = Users(username=name, embedding=avg_embedding_list)
        self.db.add(user)

    def convert_base64_to_image(self, base64_string):
        img_data = base64.b64decode(base64_string)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img

    def run_face_recognition(self, base64_images, name):
        images = [self.convert_base64_to_image(b64_img) for b64_img in base64_images]

        if len(images) == 4:
            face_embeddings = []
            for image in images:
                embeddings = self.get_face_embeddings(image)
                if len(embeddings) > 0:
                    face_embeddings.extend(embeddings)

            if len(face_embeddings) > 0:
                exists, existing_name = self.face_exists(face_embeddings[0])
                if exists:
                    print(f"Error: User '{existing_name}' already exists in the database.")
                elif not name:
                    print("Error: Name cannot be empty.")
                else:
                    self.store_face_embeddings(name, face_embeddings)

        else:
            print("Error: Four images are required for face embedding.")

        self.db.commit()
