from vosk import Model, KaldiRecognizer
from queue import Queue 
import wave
import json
import multiprocessing
import io

def trans_model(audio_tuple, model_link, output_text_queue, error_queue):
    try:
        model = Model(model_link)
        
        audio_data = audio_tuple[0]
        sample_rate = audio_tuple[1]

        print("modeloutput:")
        print(audio_data)

        recognizer = KaldiRecognizer(model, sample_rate)
        print(1)
        
        recognizer.SetWords(False)
        print(2)

        recognizer.AcceptWaveform(audio_data)  # Accept the entire waveform
        print(3)
        
        result = recognizer.Result()
        
        result_dict: dict = json.loads(result)
        
        output_text: str = result_dict['text']

        print(result)
        print(result_dict)

        print("modeloutput:")
        print(output_text)

        output_text_queue.put(output_text)

    except Exception as e:
        print(f"Error in model_one: {e}")

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

    test_process = multiprocessing.Process(trans_model,args=(audio_file_path,"vosk-model-small-en-us-0.15",outQ,errQ))
    test_process.start()
    #trans_model((audio_data,sample_rate),"vosk-model-small-en-us-0.15",outQ,errQ)



