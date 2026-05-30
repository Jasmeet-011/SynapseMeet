"""Transcription service — OpenAI Whisper + AssemblyAI speaker diarization."""

import asyncio
from pathlib import Path

import openai

from app.core.config import settings

openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def transcribe_audio(audio_path: str | Path) -> dict:
    """
    Transcribe an audio file using OpenAI Whisper.

    Returns:
        {
            "text": str,              # Full transcript
            "segments": [...],        # Timestamped segments
            "language": str           # Detected language
        }
    """
    with open(audio_path, "rb") as f:
        response = await openai_client.audio.transcriptions.create(
            model=settings.WHISPER_MODEL,
            file=f,
            response_format="verbose_json",
            timestamp_granularities=["segment", "word"],
        )

    return {
        "text": response.text,
        "segments": [s.model_dump() for s in response.segments] if response.segments else [],
        "language": response.language,
    }


async def transcribe_audio_chunk(audio_bytes: bytes, language: str = "en") -> str:
    """
    Transcribe a raw audio chunk (for real-time streaming via WebSocket).
    Used by the gateway to pipe 30-second chunks into Whisper.
    """
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        result = await transcribe_audio(tmp_path)
        return result["text"]
    finally:
        Path(tmp_path).unlink(missing_ok=True)


async def diarize_audio(audio_url: str) -> list[dict]:
    """
    Speaker diarization via AssemblyAI.
    Returns list of speaker-labeled utterances.

    NOTE: Requires ASSEMBLYAI_API_KEY in env.
    This is a placeholder — full implementation in Phase 5.
    """
    import assemblyai as aai

    aai.settings.api_key = settings.ASSEMBLYAI_API_KEY
    transcriber = aai.Transcriber()
    config = aai.TranscriptionConfig(speaker_labels=True)

    # AssemblyAI works with URLs (upload to GCS first in production)
    transcript = await asyncio.to_thread(transcriber.transcribe, audio_url, config=config)

    return [
        {
            "speaker": utterance.speaker,
            "text": utterance.text,
            "start": utterance.start,
            "end": utterance.end,
        }
        for utterance in (transcript.utterances or [])
    ]
