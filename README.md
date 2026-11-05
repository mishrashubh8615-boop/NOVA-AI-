# NOVA

Voice assistant that opens sites, reads news, checks weather, and plays songs from `musicLibrary.py`.

## Keep API keys off GitHub

Real keys live only in `.env`. That file is listed in `.gitignore`, so `git push` will not upload it.

1. Copy `.env.example` to `.env` if you do not already have one.
2. Paste your keys into `.env`:
   - `NEWS_API_KEY` from [NewsAPI](https://newsapi.org

## Run

```bash
pip install -r requirements.txt
python main.py
```

Say **nova**, then a command such as `open google`, `news`, or `play stealth`.
