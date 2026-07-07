import os
import base64
import numpy as np
import cv2
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D
from tensorflow.keras.optimizers import Adam

# ---------------- CONFIG ----------------
MODEL_PATH = os.path.join(settings.BASE_DIR, 'model.h5')
IMG_SIZE = 48
CLASSES = ['angry', 'disgusted', 'fearful', 'happy', 'neutral', 'sad', 'surprised']
STRESS_EMOTIONS = ['angry', 'disgusted', 'fearful', 'sad']

os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)


# ---------------- BUILD MODEL ----------------
def build_model():
    model = Sequential()
    model.add(Conv2D(32, (3, 3), activation='relu', input_shape=(48, 48, 1)))
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D((2, 2)))
    model.add(Dropout(0.25))
    model.add(Conv2D(128, (3, 3), activation='relu'))
    model.add(MaxPooling2D((2, 2)))
    model.add(Conv2D(128, (3, 3), activation='relu'))
    model.add(MaxPooling2D((2, 2)))
    model.add(Dropout(0.25))
    model.add(Flatten())
    model.add(Dense(1024, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(7, activation='softmax'))
    model.compile(
        loss='categorical_crossentropy',
        optimizer=Adam(learning_rate=0.0001),
        metrics=['accuracy']
    )
    return model


# ---------------- LOAD MODEL ----------------
model = build_model()
model.load_weights(MODEL_PATH)
print("✅ Model Loaded Successfully")

# ---------------- FACE DETECTOR ----------------
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)
print("✅ Face Cascade Loaded")


# ---------------- HELPER ----------------
def predict_emotion(img_path):
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Fix lighting differences with histogram equalization
    gray_eq = cv2.equalizeHist(gray)

    # Attempt 1: normal face detection
    faces = face_cascade.detectMultiScale(
        gray_eq, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )

    # Attempt 2: looser params
    if len(faces) == 0:
        faces = face_cascade.detectMultiScale(
            gray_eq, scaleFactor=1.05, minNeighbors=3, minSize=(20, 20)
        )

    face_found = len(faces) > 0

    if face_found:
        # Use the largest face
        faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
        x, y, w, h = faces[0]
        pad = int(min(w, h) * 0.1)
        img_h, img_w = gray_eq.shape
        x1 = max(0, x - pad)
        y1 = max(0, y - pad)
        x2 = min(img_w, x + w + pad)
        y2 = min(img_h, y + h + pad)
        roi = gray_eq[y1:y2, x1:x2]
    else:
        # Fallback: center crop
        h, w = gray_eq.shape
        mh, mw = h // 6, w // 6
        roi = gray_eq[mh:h - mh, mw:w - mw]

    resized = cv2.resize(roi, (IMG_SIZE, IMG_SIZE))
    arr = resized.astype('float32') / 255.0
    arr = np.expand_dims(np.expand_dims(arr, -1), 0)

    preds = model.predict(arr, verbose=0)[0]
    pred_idx = int(np.argmax(preds))
    emotion = CLASSES[pred_idx]
    confidence = round(float(preds[pred_idx]) * 100, 2)
    stress = "STRESSED 😤" if emotion in STRESS_EMOTIONS else "NOT STRESSED 😊"

    return emotion, confidence, stress, face_found


# ---------------- VIEWS ----------------

def home(request):
    return render(request, 'stress_app/index.html')


def predict(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        filepath = os.path.join(settings.UPLOAD_FOLDER, uploaded_file.name)

        with open(filepath, 'wb+') as dest:
            for chunk in uploaded_file.chunks():
                dest.write(chunk)

        emotion, confidence, stress, face_found = predict_emotion(filepath)
        image_url = settings.MEDIA_URL + 'uploads/' + uploaded_file.name

        return render(request, 'stress_app/result.html', {
            'emotion': emotion,
            'confidence': confidence,
            'stress': stress,
            'image_url': image_url,
            'face_found': face_found,
        })

    return HttpResponse("No file uploaded", status=400)


def webcam(request):
    return render(request, 'stress_app/webcam.html')


def predict_webcam(request):
    if request.method == 'POST':
        image_data = request.POST.get('image', '')

        if ',' in image_data:
            image_data = image_data.split(',')[1]

        image_bytes = base64.b64decode(image_data)
        filepath = os.path.join(settings.UPLOAD_FOLDER, 'webcam.jpg')

        with open(filepath, 'wb') as f:
            f.write(image_bytes)

        emotion, confidence, stress, face_found = predict_emotion(filepath)
        image_url = settings.MEDIA_URL + 'uploads/webcam.jpg'

        return render(request, 'stress_app/result.html', {
            'emotion': emotion,
            'confidence': confidence,
            'stress': stress,
            'image_url': image_url,
            'face_found': face_found,
        })

    return HttpResponse("Invalid request", status=400)
