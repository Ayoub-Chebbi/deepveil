import pyttsx3
import threading
import queue
import time

speech_engine = pyttsx3.init()
speech_queue = queue.Queue()
speech_lock = threading.Lock()
speech_active = threading.Event()
speech_active.set()
speech_engine.startLoop(False)

def speech_worker():
    while True:
        if not speech_active.is_set():
            time.sleep(0.1)
            continue
        try:
            text, language, gender = speech_queue.get(timeout=1)
            with speech_lock:
                if not speech_active.is_set():
                    speech_queue.task_done()
                    continue
                voices = speech_engine.getProperty('voices')
                voice_index = 1 if gender == "female" and len(voices) > 1 else 0
                speech_engine.setProperty('voice', voices[voice_index].id)
                speech_engine.setProperty('rate', 130)
                speech_engine.setProperty('volume', 1.0)
                speech_engine.say(text)
                print(f"Queued speech: {text} with voice index {voice_index}")
            speech_queue.task_done()
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Speech error: {e}")
            speech_queue.task_done()

speech_thread = threading.Thread(target=speech_worker, daemon=True)
speech_thread.start()

def text_to_speech(text, language, gender="male"):
    if not speech_queue.full():
        speech_queue.put((text, language, gender))
    else:
        print("Speech queue is full, skipping speech.")

def stop_speech():
    with speech_lock:
        speech_active.clear()
        speech_engine.stop()
        while not speech_queue.empty():
            try:
                speech_queue.get_nowait()
                speech_queue.task_done()
            except queue.Empty:
                break
        speech_active.set()
        print("Speech stopped and queue cleared")