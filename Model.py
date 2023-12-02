from vosk import Model, KaldiRecognizer
from queue import Queue 
import wave
import json
import multiprocessing

def trans_model(input_audio: tuple, model_link, output_text_queue, error_queue):
    try:
        model = Model(model_link)
        
        audio_data = input_audio[0]
        framerate = input_audio[1]

        recognizer = KaldiRecognizer(model, framerate)
        recognizer.SetWords(False)
        recognizer.AcceptWaveform(audio_data)  # Accept the entire waveform
        
        result: dict = json.loads(recognizer.Result())

        output_text: str = result["text"]
        
        output_text_queue.put(output_text)

    except Exception as e:
        print(f"Error in model_one: {e}")

# Test script for individual testing
if __name__ == "__main__":
    com_inQ = multiprocessing.Queue()
    com_outQ = multiprocessing.Queue()
    outputQ = multiprocessing.Queue()

    audio = wave.open("testAudio.wav", 'rb')  # Note the 'rb' mode to open the WAV file in binary mode
    audioQ = multiprocessing.Queue()
    audioQ.put(audio)

    try:
        trans_model(audioQ, outputQ, com_inQ, com_outQ)
    except Exception as e:
        print(f"Error in __main__: {e}")

    # Retrieve and print the content of outputQ
    while not outputQ.empty():
        print("Content of outputQ:", outputQ.get())