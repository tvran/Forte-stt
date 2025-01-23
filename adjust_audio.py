from pydub import AudioSegment

def convert_audio(audio_file_path):
    """
    Converts audio file to standard format for speech recognition.
    """
    converted_file_path = "converted_audio.wav"

    # Load the input file
    audio = AudioSegment.from_file(audio_file_path)

    # Resample to 16000 Hz and convert to mono
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

    # Export to WAV format
    audio.export(converted_file_path, format="wav")
    print("Audio successfully converted.")

    return converted_file_path
