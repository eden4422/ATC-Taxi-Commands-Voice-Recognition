from vosk import Model, KaldiRecognizer
from queue import Queue 
import wave

def model_one(input_audio_Q, output_text_queue, com_in, com_out):
    try:
        model = Model("vosk-model-small-en-us-0.15")
        print(1)

        audio = input_audio_Q.get()
        print(2)

        data = audio.readframes(audio.getnframes())
        print(3)

        recognizer = KaldiRecognizer(model, audio.getframerate())
        recognizer.AcceptWaveform(data)  # Accept the entire waveform
        print(4)

        result = recognizer.Result()
        print(5)

        output_text_queue.put(result)
        print(6)

    except Exception as e:
        print(f"Error in model_one: {e}")

if __name__ == "__main__":
    com_inQ = Queue()
    com_outQ = Queue()
    outputQ = Queue()

    audio = wave.open("testAudio.wav", 'rb')  # Note the 'rb' mode to open the WAV file in binary mode
    audioQ = Queue()
    audioQ.put(audio)
    print(audioQ)

    try:
        model_one(audioQ, outputQ, com_inQ, com_outQ)
    except Exception as e:
        print(f"Error in __main__: {e}")

    # Retrieve and print the content of outputQ
    while not outputQ.empty():
        print("Content of outputQ:", outputQ.get())