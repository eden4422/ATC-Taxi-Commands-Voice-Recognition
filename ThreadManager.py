# python library imports
import multiprocessing
import threading
from datetime import datetime
import queue
import json
import wave
import Text_To_JSON
import Mongo_Read_Data

# local imports
from JsonSaving import *
from CommandTranscription import *
from AudioListening import *
from CommandTranscription import *
from QueueKeys import *
from myGUI import *
from commands import *

# main task that handles
def thread_managing(plane_id_list: list, time_out: int):
    
    # Booleans representing different states
    currentlyListening: bool = False
    currentlyTranscribing: bool = False

    # Variables for heartbeat check across threads
    coundown_left = 0
    countdown_start = time_out

    # Variable for airplane identifier
    plane_ids = plane_id_list

    # Initializing pipes, queues, etc
    frontComIn = multiprocessing.Queue() # frontend queue, used by thread manager -> frontend
    frontComOut = multiprocessing.Queue() 

    listenAudioOutQ = multiprocessing.Queue() # audio queue, used by audio_listening -> thread_manager
    
    listenComIn = multiprocessing.Queue() # audio comm in
    listenComOut = multiprocessing.Queue() # audio comm out
    
    transAudioInQ = multiprocessing.Queue()
    transTextOutQ = multiprocessing.Queue() # 

    transComIn = multiprocessing.Queue()
    transComOut = multiprocessing.Queue()

    listenHeartBeat = False
    transHeartBeat = False
    frontHeartBeat = False

    # Creating frontend process
    frontend_process = multiprocessing.Process(target=getGoing, args=(frontComIn, frontComOut, frontHeartBeat))
    
    print("Starting frontend process")
    frontend_process.start()

    # Creating audio listening process
    audio_listening_process = multiprocessing.Process(target=listen_for_audio, args=(plane_ids, listenAudioOutQ, listenComIn, listenComOut, listenHeartBeat))
    
    # Creating audio transcribing process
    audio_transcribing_process = multiprocessing.Process(target=transcribe_audio, args=(transAudioInQ, transTextOutQ, transComIn, transComOut, transHeartBeat))
    
    running = True

    while(running):

        # Checking each thread to make sure they're still alive, and restarting the thread if it isn't
        if not audio_listening_process.is_alive and currentlyListening:
            audio_listening_process = multiprocessing.Process(target=listen_for_audio, args=(plane_ids, listenAudioOutQ, listenComIn, listenComOut, listenHeartBeat))
            print('ERROR: audio listening process failed, restarting now')

        if not frontend_process.is_alive:
            frontend_process = multiprocessing.Process(target=getGoing, args=(frontComIn, frontComOut, frontHeartBeat))
            print('ERROR: frontend process failed, restarting now')

        if not audio_transcribing_process.is_alive and currentlyTranscribing:
            audio_transcribing_process = multiprocessing.Process(target=transcribe_audio, args=(transAudioInQ, transTextOutQ, transComIn, transComOut, transHeartBeat))
            print('ERROR: audio transcribing process failed, restarting now')

        # Checking heart beat after timeout has passed
        coundown_left = coundown_left - 1
        if coundown_left <= 0:
            # Restarting threads if heartbeat queue is empty
            if frontHeartBeat == True:
                frontHeartBeat = False
                frontend_process = multiprocessing.Process(target=getGoing, args=(frontComIn, frontComOut, frontHeartBeat))
                print('ERROR: frontend process has timed out, restarting now')

            if listenHeartBeat == True and currentlyListening:
                listenHeartBeat = False
                audio_listening_process = multiprocessing.Process(target=listen_for_audio, args=(plane_ids, listenAudioOutQ, listenComIn, listenComOut, listenHeartBeat))
                print('ERROR: listening process has timed out, restarting now')

            if transHeartBeat == True and currentlyTranscribing:
                transHeartBeat = False
                audio_transcribing_process = multiprocessing.Process(target=transcribe_audio, args=(transAudioInQ, transTextOutQ, transComIn, transComOut, transHeartBeat))
                print('ERROR: audio transcribing process has timed out, restarting now')
            
            coundown_left = countdown_start

        # If audio bit was recorded
        if not listenAudioOutQ.empty():

            # Pull audioClip from queue and add to transQ
            audioClipFound = listenAudioOutQ.get()
            transAudioInQ.put(audioClipFound)
            
        # If text was successfully transcribed
        elif not transTextOutQ.empty():
            transcribedText = transTextOutQ.get()
            phoentetic_text = Text_To_JSON.phonetic_command_translator(transcribedText)
            parsed_text = Text_To_JSON.parse_taxi_command(phoentetic_text)
            Text_To_JSON.save_to_JSON(parsed_text)
            JSON_to_Mongo.Write_to_Mongo()
            print("Transcribed Text: "+transcribedText )
            frontComIn.put((updateCommandBox,transcribedText))



        # If message recieved from frontend
        elif not frontComOut.empty():
            output = frontComOut.get()
            
            if output[0] == KILLCHILDREN:
                frontComIn.put((KILLSELF,"kill self"))
                listenComIn.put((KILLSELF,"kill self"))
                transComIn.put((KILLSELF,"kill self"))

                print("Awaiting threads to kill selves")

                running = False

            elif output[0] == MUTE:
                print("toggle mute")
                listenComIn.put((MUTE,"toggle mute"))

            elif output[0] == START:
                print("Starting audio listening process")
                audio_listening_process.start()

                print("Starting audio transcribing process")
                audio_transcribing_process.start()

        # If message recieved from listener
        elif not listenComOut.empty():
            output = listenComOut.get()
                
            if output[0] == "allAudio":
                frontComIn.put((updateAllSpeechBox,output[1]))
                print(output)
            
        # If message recieved from transcriber
        elif not transComOut.empty():
            pass
        
        

if __name__ == "__main__":

    print("starting thread manager")
    processMain = multiprocessing.Process(target=thread_managing, args=( ["delta one two three", "united six seven eight", "delta five eight nine two"], 10000))
    processMain.start()
    processMain.join()
    print("threadmanager finished")