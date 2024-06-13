# Combined source file created on 2023-11-11 16:30:30

# G:\My Drive\Coding Projects\2023\Live Dialogue Assistant\src\main_app.py
# Python file for main_app.py

# Import necessary modules
from config import *  # or other relevant configuration
from views.tkinter_gui import TkinterGUI
from views.pyqt_gui import PyQtGUI
from controllers.gpt_assistance_controller import GPTAssistanceController
from controllers.audio_controller import AudioController
from controllers.summary_controller import LiveSummaryController
from managers.gpt_assistance_manager import GPTAssistanceManager
from managers.audio_manager import AudioManager
from managers.live_summary_manager import LiveSummaryManager
# from application_state import ApplicationState  # if you're using application state

import openai
import os
import sys

from PyQt5.QtWidgets import QApplication  # Add this import for PyQt


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS_PATH
openai.api_key = OPENAI_API_KEY

def main():
    # Load configuration

    # Initialize Managers
    gpt_assistance_manager = GPTAssistanceManager(FAST_LLM)
    audio_manager = AudioManager()  # Initialize with any required parameters
    live_summary_manager = LiveSummaryManager(FAST_LLM)

    # Initialize Controllers with Managers
    gpt_assistance_controller = GPTAssistanceController(gpt_assistance_manager)
    audio_controller = AudioController(audio_manager)
    summary_controller = LiveSummaryController(live_summary_manager)

    # Set up GUI
    # gui = TkinterGUI(gpt_assistance_controller, audio_controller, summary_controller)

    # # Start the GUI's main interaction loop
    # gui.start()

    # Ensure the QApplication instance is created before any other PyQt widgets
    app = QApplication(sys.argv)
    gui = PyQtGUI(gpt_assistance_controller, audio_controller, summary_controller)

    # Start the GUI's main interaction loop
    gui.show()  # Use show for PyQt instead of start
    sys.exit(app.exec_())  # This will start the event loop
    

if __name__ == "__main__":
    main()


# G:\My Drive\Coding Projects\2023\Live Dialogue Assistant\src\controllers\gpt_assistance_controller.py
# Python file for gpt_assistance_controller.py

from managers.gpt_assistance_manager import GPTAssistanceManager

class GPTAssistanceController:
    def __init__(self, gpt_assistance_manager):
        self.manager = gpt_assistance_manager

    def handle_request_for_assistance(self, transcript, summary):
        return self.manager.generate_suggestions(transcript, summary)

# G:\My Drive\Coding Projects\2023\Live Dialogue Assistant\src\controllers\audio_controller.py
# Python file for audio_controller.py

from managers.audio_manager import AudioManager
class AudioController:
    def __init__(self, audio_manager):
        self.audio_manager = audio_manager

    def start_recording(self):
        return self.audio_manager.start_recording()
    
    def is_recording(self):
        return self.audio_manager.is_recording()

    def stop_recording(self):
        return self.audio_manager.stop_recording()

    def get_transcript(self):
        return self.audio_manager.get_transcript()
    
    def _combine_audio_files(self):
        return self.audio_manager._combine_audio_files()

# G:\My Drive\Coding Projects\2023\Live Dialogue Assistant\src\controllers\summary_controller.py
# Python file for summary_controller.py

from managers.live_summary_manager import LiveSummaryManager
class LiveSummaryController:
    def __init__(self, live_summary_manager):
        self.live_summary_manager = live_summary_manager

    def generate_summary(self, transcript):
        return self.live_summary_manager.generate_summary(transcript)

# G:\My Drive\Coding Projects\2023\Live Dialogue Assistant\src\managers\gpt_assistance_manager.py
# Python file for gpt_assistance_manager.py
import openai

