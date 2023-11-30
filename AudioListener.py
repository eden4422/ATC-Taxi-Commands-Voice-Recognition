from QueueKeys import *
import queue


def audio_listener(plane_id: str, audio_segment_queue: queue, comm_in_queue: queue, comm_out_queue: queue):
    # will run concurrently unless it is stopped 
    listening = True

    while(listening):
        
        # TODO  listen for name to be called
        for i in range(500):
            pass
        
        # TODO transcribe commands until silence heard
        for i in range(400):
            pass

        # TODO check for commands from parent thread
        if not comm_in_queue.Empty:
            pass

        # TODO check for errors in audio, if any found output them to comm_out_queue 

        # save audio to the audio_segment queue to be picked up by the parent thread
        audio_segment_queue.put("AUDIO BLAH BLAH BLAH")