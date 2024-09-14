import cv2
import streamlit as st
from PIL import Image
import time
from common import process_frame, initialize_session_state, send_to_backend

def login_page(model, hands, labels_dict):
    """Display login page and authenticate the user using gesture."""
    st.title('Login with Hand Gestures')

    # Initialize session state
    initialize_session_state()

    username = st.text_input('Enter Your Name')

    if st.button('Start Camera to Authenticate'):
        if not username:
            st.warning("Please enter your username.")
            return

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

                # Check if detected characters match the stored password
                detected_gesture = ''.join(st.session_state.detected_characters)
                if detected_gesture:
                    response = send_to_backend(username, detected_gesture, 'http://localhost:3000/login')
                    
                    if response and response.get('msg') == 'Login successful':
                        st.session_state.logged_in = True
                        st.success("Logged in successfully!")
                        st.session_state.capturing = False
                        st.session_state.detected_characters = []
                        break  # Exit loop after successful login
                    elif response and response.get('msg') == 'User not found':
                        st.warning("Username not found. Please check or sign up first.")
                        st.session_state.capturing = False
                    elif response and response.get('msg') == 'Invalid credentials':
                        st.warning("Invalid gesture. Please try again.")
                        st.session_state.detected_characters = []
                    
            except Exception as e:
                st.error(f"Error during processing: {e}")
                continue

        cap.release()
        cv2.destroyAllWindows()

    if st.session_state.logged_in:
        st.title('You are logged in!')
        # Add any additional functionality for logged-in users here