class GPTAssistanceManager:
    def __init__(self, model, assistance_level=1):
        self.model = model
        self.assistance_level = assistance_level
        self.suggestion_text = None

    def set_suggestion_text_widget(self, suggestion_text_widget):
        self.suggestion_text = suggestion_text_widget

    def set_assistance_level(self, assistance_level):
        self.assistance_level = assistance_level

    def generate_suggestions(self, transcript, summary):
        assistance_level = self.assistance_level

        # Determine the system message based on the assistance level
        system_message = ''
        if assistance_level == 0:
            return ''
        elif assistance_level == 1:
            system_message = 'You will be given the current summary of the conversation and the last 10 lines of dialogue. Your job is to help person A respond to person B. Give them a response that is relevant to the conversation and that will help them continue the conversation. Give your answer in the following format: "Potential response: <response>"'
        elif assistance_level == 2:
            system_message = 'You will be given the current summary of the conversation and the last 10 lines of dialogue. Your job is to help person A respond to person B. Provide a response in the style of person A that is relevant to the conversation and that will help them continue the conversation. Give your answer in the following format: "Potential response: <response>"'
        else:
            system_message = 'Invalid assistance level'

        # Add the conversation transcript and summary to the messages list
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Conversation Transcript:\n{transcript}\n\nConversation Summary:\n{summary}"}
        ]

        # Generate suggestions using the selected model (for chat models)
        response = openai.ChatCompletion.create(  # Updated this line to use ChatCompletion
            model=self.model,
            messages=messages,   # Use 'messages' parameter for chat models
            max_tokens=50  # Adjust the max tokens as needed
        )

        # Extract and return the suggestions
        suggestions = response.choices[0].message["content"].strip()
        return suggestions


# G:\My Drive\Coding Projects\2023\Live Dialogue Assistant\src\managers\audio_manager.py
# Python file for audio_manager.py

import os
from google.cloud import speech
import speech_recognition as sr
from pydub import AudioSegment
import threading
import time
import librosa
import soundfile as sf
import openai
from config import *

