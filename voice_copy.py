from RealtimeSTT import AudioToTextRecorder
import pyautogui
import re
import logging

# Disable verbose logging from the library
logging.getLogger("RealtimeSTT").setLevel(logging.WARNING)

def main():
    WAKE_WORD = "copy"
    wake_word_regex = re.compile(r'\b' + re.escape(WAKE_WORD) + r'\b', re.IGNORECASE)
    activated = False

    def process_text(text):
        nonlocal activated
        print(f"Processing: {text}")

        # Check if we're already activated
        if activated:
            # Type the text and reset
            pyautogui.typewrite(text + " ")
            print(f"✅ Typed: {text}")
            activated = False
            return

        # Check for wake word in any position
        if wake_word_regex.search(text):
            # Extract command by removing wake word
            command = wake_word_regex.sub('', text).strip()
            
            if command:
                pyautogui.typewrite(command + " ")
                print(f"✅ Command typed: {command}")
            else:
                activated = True
                print("⚡ Activated! Speak your command...")

    print(f"🔊 Listening for wake word '{WAKE_WORD}'... (Press Ctrl+C to quit)")
    
    recorder = AudioToTextRecorder(
        model="small.en",
        language="en",
        post_speech_silence_duration=1.5,
        beam_size=5,
        wake_words=None,
        spinner=True,
        on_recording_start=lambda: print("\n⚡ Recording..."),
        on_recording_stop=lambda: print("🛑 Stopped recording")
    )

    try:
        while True:
            recorder.text(process_text)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    finally:
        recorder.shutdown()

if __name__ == '__main__':
    main()
