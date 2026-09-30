import argparse
import os
from pathlib import Path
from urllib.parse import urlparse

import yt_dlp
from pydub import AudioSegment

DOWNLOAD_DIR = 'downloades'
os.makedirs(DOWNLOAD_DIR,exist_ok = True)

def download_youtube_audio(
    url: str,
    browser: str | None = None,
    cookies_file: str | None = None,
) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }
    if browser:
        ydl_opts["cookiesfrombrowser"] = (browser,)
    if cookies_file:
        ydl_opts["cookiefile"] = cookies_file

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            source_path = Path(ydl.prepare_filename(info))
    except yt_dlp.utils.DownloadError as error:
        message = str(error)
        if "Sign in to confirm" in message or "429" in message:
            raise RuntimeError(
                "YouTube ne bot check lagaya hai. YouTube me login karke "
                "script ko --browser chrome ya --browser edge ke saath run karein."
            ) from error
        if "Could not copy Chrome cookie database" in message:
            raise RuntimeError(
                "Chrome cookies read nahi ho paaye. Chrome ki sabhi windows band "
                "karke command dobara run karein."
            ) from error
        if "Failed to decrypt with DPAPI" in message:
            raise RuntimeError(
                "Browser cookies decrypt nahi ho paaye. Firefox me YouTube login "
                "karke --browser firefox use karein, ya cookies.txt provide karein."
            ) from error
        raise RuntimeError(f"Audio download fail hua: {message}") from error

    return str(source_path.with_suffix(".wav"))


def convert_to_wav(input_path: str) -> str:
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(output_path, format="wav")
    return output_path

def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list[str]:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000

    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start:start + chunk_ms]
        chunk_path = os.path.splitext(wav_path)[0] + f"_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")

        chunks.append(chunk_path)

    return chunks


def process_input(source: str, chunk_minutes: int = 10) -> list[str]:
    if urlparse(source).scheme in {"http", "https"}:
        source_path = download_youtube_audio(source)
    else:
        source_path = source

    wav_path = convert_to_wav(source_path)
    return chunk_audio(wav_path, chunk_minutes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and prepare YouTube audio")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument(
        "--browser",
        choices=("chrome", "edge", "firefox", "brave", "chromium"),
        help="Use logged-in browser cookies when YouTube asks for sign-in",
    )
    parser.add_argument(
        "--cookies",
        dest="cookies_file",
        help="Path to an exported Netscape-format cookies.txt file",
    )
    args = parser.parse_args()

    try:
        downloaded_path = download_youtube_audio(args.url, args.browser, args.cookies_file)
        converted_path = convert_to_wav(downloaded_path)
        print("\n".join(chunk_audio(converted_path)))
    except RuntimeError as error:
        parser.error(str(error))