class AudioManager:
    def __init__(self):
        # Initialize audio manager
        self.transcript_update_callback = None
        self.is_recording = False
        self.recognizer = sr.Recognizer()
        self.saved_audio_files = []
        self.audio_counter = 0
        self.default_sample_rate = DEFAULT_SAMPLE_RATE
        self.recorded_audio_path = os.path.abspath('data/recorded_audio')
        self.preprocessed_audio_path = os.path.abspath('data/preprocessed_audio')
        self.combined_audio_path = os.path.join(self.recorded_audio_path, "combined_audio.wav")
        self.recording_thread = None
        self.combining_thread = None
        self.new_snippet_event = threading.Event()
        self.alternate_transcript = ""
        self.delete_existing_audio_files()

    def set_transcript_update_callback(self, callback):
        print("Transcript update callback triggered")
        self.transcript_update_callback = callback

    def start_recording(self):
        self.is_recording = True
        # Start recording loop
        threading.Thread(target=self._recording_loop, daemon=True).start()

        # Start processing loop
        self.combining_thread = threading.Thread(target=self._combining_and_transcribing_loop, daemon=True)
        self.combining_thread.start()
        print("Recording started.")
        # return "Recording started."
    
    def _recording_loop(self):
        try:
            while self.is_recording:
                # print("Recording loop running")
                audio_data = self._record_snippet()
                if audio_data:
                    processed = self._process_snippet(audio_data)
                    if processed:
                        print("Snippet processed.")
                        self._store_snippet(audio_data)
                    else:
                        print("Snippet could not be processed.")
        except Exception as e:
            print(f"Exception in recording loop: {e}")


    def _store_snippet(self, audio_data):
        # Logic to store the audio snippet
        filename = f"snippet_{self.audio_counter}.wav"
        filepath = os.path.join(self.recorded_audio_path, filename)
        self.audio_counter += 1
        self.saved_audio_files.append(filepath)
        # Save the audio_data to file
        with open(filepath, "wb") as f:
            f.write(audio_data.get_wav_data())
        
        # After storing a new snippet:
        self.new_snippet_event.set()

    def _combining_and_transcribing_loop(self):
        while True:
            # print("Combining and transcribing loop running")
            # Wait for a new snippet or a stop signal
            self.new_snippet_event.wait()
            self.new_snippet_event.clear()
            if not self.is_recording and not self.saved_audio_files:
                break  # Exit the loop if recording is stopped and all files are processed

            if len(self.saved_audio_files) > 1:
                self._combine_audio_files()
                if self.combined_audio_path is not None:
                    transcript = self.get_transcript(self.combined_audio_path)
                    print("Transcript: ", transcript)
                    if transcript is not None:
                        self.transcript_update_callback(transcript)

    def _combine_audio_files(self):
        # print("Combining audio files...")
        combined_audio = AudioSegment.empty()
        # print("Saved audio files: ", self.saved_audio_files)
        for audio_file in self.saved_audio_files:
            audio = AudioSegment.from_file(audio_file)
            combined_audio += audio
        combined_audio.export(self.combined_audio_path, format="wav")
    
    
    def is_recording(self):
        # Simulated check for audio recording
        return self.is_recording

    def stop_recording(self):
        self.is_recording = False

        # Ensure the combining thread is not waiting indefinitely
        self.new_snippet_event.set()

        print("Recording stopped.")
        

    def get_transcript(self):
        # Simulated audio transcript
        return "This is a simulated transcript of the recorded audio."
    
    def _record_snippet(self):
        # Logic to record a snippet of audio and return it
        # For example, using speech_recognition's listen() method
        with sr.Microphone() as source:
            print("Recording...")
            audio = self.recognizer.listen(source)
            return audio

    def _process_snippet(self, audio_data):
        try:
            transcription = self.recognizer.recognize_google(audio_data)
            print(f"\nRECOGNIZED: {transcription}")
            # Add the transcription to the alternate transcript
            self.alternate_transcript += transcription + "\n"
            # if self.transcript_update_callback:
            #     self.transcript_update_callback(transcription)
            return True
        except sr.UnknownValueError:
            print("Could not understand audio")
            return False
        except sr.RequestError as e:
            print(f"Request error from Google Speech Recognition service; {e}")
            return False


    def format_transcript(self, transcript):
        # Format the transcript to include the speaker names
        formatted_transcript = ""
        current_speaker = None
        for sentence in transcript:
            speaker = sentence[0]
            text = sentence[1]
            if speaker != current_speaker:
                # formatted_transcript += "\n"
                pass
            if speaker == 1:
                formatted_transcript += f"{SPEAKER_A}: {text}\n"
            elif speaker == 2:
                formatted_transcript += f"{SPEAKER_B}: {text}\n"
            else:
                formatted_transcript += f"{text}\n"
            current_speaker = speaker
        return formatted_transcript
    
    def get_transcript(self, audio_file):
        if audio_file:
            try:
                sentences = self.transcribe_with_diarization(audio_file)
                if sentences is not None:
                    formatted_transcript = self.format_transcript(sentences)
                    # correct_transcript = self.correct_transcript(formatted_transcript)
                    print("\nAlternate transcript: ", self.alternate_transcript)
                    print("\nFormatted transcript: ", formatted_transcript)

                    correct_transcript = self.correct_transcript_compare(formatted_transcript, self.alternate_transcript)
                    # correct_transcript = formatted_transcript
                    return correct_transcript
            except Exception as e:
                print(f"An error occurred: {e}")
                return ""
        return ""
    
    def correct_transcript(self, transcript):
        # Reconstruct the transcript using gpt-3.5-turbo
        system_message = "You will be given a transcript of a conversation with potential errors. Please try and correct the transcript. Give your answer in this form: 'Corrected Transcript: <your corrected transcript>'"
        # Add the conversation transcript and summary to the messages list
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Conversation Transcript:\n{transcript}\n"}
        ]

        # Generate suggestions using the selected model (for chat models)
        response = openai.ChatCompletion.create(  # Updated this line to use ChatCompletion
            model="gpt-3.5-turbo-16k",
            messages=messages,   # Use 'messages' parameter for chat models
            max_tokens=4000  # Adjust the max tokens as needed
        )

        # Extract and return the suggestions
        corrected_transcript = response.choices[0].message["content"].strip()
        # Remove the "Corrected Transcript: " prefix
        corrected_transcript = corrected_transcript.replace("Corrected Transcript:", "")
        return corrected_transcript
    
    def correct_transcript_compare(self, transcript, alternate_transcript):
        # Reconstruct the transcript using gpt-3.5-turbo
        system_message = """
        You will be given two transcripts of the same conversation that may have discrepancies. 
        Your task is to compare these two transcripts and produce a single, accurate transcript 
        that best represents the actual conversation. Consider differences in word choice, 
        phrasing, and any potential errors in either transcript. Provide the corrected and 
        unified transcript. Give your answer in this form: 'Corrected Transcript: <your corrected transcript>'
        """
        # Construct the message for GPT
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Original Transcript:\n{transcript}\n"},
            {"role": "user", "content": f"Alternate Transcript:\n{alternate_transcript}\n"}
        ]

        # Generate suggestions using the selected model
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=messages,
            max_tokens=4000  # Adjust the max tokens as needed
        )

        # Extract and return the corrected transcript
        corrected_transcript = response.choices[0].message["content"].strip()
        # Remove the "Corrected Transcript: " prefix
        corrected_transcript = corrected_transcript.replace("Corrected Transcript:", "")
        return corrected_transcript

    def preprocess_audio(self, speech_file):
        # Load the audio file using librosa and resample it to the desired sample rate
        y_resampled, _ = librosa.load(speech_file, sr=self.default_sample_rate)
        # Convert the resampled audio back to a wav file
        converted_audio_path = os.path.join(self.preprocessed_audio_path, f"{os.path.splitext(os.path.basename(speech_file))[0]}_converted.wav")
        # Save the resampled audio using soundfile
        sf.write(converted_audio_path, y_resampled, self.default_sample_rate)
        
        return converted_audio_path
    
    def construct_sentences(self, words_info):
        sentences = []
        sentence = []
        current_speaker = words_info[0].speaker_tag

        for word_info in words_info:
            # Check if there's a significant time gap or speaker change
            if sentence and (word_info.speaker_tag != current_speaker or 
                            word_info.start_time.seconds - sentence[-1]['end_time'].seconds > 1):
                sentences.append((current_speaker, ' '.join([w['word'] for w in sentence])))
                sentence = []
                current_speaker = word_info.speaker_tag

            sentence.append({
                'word': word_info.word,
                'start_time': word_info.start_time,
                'end_time': word_info.end_time,
                'speaker_tag': word_info.speaker_tag
            })

        # Add the last sentence
        if sentence:
            sentences.append((current_speaker, ' '.join([w['word'] for w in sentence])))

        return sentences

    def transcribe_with_diarization(self, speech_file):
        client = speech.SpeechClient()
        
        # Preprocess the audio file if necessary
        converted_audio_path = self.preprocess_audio(speech_file)

        with open(converted_audio_path, "rb") as audio_file:
            content = audio_file.read()
        audio = speech.RecognitionAudio(content=content)

        diarization_config = speech.SpeakerDiarizationConfig(
            enable_speaker_diarization=True,
            min_speaker_count=2,
            max_speaker_count=6,
        )
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.default_sample_rate,
            language_code="en-US",
            diarization_config=diarization_config,
        )
        try:
            print("Waiting for operation to complete...")
            response = client.recognize(config=config, audio=audio)
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

        if not response.results:
            print("No results returned.")
            return None

        result = response.results[-1]
        words_info = result.alternatives[0].words if result.alternatives else []

        sentences = self.construct_sentences(words_info)
        # print("Sentences: ", sentences)
        
        return sentences
    
    def delete_existing_audio_files(self):
        """Delete all existing audio files in the recorded and preprocessed audio directories."""
        for audio_dir in [self.recorded_audio_path, self.preprocessed_audio_path]:
            for filename in os.listdir(audio_dir):
                file_path = os.path.join(audio_dir, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
    

# G:\My Drive\Coding Projects\2023\Live Dialogue Assistant\src\managers\live_summary_manager.py
# Python file for live_summary_manager.py
from config import *
import openai
class LiveSummaryManager:
    def __init__(self, model):
        self.model = model
        self.live_transcript = []
        self.line_counter = 0
        self.rolling_summary = ""

    def add_text_to_transcript(self, text):
        """Append the recognized text to the transcript list and update the line counter."""
        self.live_transcript.append(text)
        self.line_counter += 1
        if self.line_counter >= 2:
            self.update_summary()
            self.line_counter = 0
    
    def set_live_transcript(self, text):
        """Set the live transcript to the provided text."""
        self.live_transcript = text
        self.line_counter = 0
        self.update_summary()


    def get_last_10_lines(self):
        """Fetch the last 10 lines of the transcript."""
        return "\n".join(self.live_transcript[-10:])

    def generate_summary_messages(self, last_10_lines):
        """Determine the messages to send to the model for summarization."""
        total_lines = len(self.rolling_summary.splitlines())

        if total_lines > 10:
            return [
                {"role": "system", "content": "You will be given the current summary of the conversation and the last 10 lines of dialogue. Your job is to update the current summary with any relevant information from the last 10 lines. Give your answer in the following format: 'Summary: <summary>'"},
                {"role": "user", "content": f"Summary:\n{self.rolling_summary}\n\nLast 10 Lines of Transcript:\n{last_10_lines}"}
            ]
        else:
            return [
                {"role": "system", "content": f"You are going to be given a transcribed conversation from two people. Your job is to summarize the conversation. Refer to the two people as {SPEAKER_A} and {SPEAKER_B} in the summary. Give your answer in the following format: 'Summary: <summary>'"},
                {"role": "user", "content": f"Transcript:\n{self.live_transcript}"}
            ]

    def update_summary(self):
        print("\nUpdating summary...")
        """Use the model to generate a summary based on the transcript."""
        last_10_lines = self.get_last_10_lines()
        messages = self.generate_summary_messages(last_10_lines)
        # print("\nMessages:", messages, "\n")
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=2000  # Adjust the max tokens as needed
            )
            
            # Update the rolling summary
            self.rolling_summary = response.choices[0].message["content"].strip()
            # Strip the 'Summary: ' prefix from the summary
            self.rolling_summary = self.rolling_summary.replace("Summary:", "")
        
        except Exception as e:
            print("Error:", e)

    def get_summary(self):
        """Retrieve the current rolling summary."""
        return self.rolling_summary
    
    def generate_summary(self, transcript):
        self.set_live_transcript(transcript)
        print("\nLive Transcript:", self.live_transcript)
        return self.rolling_summary
    
    def identify_last_speaker(self):
        messages = [
            {"role": "system", "content": "You will be given the current summary of the conversation and the last 10 lines of dialogue. Your job is to determine whether 'person A' or 'person B' was the last to speak. If person A was the last to speak, type 'A'. If person B was the last to speak, type 'B'."},
            {"role": "user", "content": f"Summary:\n{self.rolling_summary}\n\nLast 10 Lines of Transcript:\n{self.get_last_10_lines()}"}
        ]
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            return response.choices[0].message["content"].strip()

        except Exception as e:
            print("Error:", e)
            return None

