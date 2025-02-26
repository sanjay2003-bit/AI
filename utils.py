import requests
import wikipedia
import pywhatkit as kit
import gtts
import os
from pydub import AudioSegment
from pydub.playback import play
from constants import (
    NEWS_FETCH_API_URL,
    WEATHER_FORECAST_API_URL,
    NEWS_FETCH_API_KEY,
    WEATHER_FORECAST_API_KEY,
)


def speak(text):
    tts = gtts.gTTS(text,lang='en-in')
    tts.save("output.wav")

    audio = AudioSegment.from_file("output.wav")
    os.remove("output.wav")
    audio = audio.speedup(playback_speed=1.3)

    play(audio)

def find_my_ip():
    ip_address = requests.get('https://api.ipify.org?format=json').json()
    return ip_address["ip"]


def search_on_wikipedia(query):
    results = wikipedia.summary(query, sentences=2)
    return results


def search_on_google(query):
    kit.search(query)


def youtube(video):
    kit.playonyt(video)

def get_news():
    news_headline = []
    result = requests.get(
        NEWS_FETCH_API_URL,
        params={
            "country":"in",
            "category":"general",
            "apiKey": NEWS_FETCH_API_KEY,
        },
        ).json()
    articles = result["articles"]
    for article in articles:
        news_headline.append(article["title"])
    return news_headline[:6]

def weather_forecast(city):
    res = requests.get(
        WEATHER_FORECAST_API_URL,
        params={
            "q":city,
            "appid":WEATHER_FORECAST_API_KEY,
            "units":"metric"
        },
        ).json()
    weather = res["weather"][0]["main"]
    temp = res["main"]["temp"]
    feels_like = res["main"]["feels_like"]
    return weather, f"{temp}°C", f"{feels_like}°C"
