import streamlit as st
import requests

st.title("Text Input Example")
# Create the main container
main_container = st.container()
with main_container:
    # Add a header
    st.write("Enter some text:")
    # Create a rectangular box for the text input field
    with st.expander(label="Text Input Field"):
        user_text = stc.text_input(key="user_text", placeholder="Type something...")
        submit_button = stc.button(label="Submit")
        if submit_button:
            # Call the backend API when the button is clicked
            response = requests.post('https://your-backend-api.com/api/endpoint', json={'text': user_text})
            if response.status_code == 200:
                st.write("API call successful!")
            else:
                st.error("Error calling the API: " + response.text)
