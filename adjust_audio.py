import soundfile as sf
import numpy as np
from scipy.signal import resample

def convert_audio(audio_file_path):
    """
    Convert audio to mono, 16kHz using soundfile and scipy
    """
    converted_file_path = "converted_audio.wav"
    
    # Read the audio file
    data, original_sr = sf.read(audio_file_path)
    
    # Convert to mono if stereo
    if len(data.shape) > 1:
        data = data.mean(axis=1)
    
    # Resample to 16000 Hz
    num_samples = int(len(data) * 16000 / original_sr)
    resampled_data = resample(data, num_samples)
    
    # Write the converted audio
    sf.write(converted_file_path, resampled_data, 16000)
    
    return converted_file_path