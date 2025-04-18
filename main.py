import re
import base64
import streamlit as st
from ollama import chat
import re

# Set Streamlit page configuration
st.set_page_config(page_title="Ollama Streaming Chat", layout="centered")

# Format reasoning response
def format_reasoning_response(content):
    """Format the reasoning response."""
    return(
        thinking_content.replace("<think>\n\n<\think>","")
        .replace("<think>","")
        .replace("</think>","")
    )

# Display message
def display_message(message):
    """Display a message in the chat."""
    role = "user" if message["role"] == "user" else "assistant"
    with st.chat_message(role):
        if role == "user":
            display_assistant_message(message["content"])
        else:
            st.markdown(message["content"])

# Display assistant message
def display_assistant_message(content):
    """Display the assistant message."""
    pattern = r"<think>(.*?)</think>"
    think_match = re.search(pattern, content, re.DOTALL)
    if think_match:
        think_content = think_match.group(0)
        response_content = content.replace(think_content, "")
        think_content = format_reasoning_response(think_content)
        with st.expander("Reasoning"):
            st.markdown(think_content)
        st.markdown(response_content)
    else:
        st.markdown(content)

def display_chat_history():
    """Display the chat history."""
    for message in st.session_state["messages"]:
        if message["role"] != "system": # Skip system messages
            display_message(message)

# Process the thinking phase
def process_thinking_phase(stream):
    """Process the thinking phase of the assistant."""
    thinking_content = ""
    with st.status("Thinking...", expanded=True) as status:
        think_placeholder = st.empty()
        
        for chunk in stream:
            content = chunk["message"]["content"] or ""
            thinking_content += content

            if "<think>" in content:
                continue

            if "</think>" in content:
                content = content.replace("<think>", "")
                status.update(label="Thinking complete!", state="completed", expanded=False)
                break
            think_placeholder.markdown(format_reasoning_response(thinking_content))

    return thinking_content

# The response phase
def process_response_phase(stream):
    """Process the response phase of the assistant."""
    responce_placeholder = st.empty()
    response_content = ""
    for chunk in stream:
        content = chunk["message"]["content"] or ""
        response_content += content
        responce_placeholder.markdown(response_content)
    return response_content

# Setup the LLM
@st.cache_resource
def get_chat_model():
    """Get a cached instance of the chat model."""
    return lambda messages: chat(
        model="deepseek-r1",
        messages=messages,
        stream=True
    )

# Handle the user input
def handle_user_input():
    """Handle new user input"""
    if user_input := st.chat_input("Type your message here..."):
        st.session_state["messages"].append({"role": "user", "content": user_input})

        with st.chat_messages("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            chat_model = get_chat_model()
            stream = chat_model(st.session_state["messages"])

            thinking_content = process_thinking_phase(stream)
            response_content = process_response_phase(stream)

            # Save the complete response
            st.session_state["messages"].append(
                {"role": "assistant", "content": thinking_content + response_content}
            )

def main():
    """Main function to handle the chat inferface and streaming responses."""
    st.markdown("Mini ChatGPT", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;'>With thinking UI! 💡</h4>", unsafe_allow_html=True)

    display_chat_history()
    handle_user_input()
if __name__ == "__main__":
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "system", "content": "Welcome to the chat! 🤖"}
        ]
    main()