# G:\My Drive\Coding Projects\2023\Live Dialogue Assistant\src\managers\dialogue_app_manager.py
# Python file for dialogue_app_manager.py

class DialogueAppManager:
    def __init__(self, gpt_assistance_manager, audio_manager, live_summary_manager):
        self.gpt_assistance_manager = gpt_assistance_manager
        self.audio_manager = audio_manager
        self.live_summary_manager = live_summary_manager

    # You can add methods here that coordinate the actions between the different managers.
    # For example, a method to start recording, process audio, and update the summary.

# G:\My Drive\Coding Projects\2023\Live Dialogue Assistant\src\models\application_state.py
# Python file for application_state.py
# G:\My Drive\Coding Projects\2023\Live Dialogue Assistant\src\views\gui_interface.py
# Python file for gui_interface.py

from abc import ABC, abstractmethod

class GUIInterface(ABC):

    @abstractmethod
    def initialize(self, *args, **kwargs):
        """Initialize the GUI with necessary parameters."""
        pass

    @abstractmethod
    def start(self):
        """Start and display the GUI."""
        pass

    @abstractmethod
    def stop(self):
        """Close and stop the GUI."""
        pass

    @abstractmethod
    def update_transcript(self, transcript):
        """Update the transcript display."""
        pass

    @abstractmethod
    def set_suggestions(self, suggestions):
        """Update the suggestions display."""
        pass

    @abstractmethod
    def set_summary(self, summary):
        """Update the conversation summary display."""
        pass

    @abstractmethod
    def display_error(self, error_message):
        """Display an error message to the user."""
        pass

