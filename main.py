from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from langdetect import detect
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

from dbrequest import create_connection,add_music

db_conn = create_connection()

import time
import json
import re
import http.client
import json

# Setup Chrome options and enable performance logging
options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
capabilities = DesiredCapabilities.CHROME
capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

conn = http.client.HTTPSConnection("saavn.dev")

# Initialize Chrome WebDriver
service = Service(r'C:\Users\Mohammad.Ashraf\.wdm\drivers\chromedriver\win64\126.0.6478.182\chromedriver-win32\chromedriver.exe')

driver = webdriver.Chrome(service=service, options=options)

# Simulate slow network conditions
driver.execute_cdp_cmd('Network.emulateNetworkConditions', {
    'offline': False,
    'latency': 1000,  # 1000 ms latency
    'downloadThroughput': 500 * 1024,  # 500 kbps download speed
    'uploadThroughput': 500 * 1024   # 500 kbps upload speed
})

# Navigate to JioSaavn new releases
driver.get("https://www.jiosaavn.com/new-releases")

# Function to scroll to the bottom of the page slowly and fully
def scroll_to_bottom_slowly(driver, increment=300, delay=1, max_attempts=5):
    last_height = driver.execute_script("return document.body.scrollHeight")
    attempts = 0

    while attempts < max_attempts:
        driver.execute_script("window.scrollBy(0, arguments[0]);", increment)
        time.sleep(delay)  # Wait to load page
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height:
            attempts += 1
        else:
            attempts = 0  # Reset the attempts if new content is loaded
        
        last_height = new_height

# Scroll to the bottom to load all elements
scroll_to_bottom_slowly(driver)

# Wait for all elements to be loaded
try:
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "img"))
    )
except Exception as e:
    print(f"An error occurred: {e}")

# Give additional time for dynamic content to load
time.sleep(10)  # Increased wait time due to slow network

# Extract image URLs from network requests
image_urls = set()
logs = driver.get_log('performance')

# Extract and filter image URLs
for log in logs:
    message = json.loads(log['message'])['message']
    if ('Network.responseReceived' in message['method'] and
            'params' in message and
            'response' in message['params'] and
            'url' in message['params']['response']):
        url = message['params']['response']['url']
        if url.startswith('https://c.saavncdn.com/') and (url.endswith('.jpg') or url.endswith('.png')):
            image_urls.add(url)

driver.quit()


# Function to extract song details from URL
def extract_song_details(url):
    match = re.search(r'/(\d+)/(.+)-\d+x\d+\.jpg$', url)
    if match:
        song_info = match.group(2).replace('-', ' ')
        return song_info
    return None

def transliterate_text(text, lang_code):
    if lang_code == 'as':  # Assamese
        return transliterate(text, sanscript.ASSAMESE, sanscript.ITRANS)
    elif lang_code == 'bn':  # Bengali
        return transliterate(text, sanscript.BENGALI, sanscript.ITRANS)
    elif lang_code == 'gu':  # Gujarati
        return transliterate(text, sanscript.GUJARATI, sanscript.ITRANS)
    elif lang_code == 'hi':  # Hindi
        return transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS)
    elif lang_code == 'kn':  # Kannada
        return transliterate(text, sanscript.KANNADA, sanscript.ITRANS)
    elif lang_code == 'ml':  # Malayalam
        return transliterate(text, sanscript.MALAYALAM, sanscript.ITRANS)
    elif lang_code == 'mr':  # Marathi
        return transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS)
    elif lang_code == 'ne':  # Nepali
        return transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS)
    elif lang_code == 'or':  # Odia
        return transliterate(text, sanscript.ORIYA, sanscript.ITRANS)
    elif lang_code == 'pa':  # Punjabi
        return transliterate(text, sanscript.GURMUKHI, sanscript.ITRANS)
    elif lang_code == 'sa':  # Sanskrit
        return transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS)
    elif lang_code == 'ta':  # Tamil
        return transliterate(text, sanscript.TAMIL, sanscript.ITRANS)
    elif lang_code == 'te':  # Telugu
        return transliterate(text, sanscript.TELUGU, sanscript.ITRANS)
    elif lang_code == 'ur':  # Urdu
        return transliterate(text, sanscript.URDU, sanscript.ITRANS)
    else:
        return text

# Extract and print song details
slno = 1 
for url in image_urls:
    movie = extract_song_details(url)
    if movie:
        print("----------------------------",slno," ",movie,"------------------------------------")
        MovieTitle = movie
        # print(slno," ",movie)
        movie = movie.replace(" ","%20")
        conn.request("GET", f"/api/search/songs?query={movie}")
        slno += 1
        res = conn.getresponse()
        data = res.read()
        # print(type(json.loads(data.decode("utf-8"))))
        songs = json.loads(data.decode("utf-8"))
        # for key in songs:
        #     print(key)


        print("--------------------------------------- SONGS ---------------------------------------------\n")
        for sng in songs["data"]["results"]:
            print("song id:",sng["id"],"song title:",sng["name"],"\n")
            conn.request("GET",f"/api/songs/"+sng["id"]+"?lyrics=true")
            res = conn.getresponse()
            data = res.read()
            sng_lyrics = json.loads(data.decode("utf-8"))
            if sng_lyrics["success"]:
                # print("lyrics :",sng_lyrics["data"][0]["lyrics"]["lyrics"],"\n")
                lyrics = sng_lyrics["data"][0]["lyrics"]["lyrics"]
                lang_code = detect(lyrics)
                transliterated_lyric = transliterate_text(lyrics, lang_code)
                MovieTitle = sng_lyrics["data"][0]["album"]["name"]
                add_music(movieName=MovieTitle, songTitle=sng["name"], lyrics=transliterated_lyric, connection=db_conn)
            else:
                print(sng_lyrics["message"])

        # print(data.decode("utf-8"))
