import os
import shutil
import subprocess
from pytube import YouTube
from pydub import AudioSegment
import speech_recognition as sr
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class CommandExecutor:
    """Handles command execution with error handling."""
    @staticmethod
    def run_command(command):
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Command execution failed: {e}")
            raise

class FileManager:
    """Handles file and directory operations."""
    @staticmethod
    def ensure_directory_exists(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    @staticmethod
    def file_exists(file_path):
        return os.path.exists(file_path)

    @staticmethod
    def delete_file(file_path):
        if os.path.exists(file_path):
            os.remove(file_path)

class YTDownloader:
    """Handles downloading of YouTube audio."""
    @staticmethod
    def ensure_yt_dlp():
        if not shutil.which("yt-dlp"):
            print("yt-dlp is not installed. Installing...")
            CommandExecutor.run_command(["pip", "install", "yt-dlp"])

    @staticmethod
    def download_audio(youtube_url, output_path="audio"):
        YTDownloader.ensure_yt_dlp()
        FileManager.ensure_directory_exists(output_path)

        print("Downloading audio using yt-dlp...")
        command = [
            "yt-dlp", "-f", "bestaudio[ext=m4a]", "--extract-audio",
            "--audio-format", "mp3", "-o", f"{output_path}/audio.%(ext)s", youtube_url
        ]
        CommandExecutor.run_command(command)

        audio_file = os.path.join(output_path, "audio.mp3")
        if not FileManager.file_exists(audio_file):
            raise FileNotFoundError("Audio file could not be downloaded.")

        print(f"Downloaded audio to {audio_file}")
        return audio_file

class AudioProcessor:
    """Handles audio processing tasks like splitting and transcription."""
    @staticmethod
    def split_audio(audio_file, chunk_length_ms=60000):
        try:
            audio = AudioSegment.from_file(audio_file)
            chunks = []
            for start in range(0, len(audio), chunk_length_ms):
                chunk = audio[start:start + chunk_length_ms]
                chunk_filename = f"chunk_{start // chunk_length_ms}.wav"
                chunk.export(chunk_filename, format="wav")
                chunks.append(chunk_filename)
            return chunks
        except Exception as e:
            print(f"Error splitting audio: {e}")
            raise

    @staticmethod
    def transcribe_audio(audio_file, language="bn-BD"):
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(audio_file) as source:
                audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data, language=language)
        except sr.UnknownValueError:
            return "Google Speech Recognition could not understand the audio."
        except sr.RequestError as e:
            return f"Could not request results from Google Speech Recognition service; {e}"
        except Exception as e:
            print(f"Error during transcription: {e}")
            raise

class YoutubeService:
    """High-level service class coordinating downloading, processing, and transcription."""
    def __init__(self):
        self.downloader = YTDownloader()
        self.audio_processor = AudioProcessor()

    def get_video_transcript(self, video_url):
        try:
            audio_path = self.downloader.download_audio(video_url)
            chunks = self.audio_processor.split_audio(audio_path)
            transcribed_text = "\n".join(
                self.audio_processor.transcribe_audio(chunk) for chunk in chunks
            )

            # Cleanup: Remove audio and chunk files
            FileManager.delete_file(audio_path)
            for chunk in chunks:
                FileManager.delete_file(chunk)
            return transcribed_text
        except Exception as e:
            print(f"Error in transcription service: {e}")
            raise