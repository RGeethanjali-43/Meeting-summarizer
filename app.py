from flask import Flask, request, jsonify
from moviepy import VideoFileClip
from groq import Groq
import os
from dotenv import load_dotenv
import tempfile
import PyPDF2

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- VIDEO HANDLER ---
def transcribe_and_summarize(video_path: str) -> str:
    """Extracts audio, transcribes, and summarizes the meeting."""
    video = VideoFileClip(video_path)
    audio = video.audio

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio:
        audio.write_audiofile(tmp_audio.name, codec="pcm_s16le", fps=16000)
        audio_path = tmp_audio.name

    video.close()

    # Transcribe audio
    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3"
        )

    text = transcript.text

    # Summarize transcript
    response = client.chat.completions.create(
        model="llama3-8b-8192",  # or "mixtral-8x7b-32768"
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes meeting transcripts clearly and concisely."},
            {"role": "user", "content": f"Here is a meeting transcript (may contain repetition). Please summarize it in simple, clear language:\n\n{text}"}
        ],
        temperature=0.3,
        max_tokens=500
    )

    return response.choices[0].message.content


# --- PDF HANDLER ---
def summarize_pdf_text(text: str) -> str:
    """Summarizes extracted PDF text using Groq LLM."""
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes PDF documents clearly and concisely."},
            {"role": "user", "content": f"Here is a PDF document. Summarize it in simple, clear language:\n\n{text}"}
        ],
        temperature=0.3,
        max_tokens=500
    )
    return response.choices[0].message.content


# --- ROUTES ---
@app.route("/summarize", methods=["POST"])
def summarize():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_video:
        file.save(tmp_video.name)
        video_path = tmp_video.name

    try:
        summary = transcribe_and_summarize(video_path)
        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/summarize_pdf", methods=["POST"])
def summarize_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""

        summary = summarize_pdf_text(text)
        return jsonify({"summary": summary})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
