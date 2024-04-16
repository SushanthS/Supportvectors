import streamlit as st
import requests
import ast

url = 'http://127.0.0.1:9909/query'
data = {'query': 'what is udp'}

st.header("Enter your query")

#adding a single-line text input widget
text = st.text_input('')
#text = st.text_input('Enter your query: ', '')
data = {'query': text}
print(data)



def click_button():
    # Send POST request with FORM data using the data parameter
    response = requests.post(url, json=data, headers={"Content-Type":"application/json"})

    # Print the response
    output = response.json()
    print(output)

    # write output in UI
    st.write(output)

    st.session_state.clicked = True



st.button('Send', on_click=click_button)
