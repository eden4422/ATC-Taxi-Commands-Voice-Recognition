# python library imports
import multiprocessing
from datetime import datetime
import queue
import json

# local imports
from JsonSaving import *
from CommandTranscription import *
from AudioListening import *
from CommandTranscription import *
from QueueKeys import *
from Frontend import *


# main task that handles
def thread_managing():

    # Temp variable for airplane identifier
    plane_id = "JOHNNY"

    # Initializing pipes, queues, etc
    frontComIn = queue.Queue() # frontend queue, used by thread manager -> frontend
    frontComOut = queue.Queue() 


    audiobitQ = queue.Queue() # audio queue, used by audio_listening -> thread_manager
    
    audioComIn = queue.Queue() # audio comm in
    audioComOut = queue.Queue() # audio comm out
    
    textQ = queue.Queue() # 
    
    transComIn = queue.Queue()
    transComOut = queue.Queue()

    # Starting frontend process
    frontend_process = multiprocessing.Process(target=front_window, args=(frontComIn, frontComOut))

    # Starting audio listening process
    audio_listening_process = multiprocessing.Process(target=listen_for_audio, args=(plane_id, audiobitQ, audioComIn, audioComOut))

    running = True

    while(running):

        # Wait idly while audioClipQueue is empty (waiting for task 2 to finish)
        
        frontComIn.put((UPLOG, "Waiting for audio bite to be saved to audiobitQ"))
        while(audiobitQ.empty and audioComOut.empty):
            #
            
            pass



        # Pull audioClip from queue 
        audioClipFound = audiobitQ.get()

        # Start audio transcribing process using audioclip and wait for results
        audio_transcribing_process = multiprocessing.Process(target=audio_transcriber, args=(audioClipFound, textQ, errorQ))
        audio_transcribing_process.start()
        audio_transcribing_process.join()

        # Getting transcribed text from queue

        if textQ.not_empty() and transComOut:
            transcribedText = textQ.get()
            # Saving converted text to JSON
            saveToJSON(convertToJSON(transcribedText))
        
        else:
            frontQ.put((UPERROR,""))
        

if __name__ == "main":
    processMain = multiprocessing.Process(target=thread_managing)
    processMain.start()
    processMain.join()


