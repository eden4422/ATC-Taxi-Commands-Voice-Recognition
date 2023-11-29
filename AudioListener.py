from Commands import *
import queue

def audio_listening(audio_segment_queue: queue, comm_in_queue: queue, comm_out_queue):
    # will run concurrently unless it is stopped 
    listening = True

    while(listening):
        
        # listen for name to be called
        for i in range(500):
            pass
        
        

        # save audio to the audio_segment queue to be picked up by the parent thread
        audio_segment_queue.put("AUDIO BLAH BLAH BLAH")