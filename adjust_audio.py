import subprocess

def convert_audio(audio_file_path):
    """
    Converts any audio file to 16-bit PCM, resamples to 16000 Hz, and ensures mono output.

    Args:
        audio_file_path: The path to the input audio file.

    Returns:
        The path to the converted audio file.
    """
    converted_file_path = "converted_audio.wav"
    try:
        process = subprocess.run(
            [
                "ffmpeg",
                "-i",
                audio_file_path,  # Input file
                "-acodec",
                "pcm_s16le",  # Convert to 16-bit PCM
                "-ar",
                "16000",  # Resample to 16000 Hz
                "-ac",
                "1",  # Convert to mono
                "-f",
                "wav",  # Output format (WAV)
                converted_file_path  # Specific output file path
            ],
            stdout=subprocess.PIPE,  # Capture standard output
            stderr=subprocess.PIPE,  # Capture standard error
            check=True,  # Raise CalledProcessError for non-zero exit codes
        )
    except subprocess.CalledProcessError as e:
        # Handle errors and display helpful debugging information
        error_message = e.stderr.decode()
        raise RuntimeError(f"ffmpeg error:\n{error_message}")

    return converted_file_path