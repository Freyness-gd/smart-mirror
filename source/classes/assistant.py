from __future__ import division

import re
import sys

from google.cloud import speech, texttospeech

import pyaudio, simpleaudio, os, random
from six.moves import queue

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

class Assistant():
    language_code = "en-US"

    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code,
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )

    data = {'key': None, 'packet':[None, None]}

    response_tts = texttospeech.TextToSpeechClient()
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Wavenet-H",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )



    def __init__(self):
        print ("Starting Assistant")

    def start(self):
        return self.__stream()

    def __stream(self):
        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )

            responses = self.client.streaming_recognize(self.streaming_config, requests)

            for response in responses:
                if not response.results:
                    continue

                result = response.results[0]
                if not result.alternatives:
                    continue

                transcript = result.alternatives[0].transcript

                if result.is_final:
                    print(transcript)
                    return self.__interpreter(transcript)

    def __interpreter(self, transcript):

        data = self.data
        data['key'] = None

        if re.search(r"\b(exit|quit)\b", transcript, re.I):
            data['key'] = 'exit'
            self.__response_assistant("Shutting down Assistant...")
            return data

        elif re.search(r"\b(spotify|playback|song|pause|resume|play)\b", transcript, re.I):
            if re.search(r"\b(next)\b", transcript, re.I):
                data['key'] = 'sp-next'
                #self.__response_assistant("Playing the next Track")
                return data
            elif re.search(r"\b(last|previous)\b", transcript, re.I):
                data['key'] = 'sp-prev'
                #self.__response_assistant("Playing the previous Track")
                return data
            elif re.search(r"\b(pause)\b", transcript, re.I):
                data['key'] = 'sp-pause'
                #self.__response_assistant("Pausing Playback")
                return data
            elif re.search(r"\b(resume)\b", transcript, re.I):
                data['key'] = 'sp-res'
                #self.__response_assistant("Resuming playback")
                return data
            elif re.search(r"\b(play|search)\b", transcript, re.I):
                return self.__sq_spotify(transcript)
            else:
                data['key'] = 'none'
                return data

        elif re.search(r"\b(your name)\b", transcript, re.I):
            self.__response_assistant("Hi, my name is Smart Mirror")
            data['key'] = 'none'
            return data

        else:
            data['key'] = 'none'
            return data



    def __sq_spotify(self, transcript):

        data = self.data
        data['key'] = 'sp-play'
        data['packet'][0] = None
        data['packet'][1] = None

        if re.search(r"\b(track|song)\b", transcript, re.I):

            length = len(transcript)

            if re.search('by', transcript, re.I):
                index_art = (re.search('by', transcript, re.I).end())
                index_art += 1
                print("Index:" + str(index_art))

                artist = transcript[index_art:length]
                data['packet'][0] = artist

                index_song = (re.search(r"\b(song|track)\b", transcript, re.I).end())
                index_song += 1
                print("Index Song:" + str(index_song))
                song = transcript[index_song:(index_art-4)]
                data['packet'][1] = song

                response = "Playing " + data['packet'][1] + " by " + data['packet'][0]
                self.__response_assistant(response)

                return data

            else:
                index = (re.search(r"\b(song|track)\b", transcript, re.I).end())
                index += 1
                print ("Index: " + str(index))

                song = transcript[index:length]
                data['packet'][1] = song

                return data

        else:
            data['key'] = None
            return data


    def __response_assistant(self, input):

        synth_input = texttospeech.SynthesisInput(text=input)

        response = self.response_tts.synthesize_speech(
            input=synth_input, voice=self.voice, audio_config=self.audio_config
        )

        audio_path = "cache/" + str(random.randint(1000, 9999)) + "-audio.wav"

        try:
            with open(audio_path, "wb") as out:
                out.write(response.audio_content)

            sound_object = simpleaudio.WaveObject.from_wave_file(audio_path)
            sound_object.play()
            os.remove(audio_path)

        except Exception as e:
            print("OOops", e.__class__, " occured!")


class MicrophoneStream(object):

    def __init__(self, rate, chunk):
        self._rate = RATE
        self._chunk = CHUNK

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)
