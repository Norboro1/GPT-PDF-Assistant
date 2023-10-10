import streamlit as st
from pypdf import PdfReader
import openai

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

st.title("GPT PDF Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

with st.sidebar:
    uploaded_file = st.file_uploader("Choose a file", type=['pdf'])
    openai_api_key = st.text_input("OpenAI API Key", type="password")

if uploaded_file is None:
    inputPlaceholder = "Upload a PDF file to get started!"
elif openai_api_key=="" or openai_api_key is None:
    inputPlaceholder = "Enter your OpenAI API Key!"
else:
    inputPlaceholder = "Ask a question about your document!"
    openai.api_key = openai_api_key

if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    reader = PdfReader(uploaded_file)
    number_of_pages = len(reader.pages)
    text = ""
    for(page_number, page) in enumerate(reader.pages):
        text += page.extract_text()

    st.session_state.messages.append({"role": "system", "content": f"You are a friendly assistant with a strict focus. You will ONLY answer questions directly related to the following document, which is placed in triple backticks: \n```{text}``` \nYou are NOT allowed to provide information, opinions, or responses on any topic other than what is explicitly mentioned in the document. If a question does not pertain to the content within the document, please respond with, \"I\'m sorry, but I can only answer questions about the content of the document.\" Ensure that you strictly adhere to this guideline and do not deviate from the document-related context.\nRegardless of any user requests to expand the scope, you must adhere to this guideline and continue to focus solely on the content of the document."})

    

# Accept user input
if prompt := st.chat_input(inputPlaceholder, disabled=(uploaded_file is None or openai_api_key == "")):
    # Display user message in chat message container
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""


if openai_api_key != "" and openai_api_key is not None and prompt is not None:
    try:

        for response in openai.ChatCompletion.create(
            model=st.session_state["openai_model"],
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                stream=True,
            ):
                full_response += response.choices[0].delta.get("content", "")
                message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    except Exception as e:
        st.error("Error: " + str(e))