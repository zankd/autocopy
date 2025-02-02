import os
import logging
from RealtimeSTT import AudioToTextRecorder
import pyautogui
import re

# Configure logging
LOG_FILE = os.path.join(os.environ['USERPROFILE'], 'Downloads', 'voice_tt.log')
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Suppress verbose logging from RealtimeSTT
logging.getLogger("RealtimeSTT").setLevel(logging.WARNING)

def main():
    WAKE_WORD = "copy"
    wake_word_regex = re.compile(r'\b' + re.escape(WAKE_WORD) + r'\b', re.IGNORECASE)
    activated = False

    def process_text(text):
        nonlocal activated
        logging.info(f"Processing text: {text}")

        if activated:
            try:
                pyautogui.typewrite(text + " ")
                logging.info(f"Typed text: {text}")
                activated = False
            except Exception as e:
                logging.error(f"Error typing text: {str(e)}")
            return

        if wake_word_regex.search(text):
            command = wake_word_regex.sub('', text).strip()
            
            if command:
                try:
                    pyautogui.typewrite(command + " ")
                    logging.info(f"Command typed: {command}")
                except Exception as e:
                    logging.error(f"Error typing command: {str(e)}")
            else:
                activated = True
                logging.info("Activation state set to True")

    logging.info(f"Starting voice listener with wake word '{WAKE_WORD}'")
    
    recorder = AudioToTextRecorder(
        model="small.en",
        language="en",
        post_speech_silence_duration=1.5,
        beam_size=5,
        wake_words=None,
        spinner=True,
        on_recording_start=lambda: logging.info("Recording started"),
        on_recording_stop=lambda: logging.info("Recording stopped")
    )

    try:
        while True:
            try:
                recorder.text(process_text)
            except Exception as e:
                logging.error(f"Error in recording loop: {str(e)}")
    except KeyboardInterrupt:
        logging.info("Shutdown initiated by user")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}", exc_info=True)
    finally:
        try:
            recorder.shutdown()
            logging.info("Recorder shutdown complete")
        except Exception as e:
            logging.error(f"Error shutting down recorder: {str(e)}")

if __name__ == '__main__':
    main()
