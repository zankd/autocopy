from RealtimeSTT import AudioToTextRecorder
import pyautogui
import re
import logging
import os
import traceback
from logging.handlers import RotatingFileHandler
from importlib.metadata import version

# Disable verbose logging from the library
logging.getLogger("RealtimeSTT").setLevel(logging.WARNING)

# Global variables
WAKE_WORD = "copy"
wake_word_regex = re.compile(r'\b' + re.escape(WAKE_WORD) + r'\b', re.IGNORECASE)
activated = False

def configure_logging(script_dir):
    """Configure logging with rotation and detailed formatting."""
    log_file = os.path.join(script_dir, 'voice_logs.log')
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    numeric_level = getattr(logging, log_level, None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')

    formatter = logging.Formatter(
        '%(asctime)s - %(process)d - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    logging.info("="*50)
    logging.info("Starting voice command listener")
    logging.info("Log level set to: %s", log_level)
    try:
        logging.info("RealtimeSTT version: %s", version('RealtimeSTT'))
        logging.info("pyautogui version: %s", version('pyautogui'))
    except Exception as e:
        logging.warning("Version check failed: %s", str(e))

def clean_and_match(text, target):
    cleaned_words = re.sub(r'[^a-zA-Z]', ' ', text).lower().split()
    return target.lower() in cleaned_words

def process_text(text):
    global activated
    try:
        logging.debug("Raw text received: '%s'", text)
        print(f"Processing: {text}")

        if activated:
            logging.debug("Activation state: Active")
            # Check if the text ends with 'enter'
            match = re.search(r'^(.*?)\benter\b\W*$', text, re.IGNORECASE)
            if match:
                text_to_type = match.group(1).strip()
                if text_to_type:
                    pyautogui.typewrite(text_to_type + " ")
                    logging.info("Typed text: '%s'", text_to_type)
                    print(f"✅ Typed: {text_to_type}")
                pyautogui.press('enter')
                logging.info("Pressed Enter key")
                print("✅ Pressed Enter")
            else:
                if clean_and_match(text, 'enter'):
                    pyautogui.press('enter')
                    logging.info("Pressed Enter key")
                    print("✅ Pressed Enter")
                else:
                    pyautogui.typewrite(text + " ")
                    logging.info("Typed text: '%s'", text)
                    print(f"✅ Typed: {text}")
            activated = False
            return
            
        if wake_word_regex.search(text):
            # Log the text before removal.
            logging.debug("Before wake word removal: '%s'", text)
            # Remove the wake word from the text.
            command = wake_word_regex.sub('', text).strip()
            logging.debug("After wake word removal, command: '%s'", command)
            
            if command:
                # Check if the command ends with 'enter'
                match = re.search(r'^(.*?)\benter\b\W*$', command, re.IGNORECASE)
                if match:
                    text_to_type = match.group(1).strip()
                    if text_to_type:
                        pyautogui.typewrite(text_to_type + " ")
                        logging.info("Typed command: '%s'", text_to_type)
                        print(f"✅ Typed: {text_to_type}")
                    pyautogui.press('enter')
                    logging.info("Pressed Enter key")
                    print("✅ Pressed Enter")
                else:
                    if clean_and_match(command, 'enter'):
                        pyautogui.press('enter')
                        logging.info("Pressed Enter key")
                        print("✅ Pressed Enter")
                    else:
                        # Simply type the command as is.
                        pyautogui.typewrite(command + " ")
                        logging.info("Typed command: '%s'", command)
                        print(f"✅ Typed: {command}")
            else:
                activated = True
                logging.info("Entering activation mode. Waiting for further input...")
                print("⚡ Activated! Speak your command...")
    except Exception as e:
        logging.critical("Error in process_text: %s", str(e), exc_info=True)
        print(f"🔥 Critical error in processing: {e}")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    configure_logging(script_dir)

    logging.info("Initializing audio recorder")
    recorder = AudioToTextRecorder(
        model="small.en",
        language="en",
        post_speech_silence_duration=1.5,
        beam_size=5,
        wake_words=None,
        spinner=True,
        on_recording_start=lambda: logging.debug("Recording started"),
        on_recording_stop=lambda: logging.debug("Recording stopped")
    )

    try:
        logging.info("Entering main processing loop")
        print(f"⚡ Listening for wake word '{WAKE_WORD}'... (Press Ctrl+C to quit)")
        while True:
            try:
                recorder.text(process_text)
            except Exception as loop_err:
                # Catch errors from the recorder loop (e.g. BrokenPipeError)
                logging.error("Error in recorder loop: %s", str(loop_err), exc_info=True)
                print(f"🔥 Recorder error: {loop_err}")
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received")
        print("\n🛑 Shutting down...")
    except Exception as e:
        logging.critical("Unexpected error in main loop: %s", str(e), exc_info=True)
        print(f"🔥 Critical error in main loop: {e}")
    finally:
        try:
            logging.info("Initiating recorder shutdown")
            recorder.shutdown()
            logging.info("Recorder shutdown completed")
        except Exception as e:
            logging.error("Error during shutdown: %s", str(e), exc_info=True)
        logging.info("Application shutdown complete")

if __name__ == '__main__':
    main()
