import os

from faster_whisper import WhisperModel

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
WHISPER_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
_model: WhisperModel | None = None
_LANGUAGE_CODES = {"english": "en", "hindi": "hi"}


def load_model() -> WhisperModel:
    global _model

    if _model is None:
        print(f"Loading Whisper model: {WHISPER_MODEL} ...")
        _model = WhisperModel(
            WHISPER_MODEL,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
        )
        print("Whisper model loaded.")
    return _model

def transcribe_chunk(chunk_path: str, language: str = "english") -> str:
    language_code = _LANGUAGE_CODES.get(language.strip().lower(), language.strip().lower())
    segments, _ = load_model().transcribe(chunk_path, language=language_code)
    return " ".join(segment.text.strip() for segment in segments).strip()

def transcribe_all(chunks: list[str], language: str = "english") -> str:
    transcripts = []

    for i, chunk in enumerate(chunks):

        print(f"Transcribing chunk {i + 1}/{len(chunks)}...")

        transcripts.append(transcribe_chunk(chunk, language=language))

    print("Transcription complete.")

    return " ".join(transcripts).strip()