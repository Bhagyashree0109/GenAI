from groq import Groq
import streamlit as st

st.set_page_config(page_icon="🤖", layout="wide")
st.title('LeetCode Helper Chatbot 🤖')

client = Groq(
    api_key=st.secrets["GROQ_API_KEY"],
)

# Set a default model
if "groq_input_model" not in st.session_state:
    st.session_state["groq_input_model"] = "whisper-large-v3"

if "groq_output_model" not in st.session_state:
    st.session_state["groq_output_model"] = "llama3-8b-8192"
 
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def transcribe_speech(file):
    """Transcribe speech from an audio file using Whisper."""
    # Check the file type
    st.write(f"File type: {file.type}")
    st.write(f"File name: {file.name}")
    st.write(f"File size: {file.size}")

    # Read the file content
    file_content = file.read()
    st.write(f"File content size: {len(file_content)} bytes")

    # Check the file extension
    file_extension = file.name.split('.')[-1]
    st.write(f"File extension: {file_extension}")

    # Prepare the file tuple with content type
    file_tuple = (file.name, file_content, file.type)

    # Debug the file tuple
    # st.write(f"File tuple: {file_tuple}")

    # Send the request to the Groq API
    try:
        translation = client.audio.translations.create(
            file=file_tuple,
            model=st.session_state["groq_input_model"],
            response_format="json"
        )
        return translation.text
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def generate_text(description):
    """Generate text using Llama based on the transcribed description."""
    prompt = f"Generate a Python code snippet for the following task: {description}"
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=st.session_state["groq_output_model"]
    )
    return response.choices[0].message.content

# Audio file uploader
uploaded_file = st.file_uploader("Upload an audio file", type=["flac", "mp3", "mp4", "mpeg", "mpga", "m4a", "ogg", "opus", "wav", "webm"])

if uploaded_file is not None:
    with st.spinner("Transcribing speech..."):
        description = transcribe_speech(uploaded_file)
    if description:
        st.session_state.messages.append({"role": "user", "content": description})

        with st.chat_message("user"):
            st.markdown(description)

        with st.spinner("Generating response..."):
            response_content = generate_text(description)

        with st.chat_message("assistant"):
            st.markdown(response_content)
            
        st.session_state.messages.append({"role": "assistant", "content": response_content})

# Text input for prompts
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Perform the chat completion
    response = client.chat.completions.create(
        model=st.session_state["groq_output_model"],
        messages=[
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ],
    )

    response_content = response.choices[0].message.content

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response_content)
        
    st.session_state.messages.append({"role": "assistant", "content": response_content})






# # Set up API key and initialize the Groq client
# api_key = "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"
# client = Groq(api_key=api_key)

# def transcribe_speech(filename):
#     """Transcribe speech from an audio file using Whisper."""
#     with open(filename, "rb") as file:
#         translation = client.audio.translations.create(
#             file=(filename, file.read()),
#             model="whisper-large-v3",
#             response_format="json"
#         )
#         return translation.text

# def generate_text(description):
#     """Generate text using Llama based on the transcribed description."""
#     prompt = f"Generate a Python code snippet for the following task: {description}"
#     response = client.chat.completions.create(
#         messages=[{"role": "user", "content": prompt}],
#         model="llama3-8b-8192"
#     )
#     return response.choices[0].message.content

# def main():
#     if len(sys.argv) != 2:
#         print("Usage: python whisper.py <path_to_audio_file>")
#         sys.exit(1)

#     # Get the audio file path from command-line arguments
#     filename = sys.argv[1]

#     if not os.path.isfile(filename):
#         print(f"Error: The file {filename} does not exist.")
#         sys.exit(1)

#     # Transcribe the speech
#     try:
#         print("Transcribing speech...")
#         description = transcribe_speech(filename)
#         print("Transcription:", description)

#         # Generate text based on transcription
#         print("\nGenerating code snippet based on transcription...")
#         code_snippet = generate_text(description)
#         print("Generated Code Snippet:")
#         print(code_snippet)
#     except Exception as e:
#         print(f"An error occurred: {e}")

# if __name__ == "__main__":
#     main()
