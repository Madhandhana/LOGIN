import pickle
import cv2
import mediapipe as mp
import numpy as np
import requests
import streamlit as st
from PIL import Image
import time

import requests

def send_to_backend(username, gesture, endpoint):
    """Send data to the backend."""
    try:
        response = requests.post(endpoint, json={'username': username, 'gesture': gesture})
        response.raise_for_status()
        return response.json()  # Ensure response is returned for handling
    except requests.RequestException as e:
        st.error(f"Failed to send data to backend: {e}")
        return None

# In-memory user storage (or you can use a database)
users_db = {}

def load_model(model_path):
    """Load the trained model from a pickle file."""
    with open(model_path, 'rb') as file:
        model_dict = pickle.load(file)
    return model_dict['model']

def initialize_mediapipe():
    """Initialize and return MediaPipe Hands."""
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, min_detection_confidence=0.3)
    return hands

def process_frame(frame, hands, model, labels_dict):
    """Process each video frame and make predictions."""
    H, W, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    results = hands.process(frame_rgb)
    detected_character = None

    if results.multi_hand_landmarks:
        data_aux = []
        
        for hand_landmarks in results.multi_hand_landmarks:
            x_ = [lm.x for lm in hand_landmarks.landmark]
            y_ = [lm.y for lm in hand_landmarks.landmark]
            
            min_x, min_y = min(x_), min(y_)
            data_aux = [(lm.x - min_x, lm.y - min_y) for lm in hand_landmarks.landmark]
            
            # Flatten the list and ensure the length matches the model input
            data_aux = [item for sublist in data_aux for item in sublist]
            if len(data_aux) == 42:  # Adjust based on your model's requirement
                try:
                    prediction = model.predict([np.asarray(data_aux)])
                    detected_character = labels_dict[int(prediction[0])]
                    
                    x1 = int(min(x_) * W) - 10
                    y1 = int(min(y_) * H) - 10
                    x2 = int(max(x_) * W) + 10
                    y2 = int(max(y_) * H) + 10
                    
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 4)
                    cv2.putText(frame, detected_character, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 3, cv2.LINE_AA)
                    
                except Exception as e:
                    st.error(f"Prediction error: {e}")
                    
    return frame, detected_character

def send_to_backend(username, gesture, endpoint):
    """Send data to the backend for authentication."""
    try:
        response = requests.post(endpoint, json={'username': username, 'gesture': gesture})
        response.raise_for_status()
        response_data = response.json()
        if response_data.get('msg') == 'Login successful':
            st.success("Logged in successfully!")
            st.session_state.logged_in = True
            st.session_state.capturing = False
            st.session_state.detected_characters = []
        else:
            st.error(response_data.get('msg', 'Login failed'))
    except requests.RequestException as e:
        st.error(f"Failed to send data to backend: {e}")

def initialize_session_state():
    """Initialize the session state attributes if they don't exist."""
    if 'capturing' not in st.session_state:
        st.session_state.capturing = False
    if 'detected_characters' not in st.session_state:
        st.session_state.detected_characters = []
    if 'last_detection_time' not in st.session_state:
        st.session_state.last_detection_time = time.time()
    if 'last_detected_character' not in st.session_state:
        st.session_state.last_detected_character = None
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
