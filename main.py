import os
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

import requests
import speech_recognition as sr
import webbrowser
import pyttsx3
import musicLibrary

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

recognizer = sr.Recognizer()
engine = pyttsx3.init()

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "").strip()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "").strip()
DEMO_HOST = "127.0.0.1"
DEMO_PORT = 5000
DEMO_URL = f"http://{DEMO_HOST}:{DEMO_PORT}"

SITES = {
    "google": "https://www.google.com",
    "instagram": "https://www.instagram.com",
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
}


def speak(text):
    engine.say(text)
    engine.runAndWait()


def normalize(text):
    return text.lower().strip().strip(".!?")


def city_from_command(command):
    markers = (
        "what's the weather in ",
        "what is the weather in ",
        "weather in ",
        "weather of ",
        "weather for ",
        "weather ",
    )
    for marker in markers:
        if marker in command:
            city = command.split(marker, 1)[1].strip(" ?.")
            if city:
                return city
    return "Delhi"


def get_news():
    if not NEWS_API_KEY:
        return "News API key is missing. Add NEWS_API_KEY to your .env file."

    try:
        response = requests.get(
            "https://newsapi.org/v2/top-headlines",
            params={"sources": "techcrunch", "apiKey": NEWS_API_KEY},
            timeout=10,
        )
    except requests.RequestException:
        return "I could not reach the news service."

    if response.status_code != 200:
        return "I could not fetch the news. Check your NewsAPI key."

    articles = response.json().get("articles", [])
    titles = [article.get("title") for article in articles if article.get("title")]
    if not titles:
        return "There are no headlines right now."

    return "Here are the top headlines. " + ". ".join(titles[:5])


def get_weather(city):
    """Live weather when WEATHER_API_KEY is set. Demo forecast until then."""
    if not WEATHER_API_KEY:
        return (
            f"Demo forecast for {city.title()}: 28 degrees and clear sky. "
            "Add WEATHER_API_KEY to your .env file when you want live weather."
        )

    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": city, "appid": WEATHER_API_KEY, "units": "metric"},
            timeout=10,
        )
    except requests.RequestException:
        return "I could not reach the weather service."

    if response.status_code == 401:
        return "The weather API key was rejected. Check WEATHER_API_KEY in your .env file."
    if response.status_code == 404:
        return f"I could not find weather for {city}."
    if response.status_code != 200:
        return "I could not fetch the weather."

    data = response.json()
    temp = data.get("main", {}).get("temp")
    description = ""
    weather = data.get("weather") or []
    if weather:
        description = weather[0].get("description", "")
    place = data.get("name") or city

    if temp is None:
        return f"I could not read the weather for {place}."

    detail = f" and {description}" if description else ""
    return f"The weather in {place} is {round(temp)} degrees{detail}."


def find_song(query):
    query = query.strip().lower()
    if not query:
        return None, None

    for name, url in musicLibrary.music.items():
        if name.lower() == query or query in name.lower() or name.lower() in query:
            return name, url
    return None, None


def process_command(command):
    command = normalize(command)

    for name, url in SITES.items():
        if f"open {name}" in command:
            webbrowser.open(url)
            return f"Opening {name}."

    if "news" in command:
        return get_news()

    if "weather" in command:
        return get_weather(city_from_command(command))

    if command.startswith("play"):
        song_query = command.split(" ", 1)[1].strip() if " " in command else ""
        name, link = find_song(song_query)
        if link:
            webbrowser.open(link)
            return f"Playing {name}."
        if song_query:
            return f"I could not find {song_query}."
        return "Tell me which song to play."

    return "I did not understand that. Try open Google, news, weather, or play a song."


DEMO_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>NOVA demo</title>
  <style>
    :root { color-scheme: dark; }
    body {
      margin: 0;
      min-height: 100vh;
      font-family: Segoe UI, sans-serif;
      background: #0e1116;
      color: #e8eef7;
      display: grid;
      place-items: center;
    }
    main { width: min(640px, calc(100% - 32px)); }
    h1 { margin-bottom: 4px; }
    p { color: #9aa8b8; }
    form { display: flex; gap: 8px; }
    input, button {
      font: inherit;
      border-radius: 8px;
      border: 1px solid #2c3644;
      padding: 12px;
    }
    input { flex: 1; background: #171d26; color: inherit; }
    button { background: #3d7eff; color: white; cursor: pointer; }
    #reply {
      margin-top: 16px;
      min-height: 72px;
      padding: 16px;
      border-radius: 8px;
      background: #171d26;
      white-space: pre-wrap;
    }
    ul { color: #9aa8b8; }
  </style>
</head>
<body>
  <main>
    <h1>NOVA</h1>
    <p>Demo URL: __DEMO_URL__</p>
    <form id="command-form">
      <input id="command" name="command" placeholder="Try: weather in Mumbai" autocomplete="off" required>
      <button type="submit">Run</button>
    </form>
    <div id="reply">Type a command to see NOVA reply here.</div>
    <ul>
      <li>open google</li>
      <li>news</li>
      <li>weather in Delhi</li>
      <li>play stealth</li>
    </ul>
  </main>
  <script>
    const form = document.getElementById("command-form");
    const input = document.getElementById("command");
    const reply = document.getElementById("reply");
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      reply.textContent = "Working...";
      const body = new URLSearchParams({ command: input.value });
      const response = await fetch("/command", { method: "POST", body });
      const data = await response.json();
      reply.textContent = data.reply;
    });
  </script>
</body>
</html>
""".replace("__DEMO_URL__", DEMO_URL)


class DemoHandler(BaseHTTPRequestHandler):
    def _send(self, status, body, content_type):
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, DEMO_PAGE, "text/html; charset=utf-8")
            return
        self._send(404, "Not found", "text/plain; charset=utf-8")

    def do_POST(self):
        if self.path != "/command":
            self._send(404, "Not found", "text/plain; charset=utf-8")
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        command = parse_qs(raw).get("command", [""])[0]
        reply = process_command(command)
        self._send(200, json.dumps({"reply": reply}), "application/json")

    def log_message(self, format, *args):
        print(f"[demo] {self.address_string()} {format % args}")


def run_demo():
    server = ThreadingHTTPServer((DEMO_HOST, DEMO_PORT), DemoHandler)
    print(f"NOVA demo is running at {DEMO_URL}")
    webbrowser.open(DEMO_URL)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDemo stopped.")
    finally:
        server.server_close()


def run_voice():
    speak("Initializing NOVA.")
    print(f"Voice mode is on. Demo page: {DEMO_URL}  (run: python main.py --demo)")

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)

    while True:
        print("recognizing...")
        try:
            with sr.Microphone() as source:
                print("listening....")
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
            word = recognizer.recognize_google(audio)
            if normalize(word) != "nova":
                continue

            speak("Yes")
            with sr.Microphone() as source:
                print("NOVA active....")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)
            command = recognizer.recognize_google(audio)
            print(command)
            reply = process_command(command)
            print(reply)
            speak(reply)

        except sr.WaitTimeoutError:
            continue
        except sr.UnknownValueError:
            continue
        except sr.RequestError as error:
            print(f"Speech service error: {error}")
        except Exception as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    import sys

    if "--demo" in sys.argv:
        run_demo()
    else:
        run_voice()
