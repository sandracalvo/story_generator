import os
import streamlit as st
from dotenv import load_dotenv
from st_audiorec import st_audiorec

from google.cloud import texttospeech
from google.cloud import speech_v1 as speech
from google.cloud.speech_v1 import types
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from vertexai.preview.generative_models import GenerativeModel 


# Load environment variables (including your Google Cloud project ID)
load_dotenv()
project_id = "YOUR_PROJECT_ID"

# Authenticate with Google Cloud 
vertexai.init(project=project_id, location="us-central1")  # Update region if needed

# Load the Gemini Pro model
model = GenerativeModel("gemini-1.0-pro-001")  # Replace with the correct model name

# Function to generate speech from text
def generate_speech(text):
    client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code='es-ES', 
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL 
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)
    with open('output.mp3', 'wb') as out:
        out.write(response.audio_content)

# Configure Streamlit page settings
st.set_page_config(
    page_title="Cuentacuentos IA",
    page_icon=":book:",  
    layout="centered",  
)
# Display the chatbot's title
st.title("Cuentacuentos IA :book:")

# Function to translate roles between Gemini-Pro and Streamlit terminology
def translate_role_for_streamlit(user_role):
    if user_role == "model":
        return "assistant"
    else:
        return user_role

# Initialize chat session if not already present
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Display the chat history
for message in st.session_state.chat_session.history:
    with st.chat_message(translate_role_for_streamlit(message.role)):
        st.markdown(message.parts[0].text)

# Get the user's message
character_name = st.text_input("¿Como se llama el/la protagonista?")
sidekick_name = st.text_input("¿Como se llama su mascota? ¿Que es?")
favorite_activity = st.text_input("¿Que le gusta hacer a tu personaje favorito?")

# Button to generate the story
if st.button("¡Generar historia!"):
    # Input field for user's message
    story_prompt = f"""Eres un escritor reconocido de libros infantiles. Crea una historia corta usando estos elementos:
    * Personaje Principal: {character_name}
    * Mejor amigo/a o mascota: {sidekick_name}
    * Actividad favorita: {favorite_activity}
    El público objetivo son niños de 3 a 8 años. """ 

    print("Story prompt:", story_prompt)

    if story_prompt:
        # Add user's message to chat and display it
        st.chat_message("user").markdown(story_prompt)

        # Send user's message to Gemini-Pro and get the response
        gemini_response = st.session_state.chat_session.send_message(story_prompt)

        # Display Gemini-Pro's response
        with st.chat_message("assistant"):
            st.markdown(gemini_response.text) 

        # Text-to-speech for responses (correctly indented)
        if gemini_response:  # Check if you have a response
            with st.spinner("Generando audio de la historia..."):
                generate_speech(gemini_response.text)  # Read the saved text
            audio_file = open('output.mp3', 'rb')
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/mp3')
