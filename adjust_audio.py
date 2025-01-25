import os
import subprocess

def convert_audio(audio_file_path):
    """
    Converts any audio file to 16-bit PCM and resamples to 16000 Hz.
    """
    converted_file_path = "converted_audio.wav"
    
    # Remove existing file to avoid prompts
    if os.path.exists(converted_file_path):
        os.remove(converted_file_path)
    
    subprocess.run(
        [
            "ffmpeg",
            "-y",  # Overwrite output files without asking
            "-i",
            audio_file_path,
            "-ss", "00:00:03",  # Skip the first 3 seconds
            "-acodec",
            "pcm_s16le",
            "-af",
            "aresample=resampler=soxr",
            "-ar",
            "16000",
            "-f",
            "wav",
            converted_file_path
        ],
        check=True,
    )

    return converted_file_path