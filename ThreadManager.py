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
def thread_managing():
    
    # Initializing pipes, queues, etc
    front_com_in = multiprocessing.Queue() # frontend queue, used by thread manager -> frontend
    front_com_out = multiprocessing.Queue() 

    listen_audio_out_queue = multiprocessing.Queue() # audio queue, used by audio_listening -> thread_manager
    
    listen_com_in = multiprocessing.Queue() # audio comm in
    listen_com_out = multiprocessing.Queue() # audio comm out
    
    trans_audio_in_queue = multiprocessing.Queue()
    trans_text_out_queue = multiprocessing.Queue() # 

    trans_com_in = multiprocessing.Queue()
    trans_com_out = multiprocessing.Queue()

    # Creating frontend process
    frontend_process = multiprocessing.Process(target=get_going, args=(front_com_in, front_com_out))
    
    print("Starting frontend process")
    frontend_process.start()

    # Creating audio listening process
    audio_listening_process = multiprocessing.Process(target=listen_for_audio, args=(listen_audio_out_queue, listen_com_in, listen_com_out))
    
    # Creating audio transcribing process
    audio_transcribing_process = multiprocessing.Process(target=transcribe_audio, args=(trans_audio_in_queue, trans_text_out_queue, trans_com_in, trans_com_out))
    
    running = True
    while(running):
        # If audio bit was recorded
        if not listen_audio_out_queue.empty():

            # Pull audioClip from queue and add to transQ
            audio_clip_found = listen_audio_out_queue.get()
            trans_audio_in_queue.put(audio_clip_found)
            
        # If text was successfully transcribed
        elif not trans_text_out_queue.empty():
            transcribed_text = trans_text_out_queue.get()
            phoentetic_text = Text_To_JSON.phonetic_command_translator(transcribed_text)
            parsed_text = Text_To_JSON.parse_taxi_command(phoentetic_text)
            Text_To_JSON.save_to_JSON(parsed_text)
            JSON_to_Mongo.Write_to_Mongo()
            front_com_in.put((updateCommandBox,transcribed_text))



        # If message recieved from frontend
        elif not front_com_out.empty():
            output = front_com_out.get()
            
            if output[0] == KILLCHILDREN:
                front_com_in.put((KILLSELF,"kill self"))
                listen_com_in.put((KILLSELF,"kill self"))
                trans_com_in.put((KILLSELF,"kill self"))

                print("Awaiting threads to kill selves")

                running = False

            elif output[0] == MUTE:
                print("toggle mute")
                listen_com_in.put((MUTE,"toggle mute"))

            elif output[0] == START:
                print("Starting audio listening process")
                audio_listening_process.start()

                print("Starting audio transcribing process")
                audio_transcribing_process.start()

        # If message recieved from listener
        elif not listen_com_out.empty():
            output = listen_com_out.get()
                
            if output[0] == "allAudio":
                front_com_in.put((updateAllSpeechBox,output[1]))
            
        # If message recieved from transcriber
        elif not trans_com_out.empty():
            pass
        
if __name__ == "__main__":

    print("starting thread manager")
    processMain = multiprocessing.Process(target=thread_managing)
    processMain.start()
    processMain.join()
    print("threadmanager finished")