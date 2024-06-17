import streamlit as st
import requests

st. title("About Jhansi Rani")
# Create the main container
main_container = st.container()
with main_container:
    # Add a header
    st.write("Enter some text:")
    # Create a rectangular box for the text input field
    with st.expander(label="Text Input Field"):
        user_text = st.text_input(key="user_text", placeholder="Type something...", label="")
        submit_button = st.button(label="Submit")
        if submit_button:
            # Call the backend API when the button is clicked
            response = requests.post('http://yetirocks:5000/query', json={'query': user_text})
            if response.status_code == 200:
                st.write("API call successful!")
            else:
                st.error("Error calling the API: " + response.text)

