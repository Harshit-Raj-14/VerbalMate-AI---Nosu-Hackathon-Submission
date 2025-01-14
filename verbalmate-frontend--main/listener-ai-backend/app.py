import streamlit as st
import tempfile
import os
import google.generativeai as genai
from PIL import Image, ImageSequence
from dotenv import load_dotenv

load_dotenv()

# Configure Google API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)


# Path to your GIF file
gif_path = "cat.gif"

gif = Image.open(gif_path)

performance_prompt = '''
Analyze the transcription of a the conversation and provide a performance analysis. 
Include the following details(only mention the score out of 10 for all these parameters): Overall Score, Professionalism, Responsiveness, Clarity, Engagement. 
Write about your strength, weakness and suggestion in points for the conversation. 
Write key insights. Provide Actions to Take Next Time that you should take when you meet this person enxt time. 
Now write a small Conclusion. 
Put everything under proper headings.
            
'''
def transcribe_audio(audio_file_path):
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    audio_file = genai.upload_file(path=audio_file_path)
    response = model.generate_content(
        [
            "Transcribe the following audio as a conversation between you and person 1. Mark the dialogues as you and person 1. Put a line space between each dialogue. Write nothing else.",
            audio_file
        ]
    )
    return response.text

def analyze_performance(transcription):
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    response = model.generate_content(
        [
            performance_prompt,transcription
        ]
    )
    return response.text

def save_uploaded_file(uploaded_file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.' + uploaded_file.name.split('.')[-1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error handling uploaded file: {e}")
        return None

# Streamlit app interface
st.title('VerbalMate AI')

# Initialize session state for transcription and performance analysis
if "transcription" not in st.session_state:
    st.session_state["transcription"] = None

if "performance" not in st.session_state:
    st.session_state["performance"] = None

audio_file = st.file_uploader("Upload Audio File", type=['wav', 'mp3'])
if audio_file is not None:
    audio_path = save_uploaded_file(audio_file)  # Save the uploaded file and get the path
    st.audio(audio_path)

    if st.button('Analyze Audio'):
        # Create a placeholder for the GIF
        gif_placeholder = st.empty()
        
        # Display the GIF
        frames = []
        for frame in ImageSequence.Iterator(gif):
            frames.append(frame.copy())
        gif_placeholder.image(frames[0], caption='Processing audio...')
        
        # Process the audio
        st.session_state["transcription"] = transcribe_audio(audio_path)
        st.session_state["performance"] = analyze_performance(st.session_state["transcription"])
        
        # Clear the GIF after processing
        gif_placeholder.empty()

# Add toggle buttons for switching between panes
if st.session_state["transcription"] and st.session_state["performance"]:
    pane = st.radio("Choose an output view:", ("Transcription", "Performance Analysis"))

    if pane == "Transcription":
        st.subheader("Transcription Pane")
        st.markdown(st.session_state["transcription"], unsafe_allow_html=True)

    elif pane == "Performance Analysis":
        st.markdown(st.session_state["performance"], unsafe_allow_html=True)
