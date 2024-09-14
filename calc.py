import pickle
import cv2
import mediapipe as mp
import numpy as np
import streamlit as st
from PIL import Image
import time

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

def process_frame_for_calculator(frame, hands, model, labels_dict):
    """Process each video frame and make predictions for calculator recognition."""
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
                except Exception as e:
                    st.error(f"Prediction error: {e}")
                    
    return frame, detected_character

def run_calculator():
    st.title('Hand Gesture Calculator')

    model = load_model('./model.p')
    hands = initialize_mediapipe()

    # Emoji mapping for gestures
    labels_dict = {0: 'A', 1: 'B', 2: 'C'}

    # Initialize session state for control
    if 'capturing_calculator' not in st.session_state:
        st.session_state.capturing_calculator = False
    if 'input_sequence' not in st.session_state:
        st.session_state.input_sequence = []
    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'last_detection_time_calculator' not in st.session_state:
        st.session_state.last_detection_time_calculator = 0

    start_button = st.button('Start Calculator')
    stop_button = st.button('Stop Calculator')
    
    if start_button:
        st.session_state.capturing_calculator = True
        st.session_state.input_sequence = []
        st.session_state.result = None
        st.session_state.last_detection_time_calculator = time.time()  # Reset time on start
    
    if stop_button:
        st.session_state.capturing_calculator = False

    if st.session_state.capturing_calculator:
        st.text('Capturing video... Press "Stop" to end.')
        cap = cv2.VideoCapture(0)  # Use default camera index (change if needed)

        if not cap.isOpened():
            st.error("Error: Could not open video source.")
            return

        frame_placeholder = st.empty()
        result_placeholder = st.empty()  # Placeholder for the calculation result
        
        while st.session_state.capturing_calculator:
            ret, frame = cap.read()

            if not ret or frame is None:
                st.warning("Failed to capture frame.")
                continue

            try:
                frame, detected_character = process_frame_for_calculator(frame, hands, model, labels_dict)
                
                current_time = time.time()
                
                if detected_character and detected_character not in st.session_state.input_sequence:
                    if (current_time - st.session_state.last_detection_time_calculator) > 1:  # Detect character every 1 second
                        st.session_state.input_sequence.append(detected_character)
                        st.session_state.last_detection_time_calculator = current_time

                # Display the current input sequence and result
                if st.session_state.input_sequence:
                    result = ''.join(st.session_state.input_sequence)
                    result_placeholder.text("Input Sequence: " + result)
                    
                    try:
                        # Calculate result based on input sequence
                        st.session_state.result = eval(result)
                        result_placeholder.text("Result: " + str(st.session_state.result))
                    except Exception as e:
                        st.error(f"Error in calculation: {e}")
                
                # Convert the frame to RGB and display
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame_rgb)
                frame_placeholder.image(image, channels='RGB', use_column_width=True)
                
            except Exception as e:
                st.error(f"Error during processing: {e}")
                continue

        cap.release()
        cv2.destroyAllWindows()
