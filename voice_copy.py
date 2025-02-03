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

def configure_logging(script_dir):
    """Configure logging with rotation and detailed formatting."""
    log_file = os.path.join(script_dir, 'voice_logs.log')
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Validate log level
    numeric_level = getattr(logging, log_level, None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')

    # Detailed formatter including module and line numbers
    formatter = logging.Formatter(
        '%(asctime)s - %(process)d - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Rotating file handler (1MB per file, max 5 backups)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=1024*1024,  # 1MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    # Console handler for real-time monitoring
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Log environment information
    logging.info("="*50)
    logging.info("Starting voice command listener")
    logging.info("Log level set to: %s", log_level)
    try:
        logging.info("RealtimeSTT version: %s", version('RealtimeSTT'))
        logging.info("pyautogui version: %s", version('pyautogui'))
    except Exception as e:
        logging.warning("Version check failed: %s", str(e))

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    configure_logging(script_dir)

    WAKE_WORD = "copy"
    wake_word_regex = re.compile(r'\b' + re.escape(WAKE_WORD) + r'\b', re.IGNORECASE)
    activated = False

    def process_text(text):
        nonlocal activated
        try:
            logging.debug("Raw text received: %s", text)
            print(f"Processing: {text}")

            if activated:
                logging.debug("Activation state: Active")
                try:
                    pyautogui.typewrite(text + " ")
                    logging.info("Successfully typed text: %s", text)
                    print(f"✅ Typed: {text}")
                except Exception as e:
                    logging.error("Failed to type text: %s", str(e), exc_info=True)
                    print(f"❌ Error typing: {str(e)}")
                finally:
                    activated = False
                return

            if wake_word_regex.search(text):
                command = wake_word_regex.sub('', text).strip()
                logging.debug("Wake word detected. Command extracted: %s", command)
                
                if command:
                    try:
                        pyautogui.typewrite(command + " ")
                        logging.info("Successfully executed command: %s", command)
                        print(f"✅ Command typed: {command}")
                    except Exception as e:
                        logging.error("Command execution failed: %s", str(e), exc_info=True)
                        print(f"❌ Error executing command: {str(e)}")
                else:
                    activated = True
                    logging.info("Entering activation mode")
                    print("⚡ Activated! Speak your command...")

        except Exception as e:
            logging.critical("Unhandled error in process_text: %s", str(e), exc_info=True)
            print(f"🔥 Critical error: {str(e)}")

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
        print(f"🔊 Listening for wake word '{WAKE_WORD}'... (Press Ctrl+C to quit)")
        while True:
            recorder.text(process_text)
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received")
        print("\n🛑 Shutting down...")
    except Exception as e:
        logging.critical("Unexpected error in main loop: %s", str(e), exc_info=True)
        print(f"🔥 Critical error: {str(e)}")
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
