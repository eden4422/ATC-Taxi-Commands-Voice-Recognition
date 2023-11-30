import vosk


def model_one(input_audio,output_text_queue, error_queue):
    # runs for a finite ammount of time before 
    model_path = "voskModel1"
    recognizer = vosk.Model(model_path)

    result: str = recognizer.recognize(input_audio)

    output_text_queue.put(result)