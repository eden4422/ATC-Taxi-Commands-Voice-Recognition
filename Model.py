from vosk import Model, KaldiRecognizer
from queue import Queue 
import wave
import json
import multiprocessing
import io

def trans_model(audio_tuple, model_link, output_text_queue, error_queue):
    try:
        print(f"Loading model from: {model_link}")
        model = Model(model_link)
        
        audio_data = audio_tuple[0]
        sample_rate = audio_tuple[1]

        recognizer = KaldiRecognizer(model, sample_rate)
        
        recognizer.SetWords(False)

        recognizer.AcceptWaveform(audio_data)  # Accept the entire waveform
        
        result = recognizer.Result()
        
        result_dict: dict = json.loads(result)
        
        output_text: str = result_dict['text']

        output_text_queue.put(output_text)

    except Exception:
        error_message = f"Error in trans_model: {model_link}"
        print(error_message)