# G:\My Drive\Coding Projects\2023\Live Dialogue Assistant\src\views\tkinter_gui.py
# Python file for tkinter_gui.py

from views.gui_interface import GUIInterface

from config import *
import tkinter as tk
from tkinter import scrolledtext, messagebox

class TkinterGUI(GUIInterface):
    def __init__(self, gpt_assistance_controller, audio_controller, summary_controller, app_state=None):
        self.gpt_assistance_controller = gpt_assistance_controller
        self.audio_controller = audio_controller
        self.audio_controller.audio_manager.set_transcript_update_callback(self.update_frames_callback)
        self.summary_controller = summary_controller
        self.app_state = app_state  # Optional application state

        self.root = tk.Tk()
        self.root.title("Live Dialogue Assistant")
        self.create_ui_elements()

    def create_ui_elements(self):
        self.create_transcript_frame()
        self.create_input_entry()
        self.create_buttons()
        self.create_suggestion_frame()
        self.create_summary_frame()

    def create_transcript_frame(self):
        label = tk.Label(self.root, text="Conversation Transcript", font=("Arial", 14))
        label.pack(pady=(10, 0))
        self.transcript_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=10)
        self.transcript_text.pack(pady=(0, 10), padx=10, fill=tk.BOTH, expand=True)

        # Define tags for coloring
        self.transcript_text.tag_configure(SPEAKER_A, foreground="blue")
        self.transcript_text.tag_configure(SPEAKER_B, foreground="red")


    def create_input_entry(self):
        self.input_entry = tk.Entry(self.root, width=40)
        self.input_entry.pack()

    def create_buttons(self):
        tk.Button(self.root, text="Switch Assistance Level", command=self.switch_assistance_level).pack()
        tk.Button(self.root, text="Get Assistance", command=self.get_assistance).pack()
        tk.Button(self.root, text="Clear Transcript & Summary", command=self.clear_transcript_summary).pack()
        tk.Button(self.root, text="Start Recording", command=self.start_recording).pack()
        tk.Button(self.root, text="Stop Recording", command=self.stop_recording).pack()

    def create_summary_frame(self):
        label = tk.Label(self.root, text="Conversation Summary", font=("Arial", 14))
        label.pack(pady=(10, 0))
        self.summary_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=5)
        self.summary_text.pack(pady=(0, 10), padx=10, fill=tk.BOTH, expand=True)

    def create_suggestion_frame(self):
        label = tk.Label(self.root, text="Dialogue Suggestions", font=("Arial", 14))
        label.pack(pady=(10, 0))
        self.suggestion_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=5)
        self.suggestion_text.pack(pady=(0, 10), padx=10, fill=tk.BOTH, expand=True)

    
    # Implement the abstract methods
    def initialize(self, *args, **kwargs):
        pass

    def start(self):
        self.root.mainloop()

    def stop(self):
        self.root.destroy()

    def update_transcript_callback(self, transcript):
        # Ensure UI updates happen in the main thread
        self.root.after(0, lambda: self.update_transcript(transcript))

    def set_transcript_callback(self, transcript):
        # Ensure UI updates happen in the main thread
        self.root.after(0, lambda: self.set_transcript(transcript))

    def update_frames_callback(self, transcript):
        # Ensure UI updates happen in the main thread
        self.root.after(0, lambda: self.update_frames(transcript))

    def update_transcript(self, transcript):
        # Insert the new transcript
        self.transcript_text.insert(tk.END, transcript + '\n')
        self.transcript_text.see(tk.END)

    def set_transcript(self, transcript):
        self.transcript_text.delete(1.0, tk.END)
        lines = transcript.split('\n')
        for line in lines:
            line_end_index = tk.END
            self.transcript_text.insert(line_end_index, line + '\n')
            line_start_index = self.transcript_text.index(f"{line_end_index} -1 line linestart")
            line_end_index = self.transcript_text.index(f"{line_end_index} -1 line lineend")
            
            if "Person A" in line:
                self.transcript_text.tag_add("Person_A", line_start_index, line_end_index)
            elif "Person B" in line:
                self.transcript_text.tag_add("Person_B", line_start_index, line_end_index)
        self.transcript_text.see(tk.END)

    # def set_transcript(self, transcript):
    #     self.transcript_text.delete(1.0, tk.END)
    #     self.transcript_text.insert(tk.END, transcript + '\n')
    #     self.transcript_text.see(tk.END)

    def set_summary(self, summary):
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, summary + '\n')
        self.summary_text.see(tk.END)

    def set_suggestions(self, suggestions):
        self.suggestion_text.delete(1.0, tk.END)
        self.suggestion_text.insert(tk.END, suggestions + '\n')
        self.suggestion_text.see(tk.END)

    def display_error(self, error_message):
        messagebox.showerror("Error", error_message)

    # Placeholder methods for button commands
    def switch_assistance_level(self):
        pass

    def get_assistance(self):
        transcript = self.transcript_text.get(1.0, tk.END).strip()  # Get transcript from UI
        summary = self.summary_text.get(1.0, tk.END).strip()        # Get summary from UI
        if transcript:
            self.gpt_assistance_manager.get_assistance(transcript, summary)
        else:
            self.display_error("Please provide some input or start recording.")

    def clear_transcript_summary(self):
        self.transcript_text.delete(1.0, tk.END)
        self.summary_text.delete(1.0, tk.END)

    def start_recording(self):
        # Start recording audio
        self.audio_controller.start_recording()

    def stop_recording(self):
        # Signal the AudioManager to stop recording
        self.audio_controller.stop_recording()

    def update_frames(self, transcript):
        # Update the transcript, conversation summary, and suggestions

        # Update the transcript
        self.set_transcript(transcript)

        # Update the conversation summary
        summary = self.summary_controller.generate_summary(transcript)
        self.set_summary(summary)

        # Update the suggestions
        suggestions = self.gpt_assistance_controller.handle_request_for_assistance(transcript, summary)
        self.set_suggestions(suggestions)
