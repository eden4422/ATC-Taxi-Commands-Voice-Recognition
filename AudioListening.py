import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import sys
import json
import wave
from commands import MUTE
import fasteners

file_num = 0

def make_wav_file(_samplerate, _recording_data, _frame_limit):
    global file_num
    # Save the accumulated audio data to a WAV file
    with wave.open(f'output{file_num}.wav', 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(_samplerate)
        wf.writeframes(_recording_data[-_frame_limit:])
        file_num += 1
        if file_num == 100:
            file_num = 0

def listen_for_audio(audiobit_queue, audio_com_in, audio_com_out):
    muted = True
    # get the samplerate - this is needed by the Kaldi recognizer
    device_info = sd.query_devices(sd.default.device[0], 'input')
    samplerate = int(device_info['default_samplerate'])

    # display the default input device
    print("===> Initial Default Device Number:{} Description: {}".format(sd.default.device[0], device_info))

    # setup queue and callback function
    q = queue.Queue()

    def record_call_back(indata, frames, time, status):
        if not muted:
            if status:
                print(status, file=sys.stderr)
            q.put(bytes(indata))

    # build the model and recognizer objects.
    print("===> Build the model and recognizer objects.  This will take a few minutes.")
    model = Model("../vosk models/vosk-model-en-us-0.42-gigaspeech")
    recognizer = KaldiRecognizer(model, samplerate)
    recognizer.SetWords(True)

    desired_duration = 40  #10 = 5 seconds
    frame_limit = int(samplerate * desired_duration)


    print("===> Begin recording. Press Ctrl+C to stop the recording ")
    try:
        recording_data = b''  # Accumulate audio data

        with sd.RawInputStream(dtype='int16',
                            channels=1,
                            callback=record_call_back):
            previous_flight_json = {}
            lock = fasteners.InterProcessLock('flight_id.json.lock')
            while True:
                if not audio_com_in.empty():
                    _input = audio_com_in.get()
                    if _input[0] == MUTE:
                        muted = not muted
                if not q.empty():     
                    data = q.get()
                    recording_data += data  # Accumulate audio data
                    if recognizer.AcceptWaveform(data):
                        recognizer_result = recognizer.Result()
                        # convert the recognizerResult string into a dictionary
                        result_dict = json.loads(recognizer_result)
                        result_text: str = result_dict["text"]
                        audio_com_out.put(("allAudio", result_text))
                        
                        with lock:
                            with open('flight_id.json') as f:
                                flight_json = json.load(f)

                        # Check if the contents have changed
                        if flight_json != previous_flight_json:
                            # Update previous state
                            previous_flight_json = flight_json

                            # Check if the loaded dictionary is not empty
                            if flight_json:
                                # Update current flight_id
                                flight_id = flight_json["flight_id"] 

                        if flight_id in result_text:
                            make_wav_file(samplerate, recording_data, frame_limit)
                            audiobit_queue.put((recording_data,samplerate))
                            recording_data = b''  # Reset accumulated audio data

                        else:
                            recording_data = b''
                            print("no command found")

    except KeyboardInterrupt:
        print('===> Finished Recording')
    except Exception as e:
        print(str(e))