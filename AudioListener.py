import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import sys
import json

def audio_listener(plane_id: str, audio_segment_queue: queue, comm_in_queue: queue, comm_out_queue: queue):
    device_info = sd.query_devices(sd.default.device[0], 'input')
    samplerate = int(device_info['default_samplerate'])
    q = queue.Queue()

    def recordCallback(indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        q.put(bytes(indata))
    model = Model("voskModel1")
    recognizer = KaldiRecognizer(model, samplerate)
    recognizer.SetWords(False)

    print("===> Begin recording. Press Ctrl+C to stop the recording ")
    try:
        with sd.RawInputStream(dtype='int16',
                            channels=1,

                            callback=recordCallback):
            while True:
                data = q.get()        
                if recognizer.AcceptWaveform(data):
                    recognizerResult = recognizer.Result()
                    # convert the recognizerResult string into a dictionary  
                    resultDict = json.loads(recognizerResult)
                    if not resultDict.get("text", "") == "":
                        print(recognizerResult)
                    else:
                        print("no input sound")

    except KeyboardInterrupt:
        print('===> Finished Recording')
    except Exception as e:
        print(str(e))