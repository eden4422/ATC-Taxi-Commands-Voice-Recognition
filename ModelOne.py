from vosk import Model, KaldiRecognizer
import pyaudio
from queue import Queue 

def model_one(input_audio_Q: queue, output_text_queue, com_in, com_out):
    model = Model("voskModel1")
    recognizer = KaldiRecognizer(model)

    with input_audio_Q.get() as audio_file:
        data = audio_file.read()
        recognizer.AcceptWaveform(data)  # Accept the entire waveform

    result = recognizer.Result()
    output_text_queue.put(result)

if __name__ == "__main__":
    com_inQ = Queue()
    com_outQ = Queue()
    outputQ = Queue()
    
    audio = open("audio.wav")
    audioQ = Queue()
    audioQ.put(audio)
    model_one()

