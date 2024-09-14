import streamlit as st
from common import load_model, initialize_mediapipe, initialize_session_state
from newlogin import login_page

def main():
    model = load_model('./model.p')
    hands = initialize_mediapipe()
    labels_dict = {0: 'A', 1: 'B', 2: 'C', 3: 'Z'}  # Example labels

    st.sidebar.title("Menu")
    page = st.sidebar.selectbox("Choose Action", ["Login"])

    if page == "Login":
        login_page(model, hands, labels_dict)

    if st.session_state.get('logged_in', False):
        st.title('You are logged in!')
        # Add additional functionality for logged-in users here

if __name__ == "__main__":
    main()
