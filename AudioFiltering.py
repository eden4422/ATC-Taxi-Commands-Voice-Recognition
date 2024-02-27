import numpy as np
import webrtcvad
import wave

def wav_to_raw_audio(wav_file_path):
    # Read the WAV file
    with wave.open(wav_file_path, 'rb') as wf:
        sample_width = wf.getsampwidth()
        audio_array = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)

    return audio_array, wf.getframerate()

def raw_audio_to_wav(raw_audio, sample_rate, output_file_path):
    # Ensure the raw_audio is a NumPy array of int16
    if not isinstance(raw_audio, np.ndarray) or raw_audio.dtype != np.int16:
        raise ValueError("raw_audio must be a NumPy array of int16")

    # Open a WAV file for writing
    with wave.open(output_file_path, 'wb') as wf:
        wf.setnchannels(1)  # Set to 1 for mono, 2 for stereo
        wf.setsampwidth(2)  # 2 bytes for int16
        wf.setframerate(sample_rate)
        wf.writeframes(raw_audio.tobytes())

def remove_background_noise(raw_audio, sample_rate):
    # Convert raw audio bytes to numpy array
    audio_array = np.frombuffer(raw_audio, dtype=np.int16)

    # Initialize VAD with the sample rate
    vad = webrtcvad.Vad()
    vad.set_mode(1)  # Set the VAD aggressiveness (0 to 3)

    # Define a function to split the audio into speech and non-speech segments
    def vad_segmentation(audio, sample_rate):
        frames = []
        frame_duration = 10  # Duration of each frame in milliseconds

        # Convert frame duration to number of samples
        frame_length = int(sample_rate * frame_duration / 1000)

        for start in range(0, len(audio), frame_length):
            end = min(start + frame_length, len(audio))
            frames.append(audio[start:end])

        return frames

    # Perform VAD segmentation
    segments = vad_segmentation(audio_array, sample_rate)

    # Filter out non-speech segments
    filtered_audio = np.concatenate([segment for segment in segments])

    return filtered_audio


# Converting wav file to raw
samp = wav_to_raw_audio("output1.wav")

# Filtering out background noise from raw audio
audio = remove_background_noise(samp[0], samp[1])

# Saving filtered audio to wav
raw_audio_to_wav(audio, samp[1], "output11.wav")