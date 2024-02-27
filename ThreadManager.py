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
    countdown_left = 0
    countdown_start = time_out

    # Variable for airplane identifier
    plane_ids = plane_id_list

    # Initializing pipes, queues, etc
    front_com_in = multiprocessing.Queue() # frontend queue, used by thread manager -> frontend
    front_com_out = multiprocessing.Queue() 

    listen_audio_outQ = multiprocessing.Queue() # audio queue, used by audio_listening -> thread_manager
    
    listen_com_in = multiprocessing.Queue() # audio comm in
    listen_com_out = multiprocessing.Queue() # audio comm out
    
    trans_audio_inQ = multiprocessing.Queue()
    trans_text_outQ = multiprocessing.Queue() # 

    trans_com_in = multiprocessing.Queue()
    trans_com_out = multiprocessing.Queue()

    listenHeartBeat = False
    transHeartBeat = False
    frontHeartBeat = False

    # Creating frontend process
    frontend_process = multiprocessing.Process(target=getGoing, args=(front_com_in, front_com_out, frontHeartBeat))
    
    print("Starting frontend process")
    frontend_process.start()

    # Creating audio listening process
    audio_listening_process = multiprocessing.Process(target=listen_for_audio, args=(plane_ids, listen_audio_outQ, listen_com_in, listen_com_out, listenHeartBeat))
    
    # Creating audio transcribing process
    audio_transcribing_process = multiprocessing.Process(target=transcribe_audio, args=(trans_audio_inQ, trans_text_outQ, trans_com_in, trans_com_out, transHeartBeat))
    
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
        countdown_left = countdown_left - 1
        if countdown_left <= 0:
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
            
            countdown_left = countdown_start

        # If audio bit was recorded
        if not listen_audio_outQ.empty():

            # Pull audioClip from queue and add to transQ
            audio_clip_found = listen_audio_outQ.get()
            trans_audio_inQ.put(audio_clip_found)
            
        # If text was successfully transcribed
        elif not trans_text_outQ.empty():
            transcribed_text = trans_text_outQ.get()
            phoentetic_text = Text_To_JSON.phonetic_command_translator(transcribed_text)
            parsed_text = Text_To_JSON.parse_taxi_command(phoentetic_text)
            Text_To_JSON.save_to_JSON(parsed_text)
            JSON_to_Mongo.Write_to_Mongo()
            print("Transcribed Text: "+transcribed_text )
            front_com_in.put((update_command_box,transcribed_text))



        # If message recieved from frontend
        elif not front_com_out.empty():
            output = front_com_out.get()
            
            if output[0] == KILLCHILDREN:
                front_com_in.put((KILLSELF,"kill self"))
                listen_com_in.put((KILLSELF,"kill self"))
                trans_com_in.put((KILLSELF,"kill self"))

                currentlyTranscribing = False
                currentlyListening = False

                print("Awaiting threads to kill selves")

                running = False

            elif output[0] == MUTE:
                print("toggle mute")
                listen_com_in.put((MUTE,"toggle mute"))

            elif output[0] == START:
                print("Starting audio listening process")
                audio_listening_process.start()
                currentlyListening = True

                print("Starting audio transcribing process")
                audio_transcribing_process.start()
                currentlyTranscribing = True

        # If message recieved from listener
        elif not listen_com_out.empty():
            output = listen_com_out.get()
                
            if output[0] == "allAudio":
                front_com_in.put((updateAllSpeechBox,output[1]))
                print(output)
            
        # If message recieved from transcriber
        elif not trans_com_out.empty():
            pass
        
        

if __name__ == "__main__":

    print("starting thread manager")
    process_main = multiprocessing.Process(
        target=thread_managing, 
        args=( ["delta one two three", "united six seven eight", "delta five eight nine two"], 10000)
        )
    
    process_main.start()
    process_main.join()
    print("threadmanager finished")