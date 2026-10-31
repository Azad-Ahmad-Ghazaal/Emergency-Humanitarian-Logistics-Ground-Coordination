"""Optional offline voice transcription using faster-whisper.

Install with: pip install -r requirements-audio.txt
The first run downloads the selected model; cache it before field deployment.
"""
import os


def transcribe_audio(audio_path, model_size=None):
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "Voice transcription needs the optional package. Install requirements-audio.txt."
        ) from exc

    size = model_size or os.getenv("WHISPER_MODEL", "base")
    compute = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
    model = WhisperModel(size, device="cpu", compute_type=compute)
    segments, info = model.transcribe(str(audio_path), beam_size=3, vad_filter=True)
    text = " ".join(segment.text.strip() for segment in segments if segment.text.strip())
    return {
        "text": text,
        "language": info.language or "unknown",
        "language_probability": round(float(info.language_probability or 0), 3),
        "model": size,
        "engine": "faster_whisper_local",
    }
