# AI Video Assistant

Download audio from a YouTube URL or process a local audio file, split it into
chunks, and transcribe it locally with faster-whisper.

## Setup

Use Python 3.10 or newer and install FFmpeg so `pydub` can convert audio.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run the sample

```powershell
python test.py
```

The sample URL is set in `test.py`. Replace its `source` value to process a
different YouTube video or a local audio file. The first run downloads the
configured Whisper model.

The model defaults to `base` on CPU using `int8`. Override these settings with
`WHISPER_MODEL`, `WHISPER_DEVICE`, and `WHISPER_COMPUTE_TYPE` environment
variables.

## Run tests

```powershell
python -m unittest discover -s tests -v
```

Keep browser cookies, API keys, virtual environments, and downloaded media out
of Git. The project `.gitignore` excludes the local cookies file and generated
files.