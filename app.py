import streamlit as st
from emoji import run_emoji_recognition
from calc import run_calculator
from sequence import run_sequence_recognition  # Make sure this import works correctly

def main():
    st.title('Gesture Recognition App')

    # Sidebar for mode selection
    option = st.sidebar.selectbox("Select Mode", ["Emoji Recognition", "Calculator", "Sequence Recognition"])

    # Conditional execution based on the selected option
    if option == "Emoji Recognition":
        run_emoji_recognition()
    elif option == "Calculator":
        run_calculator()
    elif option == "Sequence Recognition":
        run_sequence_recognition()

if __name__ == "__main__":
    main()
