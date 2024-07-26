import os
from pipes import quote
import sqlite3
import struct
import subprocess
import time
import webbrowser
from playsound import playsound
import eel
import pyaudio
import pyautogui
from engine.command import speak
from engine.config import ASSISTANT_NAME
# Playing assiatnt sound function
import pywhatkit as kit
import pvporcupine
import requests
import geocoder
from engine.config import api_key
import speech_recognition as sr

from engine.helper import extract_yt_term, remove_words
from hugchat import hugchat

con = sqlite3.connect("jarvis.db")
cursor = con.cursor()

@eel.expose
def playAssistantSound():
    try:
        music_dir = "C:/Users/Meet/Desktop/CORAL/www/assets/audio/start_sound.mp3"
        playsound(music_dir)
    except Exception as e:
        print(e)

def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query.lower()

    app_name = query.strip()

    if app_name != "":

        try:
            cursor.execute(
                'SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening "+query)
                os.startfile(results[0][0])

            elif len(results) == 0: 
                cursor.execute(
                'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                
                if len(results) != 0:
                    speak("Opening "+query)
                    webbrowser.open(results[0][0])

                else:
                    speak("Opening "+query)
                    try:
                        os.system('start '+query)
                    except:
                        speak("not found")
        except:
            speak("some thing went wrong")

def PlayYoutube(query):
    search_term = extract_yt_term(query)
    speak("Playing "+search_term+" on YouTube")
    kit.playonyt(search_term)

def weatherreport(query):
    location = geocoder.ip('me')
    latitude, longitude = location.latlng

    url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()

    try :
        if data["cod"] == 200:
            city = data["name"]
            weather = data["weather"][0]["description"]
            temperature = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]
            speak(
                f"Weather in {city} is {weather} with {temperature}°C Temperature, {humidity}% Humidity and Wind Speed is {wind_speed} meters per second")
    except:
        speak(f"Sorry, I am currently unable to fetch weather data.")


def hotword():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    try:
        while True:
            with microphone as source:
                print("Listening for the wake word...")
                audio = recognizer.listen(source)
                
                try:
                    # Recognize speech using Google Web Speech API
                    transcription = recognizer.recognize_google(audio).lower()
                    
                    if "coral" in transcription:
                        print("Hotword detected: CORAL")
                        
                        # Perform the action when hotword is detected
                        pyautogui.keyDown("win")
                        pyautogui.press("j")
                        time.sleep(2)
                        pyautogui.keyUp("win")
                
                except sr.UnknownValueError:
                    # Handle when the speech is unintelligible
                    print("Could not understand audio")
                except sr.RequestError as e:
                    # Handle when there's an error with the Google Web Speech API
                    print(f"Could not request results; {e}")
                    
    except KeyboardInterrupt:
        # Handle exit on interrupt
        print("Hotword detection stopped")

# find contacts
def findContact(query):
    
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wahtsapp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        print(results[0][0])
        mobile_number_str = str(results[0][0])

        if not mobile_number_str.startswith('+91'):
            mobile_number_str = '+91' + mobile_number_str

        return mobile_number_str, query
    except:
        speak('not exist in contacts')
        return 0, 0
    
def whatsApp(mobile_no, message, flag, name):
    
    if flag == 'message':
        target_tab = 12
        jarvis_message = "message send successfully to "+name

    elif flag == 'call':
        target_tab = 7
        message = ''
        jarvis_message = "calling to "+name

    else:
        target_tab = 6
        message = ''
        jarvis_message = "staring video call with "+name


    # Encode the message for URL
    encoded_message = quote(message)
    print(encoded_message)
    # Construct the URL
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"

    # Construct the full command
    full_command = f'start "" "{whatsapp_url}"'

    # Open WhatsApp with the constructed URL using cmd.exe
    subprocess.run(full_command, shell=True)
    time.sleep(5)
    subprocess.run(full_command, shell=True)
    
    pyautogui.hotkey('ctrl', 'f')

    for i in range(1, target_tab):
        pyautogui.hotkey('tab')

    pyautogui.hotkey('enter')
    speak(jarvis_message)

# chat bot 
def chatBot(query):
    user_input = query.lower()
    chatbot = hugchat.ChatBot(cookie_path="engine\\cookies.json")
    id = chatbot.new_conversation()
    chatbot.change_conversation(id)
    response = chatbot.chat(user_input)
    print(response)

    # Check if the query contains any of the keywords
    keywords = ["write", "email", "code"]
    if any(keyword in user_input for keyword in keywords):
        speak("Please wait for a while, your task is in process....")
        # Convert response to string
        response_str = str(response)
        with open(f"Database/{''.join(user_input.split('write')[1:]).strip() }.txt", "w") as f:
            f.write(response_str)
            speak("Task is completed, please check result in the database folder")
    else:
        speak(response)
        return response

