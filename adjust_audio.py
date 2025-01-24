import subprocess

def convert_audio(audio_file_path):
    """
    Converts any audio file to 16-bit PCM and resamples to 16000 Hz.

    Args:
        audio_file_path: The path to the input audio file.

    Returns:
        The path to the converted audio file.
    """
    converted_file_path = "converted_audio.wav"
    
    subprocess.run(
        [
            "ffmpeg",
            "-i",
            audio_file_path,  # Input file
            "-acodec",
            "pcm_s16le",  # Convert to 16-bit PCM
            "-af",
            "aresample=resampler=soxr",
            "-ar",
            "16000",  # Resample to 16000 Hz
            "-ac", 
            "1",  # Convert to mono
            "-f",
            "wav",  # Output format (WAV)
            converted_file_path  # Specific output file path
        ],
        check=True,
    )

    return converted_file_path