from groq import Groq
import streamlit as st
from audio_recorder_streamlit import audio_recorder

st.set_page_config(page_icon="🤖", layout="wide")
st.title('LeetCode Helper Chatbot 🤖')

client = Groq(
    api_key=st.secrets["GROQ_API_KEY"],
)

# Set default models
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
    # Read the file content
    file_content = file.read()
    file_tuple = (file.name, file_content, file.type)

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

def transcribe_audio_bytes(audio_bytes, file_name):
    """Transcribe audio bytes using Whisper."""
    file_tuple = (file_name, audio_bytes, "audio/wav")

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

# Option to upload audio file or record audio
st.header("Choose an input method:")
input_method = st.radio("Input Method", ("Upload an audio file", "Record using microphone"))

if input_method == "Upload an audio file":
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

elif input_method == "Record using microphone":
    if 'recording' not in st.session_state:
        st.session_state.recording = False

    if st.button("Start Recording"):
        st.session_state.recording = True

    # If recording is in progress, use the audio recorder
    if st.session_state.recording:
        audio_bytes = audio_recorder()

        # Check if audio was recorded
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            st.write("Audio recorded successfully!")
            st.session_state.recording = False  # Stop recording after audio is captured

            with st.spinner("Transcribing speech..."):
                description = transcribe_audio_bytes(audio_bytes, "recorded_audio.wav")
            if description:
                st.session_state.messages.append({"role": "user", "content": description})

                with st.chat_message("user"):
                    st.markdown(description)

                with st.spinner("Generating response..."):
                    response_content = generate_text(description)

                with st.chat_message("assistant"):
                    st.markdown(response_content)
                    
                st.session_state.messages.append({"role": "assistant", "content": response_content})
        else:
            st.write("Recording... Speak now.")
    else:
        st.write("Press the button to start recording audio.")

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
