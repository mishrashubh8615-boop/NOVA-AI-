# NOVA

Voice assistant that opens sites, reads news, checks weather, and plays songs from `musicLibrary.py`.

## Keep API keys off GitHub

Real keys live only in `.env`. That file is listed in `.gitignore`, so `git push` will not upload it.

1. Copy `.env.example` to `.env` if you do not already have one.
2. Paste your keys into `.env`:
   - `NEWS_API_KEY` from [NewsAPI](https://newsapi.org)
   - `WEATHER_API_KEY` from [OpenWeather](https://openweathermap.org/api) when you have it

Until `WEATHER_API_KEY` is set, weather replies with a demo forecast.

## Run

```bash
pip install -r requirements.txt
python main.py
```

Say **nova**, then a command such as `open google`, `news`, `weather in Mumbai`, or `play stealth`.

## Demo URL

```bash
python main.py --demo
```

Opens [http://127.0.0.1:5000](http://127.0.0.1:5000). Type the same commands in the page. This address only works on your computer.
