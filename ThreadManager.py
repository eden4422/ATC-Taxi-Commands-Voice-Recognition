import multiprocessing
from datetime import datetime
import queue
import json

# local imports
from JsonSaving import *
from CommandTranscription immport audio_transcripting




AUDPROC = "Audio listening process"
AUDTRAN = "Audio " 

# main task that handles
def thread_managing():

    # Initializing pipes, queues, etc
    errorQ = queue.Queue() # error queue, used by all processes for all error handling
    audioQ = queue.Queue() # audio queue, used by thread manager and audio_listening
    textQ = queue.Queue()

    # Starting 
    audio_listening_process = multiprocessing.Process(target=audio_listening, args=(audioQ, errorQ))

    while(True):

        # Wait idly while audioClipQueue is empty (waiting for task 2 to finish)
        while(audioQ.empty):
            pass

        # Pull audioClip from queue 
        audioClipFound = audioQ.get()

        # Start audio transcribing process using audioclip and wait for results
        audio_transcribing_process = multiprocessing.Process(target=audio_transcribing, args=(audioClipFound, textQ, errorQ))
        audio_transcribing_process.start()
        audio_transcribing_process.join()

        # Getting transcribed text from queue

        transcribedText: str = ""

        if textQ.not_empty():
            transcribedText = textQ.get()
        else:
            transcribedText = "ERROR: Text was not transcribed properly. Please refer to error log."

        # Saving converted text to JSON
        saveToJSON(convertToJSON(transcribedText))

if __name__ == "main":
    processMain = multiprocessing.Process(target=thread_managing)
    processMain.start()
    processMain.join()


