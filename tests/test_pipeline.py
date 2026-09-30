import unittest
from unittest.mock import Mock, patch

import audio_processor
from core import transcribe


class AudioProcessorTests(unittest.TestCase):
    @patch("audio_processor.chunk_audio", return_value=["chunk.wav"])
    @patch("audio_processor.convert_to_wav", return_value="converted.wav")
    @patch("audio_processor.download_youtube_audio", return_value="download.wav")
    def test_processes_youtube_url(self, download, convert, chunk):
        result = audio_processor.process_input("https://example.com/video")

        self.assertEqual(result, ["chunk.wav"])
        download.assert_called_once_with("https://example.com/video")
        convert.assert_called_once_with("download.wav")
        chunk.assert_called_once_with("converted.wav", 10)

    @patch("audio_processor.chunk_audio", return_value=["chunk.wav"])
    @patch("audio_processor.convert_to_wav", return_value="converted.wav")
    @patch("audio_processor.download_youtube_audio")
    def test_processes_local_audio_without_download(self, download, convert, chunk):
        result = audio_processor.process_input("recording.mp3", chunk_minutes=5)

        self.assertEqual(result, ["chunk.wav"])
        download.assert_not_called()
        convert.assert_called_once_with("recording.mp3")
        chunk.assert_called_once_with("converted.wav", 5)


class TranscriptionTests(unittest.TestCase):
    def test_transcribes_and_joins_chunks(self):
        model = Mock()
        model.transcribe.side_effect = [
            (iter([Mock(text=" first ")]), object()),
            (iter([Mock(text=" second ")]), object()),
        ]

        with patch.object(transcribe, "load_model", return_value=model):
            result = transcribe.transcribe_all(["one.wav", "two.wav"], "English")

        self.assertEqual(result, "first second")
        self.assertEqual(
            model.transcribe.call_args_list,
            [
                unittest.mock.call("one.wav", language="en"),
                unittest.mock.call("two.wav", language="en"),
            ],
        )


if __name__ == "__main__":
    unittest.main()