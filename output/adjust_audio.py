import subprocess

def convert_audio(audio_file_path):
    """
    Converts any audio file to 16-bit PCM and resamples to 16000 Hz.

    Args:
        audio_file_path: The path to the input audio file.

    Returns:
        The converted audio data as bytes.
    """
    process = subprocess.run(
        [
            "ffmpeg",
            "-i",
            audio_file_path,  # Input file
            "-acodec",
            "pcm_s16le",  # Convert to 16-bit PCM
            "-ar",
            "16000",  # Resample to 16000 Hz
            "-f",
            "wav",  # Output format (WAV)
            "-",  # Output to stdout
        ],
        capture_output=True,
        check=True,
    )

    # Get converted audio data from stdout
    converted_audio = process.stdout

    return converted_audio