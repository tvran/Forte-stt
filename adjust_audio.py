def convert_audio(audio_file_path):
    """
    Converts audio file to standard format for speech recognition
    """
    converted_file_path = "converted_audio.wav"
    
    subprocess.run(
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
            "-af",
            "aresample=resampler=soxr",  # High-quality resampling
            "-f",
            "wav",  # Output format (WAV)
            converted_file_path  # Specific output file path
        ],
        check=True,
    )

    return converted_file_path