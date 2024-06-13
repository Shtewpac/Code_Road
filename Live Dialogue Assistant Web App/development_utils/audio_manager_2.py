import os
from google.cloud import speech
import speech_recognition as sr
from pydub import AudioSegment
import threading
import time
import librosa
import soundfile as sf
import openai
import multiprocessing
import asyncio
from concurrent.futures import ThreadPoolExecutor
from queue import Empty
from config import *


def create_audio_manager(command_queue, result_queue):
    manager = AudioManager(command_queue, result_queue)
    manager.initialize()
    return manager


class AudioManager:

    def __init__(self, command_queue, result_queue):
        self.command_queue = command_queue
        self.result_queue = result_queue
        self.transcript_update_callback = None
        self.is_recording = False
        self.recognizer = sr.Recognizer()
        self.saved_audio_files = []
        self.audio_counter = 0
        self.default_sample_rate = DEFAULT_SAMPLE_RATE
        self.recorded_audio_path = os.path.abspath('data/recorded_audio')
        self.preprocessed_audio_path = os.path.abspath('data/preprocessed_audio')
        self.combined_audio_path = os.path.join(self.recorded_audio_path, 'combined_audio.wav')
        self.alternate_transcript = ''
        self.delete_existing_audio_files()

    def initialize(self):
        self.new_snippet_event = threading.Event()

    def start_recording(self):
        self.is_recording = True
        self.recording_thread = threading.Thread(target=self.
            _recording_loop, daemon=True)
        self.recording_thread.start()
        self.processing_thread = threading.Thread(target=self.
            _async_processing_loop, daemon=True)
        self.processing_thread.start()

    def stop_recording(self):
        self.is_recording = False
        self.processing_process.terminate()
        print('Recording stopped.')

    def is_recording(self):
        return self.is_recording

    def run(self):
        self.initialize()
        while True:
            print('Running')
            command = self.command_queue.get()
            print('Command: ', command)
            if command == 'START':
                self.start_recording()
            elif command == 'STOP':
                self.stop_recording()
                break
            self.check_and_process_updates()

    def check_and_process_updates(self):
        if self.new_snippet_event.is_set():
            self._combine_audio_files()
            transcript = self.get_transcript(self.combined_audio_path)
            if transcript:
                self.result_queue.put(transcript)
            self.new_snippet_event.clear()

    def _recording_loop(self):
        try:
            while self.is_recording:
                audio_data = self._record_snippet()
                if audio_data:
                    processed = self._process_snippet(audio_data)
                    if processed:
                        print('Snippet processed.')
                        self._store_snippet(audio_data)
                    else:
                        print('Snippet could not be processed.')
        except Exception as e:
            print(f'Exception in recording loop: {e}')

    def _async_processing_loop(self):
        while self.is_recording:
            time.sleep(1)
            self.check_and_process_updates()

    def _store_snippet(self, audio_data):
        filename = f'snippet_{self.audio_counter}.wav'
        filepath = os.path.join(self.recorded_audio_path, filename)
        self.audio_counter += 1
        self.saved_audio_files.append(filepath)
        with open(filepath, 'wb') as f:
            f.write(audio_data.get_wav_data())
        self.new_snippet_event.set()

    def _combine_audio_files(self):
        combined_audio = AudioSegment.empty()
        for audio_file in self.saved_audio_files:
            audio = AudioSegment.from_file(audio_file)
            combined_audio += audio
        combined_audio.export(self.combined_audio_path, format='wav')

    def _combining_and_transcribing_loop(self):
        while True:
            self.new_snippet_event.wait()
            self.new_snippet_event.clear()
            if not self.is_recording and not self.saved_audio_files:
                break
            if len(self.saved_audio_files) > 0:
                self._combine_audio_files()
                if self.combined_audio_path is not None:
                    transcript = self.get_transcript(self.combined_audio_path)
                    print('Transcript: ', transcript)
                    if transcript is not None:
                        self.transcript_update_callback(transcript)

    def get_transcript(self, audio_file):
        if audio_file:
            try:
                sentences = self.transcribe_with_diarization(audio_file)
                if sentences is not None:
                    formatted_transcript = self.format_transcript(sentences)
                    print('\nAlternate transcript: ', self.alternate_transcript
                        )
                    print('\nFormatted transcript: ', formatted_transcript)
                    correct_transcript = self.correct_transcript_compare(
                        formatted_transcript, self.alternate_transcript)
                    return correct_transcript
            except Exception as e:
                print(f'An error occurred: {e}')
                return ''
        return ''

    def format_transcript(self, transcript):
        formatted_transcript = ''
        current_speaker = None
        for sentence in transcript:
            speaker = sentence[0]
            text = sentence[1]
            if speaker != current_speaker:
                pass
            if speaker == 1:
                formatted_transcript += f'{SPEAKER_A}: {text}\n'
            elif speaker == 2:
                formatted_transcript += f'{SPEAKER_B}: {text}\n'
            else:
                formatted_transcript += f'{text}\n'
            current_speaker = speaker
        return formatted_transcript

    def transcribe_with_diarization(self, speech_file):
        client = speech.SpeechClient()
        converted_audio_path = self.preprocess_audio(speech_file)
        with open(converted_audio_path, 'rb') as audio_file:
            content = audio_file.read()
        audio = speech.RecognitionAudio(content=content)
        diarization_config = speech.SpeakerDiarizationConfig(
            enable_speaker_diarization=True, min_speaker_count=1,
            max_speaker_count=2)
        config = speech.RecognitionConfig(encoding=speech.RecognitionConfig
            .AudioEncoding.LINEAR16, sample_rate_hertz=self.
            default_sample_rate, language_code='en-US', diarization_config=
            diarization_config)
        try:
            print('Waiting for operation to complete...')
            response = client.recognize(config=config, audio=audio)
        except Exception as e:
            print(f'An error occurred: {e}')
            return None
        if not response.results:
            print('No results returned.')
            return None
        result = response.results[-1]
        words_info = result.alternatives[0].words if result.alternatives else [
            ]
        sentences = self.construct_sentences(words_info)
        return sentences

    def preprocess_audio(self, speech_file):
        y_resampled, _ = librosa.load(speech_file, sr=self.default_sample_rate)
        converted_audio_path = os.path.join(self.preprocessed_audio_path,
            f'{os.path.splitext(os.path.basename(speech_file))[0]}_converted.wav'
            )
        sf.write(converted_audio_path, y_resampled, self.default_sample_rate)
        return converted_audio_path

    def correct_transcript(self, transcript):
        system_message = (
            "You will be given a transcript of a conversation with potential errors. Please try and correct the transcript. Give your answer in this form: 'Corrected Transcript: <your corrected transcript>'"
            )
        messages = [{'role': 'system', 'content': system_message}, {'role':
            'user', 'content': f"""Conversation Transcript:
{transcript}
"""}]
        response = openai.ChatCompletion.create(model='gpt-3.5-turbo-16k',
            messages=messages, max_tokens=4000)
        corrected_transcript = response.choices[0].message['content'].strip()
        corrected_transcript = corrected_transcript.replace(
            'Corrected Transcript:', '')
        return corrected_transcript

    def correct_transcript_compare(self, transcript, alternate_transcript):
        system_message = """
        You will be given two transcripts of the same conversation that may have discrepancies. 
        Your task is to compare these two transcripts and produce a single, accurate transcript 
        that best represents the actual conversation. Consider differences in word choice, 
        phrasing, and any potential errors in either transcript. Provide the corrected and 
        unified transcript. Give your answer in this form: 'Corrected Transcript: <your corrected transcript>'
        """
        messages = [{'role': 'system', 'content': system_message}, {'role':
            'user', 'content': f"""Original Transcript:
{transcript}
"""},
            {'role': 'user', 'content':
            f"""Alternate Transcript:
{alternate_transcript}
"""}]
        response = openai.ChatCompletion.create(model='gpt-3.5-turbo-16k',
            messages=messages, max_tokens=4000)
        corrected_transcript = response.choices[0].message['content'].strip()
        corrected_transcript = corrected_transcript.replace(
            'Corrected Transcript:', '')
        return corrected_transcript

    def set_transcript_update_callback(self, callback):
        print('Transcript update callback triggered')
        self.transcript_update_callback = callback

    def delete_existing_audio_files(self):
        """Delete all existing audio files in the recorded and preprocessed audio directories."""
        for audio_dir in [self.recorded_audio_path, self.
            preprocessed_audio_path]:
            for filename in os.listdir(audio_dir):
                file_path = os.path.join(audio_dir, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)

    def _record_snippet(self):
        with sr.Microphone() as source:
            print('Recording...')
            audio = self.recognizer.listen(source)
            return audio

    def _process_snippet(self, audio_data):
        try:
            transcription = self.recognizer.recognize_google(audio_data)
            print(f'\nRECOGNIZED: {transcription}')
            self.alternate_transcript += transcription + '\n'
            return True
        except sr.UnknownValueError:
            print('Could not understand audio')
            return False
        except sr.RequestError as e:
            print(f'Request error from Google Speech Recognition service; {e}')
            return False
