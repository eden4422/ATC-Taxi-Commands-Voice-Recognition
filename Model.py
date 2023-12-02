from vosk import Model, KaldiRecognizer
from queue import Queue 
import wave
import json
import multiprocessing
import io

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
        print("modeloutput:")
        print(output_text)

        output_text_queue.put(output_text)

    except Exception as e:
        print(f"Error in model_one: {e}")

def main():
    try:
        # Read audio file
        audio_file_path = 'testAudio.wav'
        with wave.open(audio_file_path, 'rb') as wf:
            framerate = wf.getframerate()
            audio_data = wf.readframes(wf.getnframes())

        # Create queues for communication between processes
        output_text_queue = Queue()
        error_queue = Queue()

        # Replace 'your_model_link_here' with the actual link to your model
        model_link = 'your_model_link_here'

        # Create a tuple containing audio data and framerate
        input_audio = (audio_data, framerate)

        # Call the trans_model function in a separate process
        process = multiprocessing.Process(target=trans_model, args=(input_audio, model_link, output_text_queue, error_queue))
        process.start()
        process.join()

        # Retrieve results from the queues
        output_text = output_text_queue.get()
        error_message = error_queue.get()

        if error_message:
            print(f"Error: {error_message}")
        else:
            print("Main function output:")
            print(output_text)

    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == "__main__":
    main()