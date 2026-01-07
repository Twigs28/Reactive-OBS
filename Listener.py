import speech_recognition as sr
import pyaudio
import math
import struct
import wave
import time
import Core


filename = "test.wav"

Threshold = 8

SHORT_NORMALIZE = (1.0/32768.0)
chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
swidth = 2

TIMEOUT_LENGTH = 1.5

f_name_directory = r'.'

class Recorder:

    run:bool=True

    @staticmethod
    def rms(frame):
        count = len(frame) / swidth
        format = "%dh" % (count)
        shorts = struct.unpack(format, frame)

        sum_squares = 0.0
        for sample in shorts:
            n = sample * SHORT_NORMALIZE
            sum_squares += n * n
        rms = math.pow(sum_squares / count, 0.5)

        return rms * 1000

    def __init__(self,core:Core):
        self.core=core
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  input=True,
                                  output=True,
                                  frames_per_buffer=chunk)

    def record(self):
        print('Noise detected, audio recording beginning')
        rec = []
        current = time.time()
        end = time.time() + TIMEOUT_LENGTH

        while current <= end:

            data = self.stream.read(chunk)
            if self.rms(data) >= Threshold: end = time.time() + TIMEOUT_LENGTH

            current = time.time()
            rec.append(data)
        self.write(b''.join(rec))

    def write(self, recording):

        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(recording)
        wf.close()
        print('Written to file: {}'.format(filename))
        print('Returning to listening')


    def analize(self):
        # initialize the recognizer
        r = sr.Recognizer()
        # open the file
        with sr.AudioFile(filename) as source:
        # listen for the data (load audio to memory)
            audio_data = r.record(source)
            text = ""
        # recognize (convert from speech to text)
            try:
                text = r.recognize_google(audio_data)
            except (sr.exceptions.UnknownValueError, sr.exceptions.TranscriptionNotReady , sr.exceptions.WaitTimeoutError , sr.exceptions.TranscriptionFailed , sr.exceptions.RequestError):
                print("an error occurred while understanding the message")
            self.core.read_activation(text)



    def listen(self):
        print('Listening beginning')
        run = True
        self.core.status=True
        while run:
            run=self.core.getStatus()
            input = self.stream.read(chunk)
            rms_val = self.rms(input)
            if rms_val > Threshold:
                self.record()
                self.analize()
    
    def stop(self):
        self.run=False
        return 0


if __name__=="__main__":

    a = Recorder()
    a.listen()
