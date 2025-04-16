import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from google.cloud import speech, texttospeech
from PyPDF2 import PdfReader
import logging
import vertexai
from vertexai.preview.generative_models import GenerativeModel

# --- Configuration ---
BOOK_TEXT_FILE = 'uploads/book_text.txt'
PROJECT_ID = "renne-cot5930-sp25-final-proj"
LOCATION = "us-central1"

# --- Initialize Flask ---
app = Flask(__name__)

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Initialize Google Cloud Clients ---
speech_client = speech.SpeechClient()
tts_client = texttospeech.TextToSpeechClient()
vertexai.init(project=PROJECT_ID, location=LOCATION)
gemini_model = GenerativeModel("gemini-1.5-pro-002")

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    try:
        pdf = request.files.get('pdf')
        if not pdf or pdf.filename == '':
            return jsonify({"error": "No PDF uploaded"}), 400

        os.makedirs('uploads', exist_ok=True)
        pdf_path = os.path.join('uploads', pdf.filename)
        pdf.save(pdf_path)
        logger.info(f"Saved PDF to {pdf_path}")

        reader = PdfReader(pdf_path)
        book_text = "\n".join([page.extract_text() or "" for page in reader.pages])

        with open(BOOK_TEXT_FILE, 'w', encoding='utf-8') as f:
            f.write(book_text)

        return jsonify({
            "message": "PDF uploaded and parsed successfully",
            "filename": pdf.filename
        })

    except Exception as e:
        logger.exception("Error during PDF upload")
        return jsonify({"error": f"Failed to process PDF: {str(e)}"}), 500

@app.route('/upload', methods=['POST'])
def upload_audio():
    try:
        audio_file = request.files.get('audio_data')
        if not audio_file or audio_file.filename == '':
            return jsonify({"error": "No audio file uploaded"}), 400

        os.makedirs('uploads', exist_ok=True)
        audio_path = os.path.join('uploads', audio_file.filename)
        audio_file.save(audio_path)
        logger.info(f"Saved audio to {audio_path}")

        transcript = transcribe_audio(audio_path)
        book_content = load_book_content()
        answer = generate_answer(transcript, book_content)
        audio_filename = synthesize_speech(answer)
        audio_url = f"/static/{audio_filename}"
        logger.info(f"Synthesized answer saved as {audio_url}")

        return jsonify({
            "message": "Processed successfully",
            "result": transcript,
            "answer": answer,
            "audio_url": audio_url
        })

    except Exception as e:
        logger.exception("Processing error:")
        return jsonify({"error": str(e)}), 500

@app.route('/static/<path:filename>')
def serve_static_file(filename):
    return send_from_directory('static', filename)

# --- Utility Functions ---

def transcribe_audio(audio_path):
    with open(audio_path, "rb") as f:
        audio_content = f.read()

    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
        language_code="en-US",
    )

    response = speech_client.recognize(config=config, audio=audio)
    transcript = " ".join([r.alternatives[0].transcript for r in response.results])
    return transcript.strip() or "No transcription found."

def load_book_content():
    with open(BOOK_TEXT_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def generate_answer(transcript, book_content):
    prompt = f"""
You are a helpful assistant. Based on the following book content, answer the user's question.

Book:
{book_content[:4000]}

User's question:
{transcript}

Answer:
"""
    response = gemini_model.generate_content(prompt)
    return response.text.strip()

def synthesize_speech(text):
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    response = tts_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    os.makedirs('static', exist_ok=True)
    filename = f"response_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
    path = os.path.join("static", filename)
    with open(path, "wb") as out:
        out.write(response.audio_content)

    return filename

# --- Run Server ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
