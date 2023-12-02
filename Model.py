from vosk import Model, KaldiRecognizer
from queue import Queue 
import wave
import json
import multiprocessing
import io
import wave

def trans_model(input_audio: tuple, model_link, output_text_queue, error_queue):
    try:
        model = Model(model_link)
        
        audio_data = input_audio[0]
        framerate = input_audio[1]

        print("modeloutput:")
        print(audio_data)
        print(framerate)

        recognizer = KaldiRecognizer(model, framerate)
        print(1)
        recognizer.SetWords(False)
        print(2)
        recognizer.AcceptWaveform(audio_data)  # Accept the entire waveform
        
        print(3)
        result = recognizer.Result()
        print(result)
        resultDict: dict = json.loads(result)
        print(resultDict)
        resultText: str = resultDict["text"]
        print(resultText)
        
        output_text: str = resultDict['text']
        print(result)
        print(resultDict)
        print(resultText)

        print("modeloutput:")
        print(output_text)

        output_text_queue.put(output_text)

    except Exception as e:
        print(f"Error in model_one: {e}")

def main():
    pass

if __name__ == "__main__":
    audio_file_path = 'testaudio.wav'
    sample_rate: int
    audio_data: str

    # Read the audio file as binary data
    with wave.open(audio_file_path, 'rb') as audio_file:
        sample_rate = audio_file.getframerate()
        audio_data = audio_file.readframes(audio_file.getnframes())

    outQ = Queue()
    errQ = Queue()

    trans_model((audio_data,sample_rate),"vosk-model-small-en-us-0.15",outQ,errQ)