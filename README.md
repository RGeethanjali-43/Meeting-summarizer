🎥 Meeting Summarizer

A Python-based application that automatically summarizes meeting videos and PDFs using AI.
It combines speech-to-text transcription with large language model summarization to provide concise, easy-to-understand meeting notes.

Features

Upload meeting videos (MP4, MOV, AVI, MKV) and get a summarized transcript.

Upload PDF documents and generate concise summaries.

Uses MoviePy to extract audio from videos.

Transcribes audio using Groq Whisper (speech-to-text).

Summarizes transcripts with Groq LLaMA to remove repetition and provide a clear explanation.

Streamlit frontend with session management for smooth user experience.

RESTful Flask backend handles transcription and summarization.

Tech Stack

Python 3.12+

MoviePy – video/audio processing

Groq SDK – Whisper & LLM models

Flask – backend API

Streamlit – interactive frontend

dotenv – API key management

How It Works

User uploads a video or PDF via the frontend.

For videos, audio is extracted and transcribed to text.

The raw transcript is sent to an LLM for summarization.

The summarized text is returned to the frontend for display.