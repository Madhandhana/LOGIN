import cv2
import streamlit as st
from PIL import Image
import time
from common import load_model, initialize_mediapipe, process_frame, send_to_backend, initialize_session_state, users_db

def sign_up_page(model, hands, labels_dict):
    """Display sign-up page and save the user's gesture."""
    st.title('Sign Up with Hand Gestures')

    # Initialize session state
    initialize_session_state()

    username = st.text_input('Enter Your Name')

    if username in users_db:
        st.warning("Name already exists. Please choose another name.")
        return

    if st.button('Start Camera to Set Gesture'):
        st.session_state.capturing = True
        st.session_state.detected_characters = []
        st.session_state.last_detection_time = time.time()  # Reset time on start
        st.session_state.last_detected_character = None  # Initialize last_detected_character

    if st.button('Stop Camera'):
        st.session_state.capturing = False

    if st.session_state.capturing:
        st.text('Capturing gestures... Press "Stop Camera" to end.')
        cap = cv2.VideoCapture(0)  # Use default camera index (change if needed)

        if not cap.isOpened():
            st.error("Error: Could not open video source.")
            return

        frame_placeholder = st.empty()
        detection_text_placeholder = st.empty()  # Placeholder for the detected characters text

        while st.session_state.capturing:
            ret, frame = cap.read()

            if not ret or frame is None:
                st.warning("Failed to capture frame.")
                continue

            try:
                frame, detected_character = process_frame(frame, hands, model, labels_dict)
                
                current_time = time.time()
                
                if detected_character and detected_character != st.session_state.last_detected_character:
                    if (current_time - st.session_state.last_detection_time) > 1:  # Detect character every 1 second
                        st.session_state.detected_characters.append(detected_character)
                        st.session_state.last_detection_time = current_time
                
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame_rgb)
                frame_placeholder.image(image, channels='RGB', use_column_width=True)
                
                detection_text_placeholder.text("Detected Characters: " + ''.join(st.session_state.detected_characters))
                st.session_state.last_detected_character = detected_character

            except Exception as e:
                st.error(f"Error during processing: {e}")
                continue

        cap.release()
        cv2.destroyAllWindows()

    # After stopping camera, display the Register button to store the user and gesture
    if len(st.session_state.detected_characters) > 0:
        gesture = ''.join(st.session_state.detected_characters)

        if st.button('Register'):
            # Save to in-memory storage and send gesture to backend
            users_db[username] = gesture
            send_to_backend(username, gesture, 'http://localhost:3000/signup')  # Adjust with correct URL
            st.success(f"User {username} registered successfully with gesture.")
            st.session_state.detected_characters = []