# G:\My Drive\Coding Projects\2023\Live Dialogue Assistant\src\views\pyqt_gui.py

from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import pyqtSignal

class PyQtGUI(QMainWindow):
    transcript_update_signal = pyqtSignal(str)

    def __init__(self, gpt_assistance_controller, audio_controller, summary_controller, app_state=None):
        super().__init__()
        self.title = "Live Dialogue Assistant"
        self.gpt_assistance_controller = gpt_assistance_controller
        self.audio_controller = audio_controller
        self.summary_controller = summary_controller
        self.audio_controller.audio_manager.set_transcript_update_callback(self.update_frames_callback)
        self.app_state = app_state  # Optional application state
        self.transcript_update_signal.connect(self.update_frames)   
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(100, 100, 800, 600)  # Set position and size
        
        # Set a default font for the text edit widgets
        text_edit_font = QFont('Arial', 12)  # You can adjust the size as needed
        
        # Set a larger font for labels
        label_font = QFont('Arial', 16)  # Adjust the size as needed
        
        layout = QVBoxLayout()

        # Create and configure the transcript label
        transcript_label = QLabel("Conversation Transcript")
        transcript_label.setFont(label_font)
        layout.addWidget(transcript_label)

        # Create and configure the transcript text edit widget
        self.transcript_text = QTextEdit()
        self.transcript_text.setFont(text_edit_font)
        layout.addWidget(self.transcript_text)

        # Create and configure the summary label
        summary_label = QLabel("Conversation Summary")
        summary_label.setFont(label_font)
        layout.addWidget(summary_label)

        # Create and configure the summary text edit widget
        self.summary_text = QTextEdit()
        self.summary_text.setFont(text_edit_font)
        layout.addWidget(self.summary_text)

        # Create and configure the suggestions label
        suggestion_label = QLabel("Dialogue Suggestions")
        suggestion_label.setFont(label_font)
        layout.addWidget(suggestion_label)

        # Create and configure the suggestions text edit widget
        self.suggestion_text = QTextEdit()
        self.suggestion_text.setFont(text_edit_font)
        layout.addWidget(self.suggestion_text)

        # Create and configure the start recording button
        self.start_button = QPushButton("Start Recording", self)
        self.start_button.setFont(label_font)  # Set the font for the button as well
        self.start_button.clicked.connect(self.start_recording)
        layout.addWidget(self.start_button)

        # Create and configure the stop recording button
        self.stop_button = QPushButton("Stop Recording", self)
        self.stop_button.setFont(label_font)  # Set the font for the button as well
        self.stop_button.clicked.connect(self.stop_recording)
        layout.addWidget(self.stop_button)

        # Set the central widget and layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def update_frames_callback(self, transcript):
        # Call this method to emit the signal
        self.transcript_update_signal.emit(transcript)

    def display_error(self, error_message):
        # Placeholder for displaying error messages
        pass

    def start_recording(self):
        # Start recording audio
        self.audio_controller.start_recording()

    def stop_recording(self):
        # Signal the AudioManager to stop recording
        self.audio_controller.stop_recording()

    def update_transcript(self, transcript):
        self.transcript_text.clear()
        for line in transcript.split('\n'):
            if "Person A" in line:
                color = QColor("blue")
            elif "Person B" in line:
                color = QColor("red")
            else:
                color = QColor("black")
            self.transcript_text.setTextColor(color)
            self.transcript_text.append(line)

    def set_summary(self, summary):
        self.summary_text.setPlainText(summary)

    def set_suggestions(self, suggestions):
        self.suggestion_text.setPlainText(suggestions)

    def update_frames(self, transcript):
        # Update the transcript, conversation summary, and suggestions

        # Update the transcript
        self.update_transcript(transcript)

        # Update the conversation summary
        summary = self.summary_controller.generate_summary(transcript)
        print("Setting summary...")
        self.set_summary(summary)

        # Update the suggestions
        suggestions = self.gpt_assistance_controller.handle_request_for_assistance(transcript, summary)
        print("Setting suggestions...")
        self.set_suggestions(suggestions)


# # Sample test code to run the application
# if __name__ == '__main__':
#     import sys
#     app = QApplication(sys.argv)
#     ex = PyQtGUI()
#     ex.show()
#     sys.exit(app.exec_())

