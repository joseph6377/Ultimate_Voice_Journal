# Organize imports by standard library, third-party packages, then project-specific modules
import os
from dotenv import load_dotenv

import sounddevice as sd
from scipy.io.wavfile import write
import whispercpp
import simplenote
import google.generativeai as genai

# Constants
SAMPLE_RATE = 44100
DEFAULT_DURATION = 5
TEMP_AUDIO_FILENAME = 'temp_audio.wav'

# Load environment variables
load_dotenv()
api_key = os.getenv("API_KEY")


# Check and configure API key
def configure_api():
    if not api_key:
        raise ValueError("API_KEY not found in environment variables.")
    genai.configure(api_key=api_key)


# Record audio
def record_audio(duration=DEFAULT_DURATION, sample_rate=SAMPLE_RATE, filename=TEMP_AUDIO_FILENAME):
    print(f"Recording for {duration} seconds...")
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float64')
    sd.wait()  # Wait until recording is finished
    write(filename, sample_rate, recording)  # Save as WAV file
    print("Recording stopped.")


# Transcribe audio
def transcribe_audio(filename=TEMP_AUDIO_FILENAME):
    w = whispercpp.Whisper('base')
    result = w.transcribe(filename)
    transcription_text = ' '.join(w.extract_text(result))
    print(transcription_text)
    return transcription_text


# Generate summary using Google's generative AI
def generate_summary(text):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(text)
    return response.text


# Send transcription and summary to Simplenote
def send_to_simplenote(text, summary):
    username = os.getenv('SIMPLENOTE_USERNAME')
    password = os.getenv('SIMPLENOTE_PASSWORD')

    if not username or not password:
        raise ValueError("Simplenote credentials not found in environment variables.")

    sn = simplenote.Simplenote(username, password)
    note_content = f"Transcription: {text}\n\nSummary: {summary}"
    note = {'content': note_content}

    result = sn.add_note(note)
    if result[1] == 0:
        print("Note added successfully.")
    else:
        print("Failed to add note.")


# Main function to encapsulate script logic
def main():
    configure_api()

    try:
        user_input = input("Enter duration for recording in seconds (default is 5): ")
        duration = int(user_input) if user_input else DEFAULT_DURATION
    except ValueError:
        print("Invalid input. Using default duration.")
        duration = DEFAULT_DURATION

    record_audio(duration)
    transcription_text = transcribe_audio()
    gemini_input = "Summarize the following in 50 words:" + transcription_text
    summary_text = generate_summary(gemini_input)
    print(summary_text)
    send_to_simplenote(transcription_text, summary_text)


# Execute main function
if __name__ == "__main__":
    main()
