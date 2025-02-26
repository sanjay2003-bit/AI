import time
import threading
import keyboard
import numpy as np
import sounddevice as sd
import speech_recognition as sr
import os
import subprocess as sp
from kivy.uix import widget,image,label,boxlayout,textinput
from kivy import clock
from constants import SCREEN_HEIGHT,SCREEN_WIDTH
from utils import speak,youtube,search_on_google,search_on_wikipedia,get_news,weather_forecast,find_my_ip

class Assistant(widget.Widget):
    def __init__(self, **kwargs):
        super(Assistant,self).__init__(**kwargs)
        self.volume = 0
        self.volume_history = [0,0,0,0,0,0,0]
        self.volume_history_size = 140

        self.min_size = .2 * SCREEN_WIDTH
        self.max_size = .7 * SCREEN_WIDTH

        self.start_recording()

        img = image.Image(source='static/AI2.gif')
        img.size = (self.min_size, self.min_size)
        img.pos = (SCREEN_WIDTH / 2 - self.min_size / 2, SCREEN_HEIGHT / 2 - self.min_size / 2)

        self.add_widget(img)

        time_layout = boxlayout.BoxLayout(orientation='vertical',pos=(150,900))
        self.time_lable = label.Label(text='', font_size=24, markup=True,font_name='static/mw.ttf')
        time_layout.add_widget(self.time_lable)
        self.add_widget(time_layout)

        clock.Clock.schedule_interval(self.update_time, 1)

        self.title =label.Label(text='[b][color=3333ff]HELLO SAM[/color][/b]',font_size = 42,markup = True,font_name='static/dusri.ttf',pos=(920,900))
        self.add_widget(self.title)

        self.subtitle_input = textinput.TextInput(
            text='Hey Sam! I am your personal Assistant',
            font_size=24,
            readonly=False,
            background_color=(0, 0, 0, 0),
            foreground_color=(1, 1, 1, 1),
            size_hint_y=None,
            height=110,
            pos=(720, 100),
            width=1200,
            font_name='static/teesri.otf',
        )
        self.add_widget(self.subtitle_input)

        keyboard.add_hotkey('`', self.start_recording)

    def take_command(self):
            r = sr.Recognizer()
            with sr.Microphone() as source:
                print("Listening....")
                r.pause_threshold = 1
                audio = r.listen(source)

            try:
                print("Recognizing....")
                queri = r.recognize_google(audio, language='en-in')
                return queri.lower()

            except Exception:
                response_text = "Sorry I couldn't understand. Can you pleas repeat that"
                print(response_text)
                return ""

    def start_recording(self):
            print(("Recording started"))
            threading.Thread(target=self.run_speech_recognition).start()
            print("recording ended")

    def run_speech_recognition(self):
        global query
        if hasattr(self, 'is_recognizing') and self.is_recognizing:  # Prevent re-entry
            return
        self.is_recognizing = True

        print('before speech rec obj')
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            audio = r.listen(source)
            print("audio recorded")

        print("after speech rec obj")

        try:
            query = r.recognize_google(audio, language="en-in")
            print(f'Recognised: {query}')
            clock.Clock.schedule_once(
                lambda dt: setattr(self.subtitle_input, 'text', self.subtitle_input.text + f"\nYou: {query}"))
            self.handle_Assistant_commands(query.lower())

        except sr.UnknownValueError:
            response_text = "Sorry, I couldn't understand."
            print("Google speech recognition could not understand audio")
            clock.Clock.schedule_once(
                lambda dt: setattr(self.subtitle_input, 'text', self.subtitle_input.text + f"\nAI: {response_text}"))
            print(response_text)

        except sr.RequestError as e:
            response_text = "There was an issue connecting to the server."
            clock.Clock.schedule_once(
                lambda dt: setattr(self.subtitle_input, 'text', self.subtitle_input.text + f"\nAI: {response_text}"))
            print(e)

        finally:
            self.is_recognizing = False

    def update_time(self, dt):
            current_time = time.strftime('TIME\n\t%I:%M:%S:%p')
            self.time_lable.text = f'[b][color=3333ff]{current_time}[/color][/b]'

    def update_circle(self, dt):
            try:
                self.size_value = int(np.mean(self.volume_history))

            except Exception as e:
                self.size_value = self.min_size
                print('Warning:', e)

            if self.size_value <= self.min_size:
                self.size_value = self.min_size
            elif self.size_value >= self.max_size:
                self.size_value = self.max_size
            self.circle.size = (self.size_value, self.size_value)
            self.circle.pos = (SCREEN_WIDTH / 2 - self.circle.width / 2, SCREEN_HEIGHT / 2 - self.circle.height / 2)

    def update_volume(self, indata, frames, time, status):
            volume_norm = np.linalg.norm(indata) * 200
            self.volume = volume_norm
            self.volume_history.append(volume_norm)

            if len(self.volume_history) > self.volume_history_size:
                self.volume_history.pop(0)

    def start_listening(self):
            self.stream = sd.InputStream(callback=self.update_volume, dtype='float32', samplerate=44100)
            self.stream.start()

    def handle_Assistant_commands(self, query):
            if not query:
                print("No valid command received.")
                return

            try:
                response_text = ""

                if "how are you" in query:
                    response_text += "I am absolutely fine, sir. What about you?"

                if "what is your name" in query:
                    response_text += "My name is Aandaval"

                elif "open cmd" in query:

                    response_text = "Opening command prompt."
                    os.system('start cmd')

                elif "open camera" in query:
                    response_text = "Opening camera sir"
                    sp.run('start microsoft.windows.camera:', shell=True)

                elif "open notepad" in query:
                    response_text = "Opening Notepad for you sir"
                    notepad_path = "C:\\Users\\johnn\\AppData\\Local\\Microsoft\\WindowsApps\\notepad.exe"
                    os.startfile(notepad_path)

                elif 'ip address' in query:
                    ip_address = find_my_ip()
                    response_text = f'Your IP Address is {ip_address}.\n For your convenience, I am printing it on the screen sir.'
                    response_text = f'Your IP Address is {ip_address}'

                elif "youtube" in query:
                    video = query.replace("search on youtube", "").strip()
                    if not video:
                        speak("What do you want to search on YouTube?")
                        video = self.take_command()
                    youtube(video)

                elif "search on google" in query:
                    search_query = query.replace("search on google", "").strip()

                    if search_query:
                        print(f"Searching Google for: {search_query}")
                        search_on_google(search_query)
                    else:
                        speak("What do you want to search on Google?")
                        search_query = self.take_command()

                        if search_query:
                            search_on_google(search_query)

                elif "search on wikipedia" in query:
                    search_query = query.replace("search on wikipedia", "").strip()

                    if not search_query:
                        speak("What do you want to search on Wikipedia, sir?")
                        search_query = self.take_command()

                    if search_query:
                        results = search_on_wikipedia(search_query)

                        if results:
                            response_text = f"According to Wikipedia, {results}"
                        else:
                            response_text = "Sorry, I couldn't find any relevant information on Wikipedia."

                elif "tell me news" in query:
                    response_text = f"I am reading out the latest headline of today,sir"
                    response_text = get_news()


                elif 'weather' in query:
                    city = "Coimbatore"
                    response_text = f"Getting weather report for your city {city}"
                    weather, temp, feels_like = weather_forecast(city)
                    response_text = f"The current temperature is {temp}, but it feels like {feels_like}"
                    response_text = f"Also, the weather report talks about {weather}"
                    weather_message = f"The weather in Coimbatore is {weather}. The temperature is {temp} degrees Celsius, but it feels like {feels_like} degrees."
                    speak(weather_message)
                    weather_info = f"[b]Weather Update:[/b]\nDescription: {weather}\nTemperature: {temp}°C\nFeels like: {feels_like}°C"
                    clock.Clock.schedule_once(lambda dt: setattr(self.subtitle_input, 'text',self.subtitle_input.text + f"\nAI: {weather_info}"))
                    print(weather_info)

                if response_text:
                    speak(response_text)
                    clock.Clock.schedule_once(lambda dt: setattr(self.subtitle_input, 'text', self.subtitle_input.text + f"\nAI: {response_text}"))
                    print(response_text)

            except Exception as e:
                print(f"Error handling command: {e}")