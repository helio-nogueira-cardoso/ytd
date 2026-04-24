# YTD — YouTube Downloader

A small, friendly Streamlit web app that downloads YouTube videos to your device
as MP4. Paste a URL, press Enter, and save the file.

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/built%20with-Streamlit-ff4b4b)

---

## Features

- One-field UI — paste a YouTube URL and go.
- Downloads the **best available MP4** (progressive or merged by `yt-dlp`).
- Shows the video **thumbnail, title, uploader and duration** before saving.
- File is renamed to the video title (sanitized for the filesystem).
- Submits on **Enter** (form) and on button click.
- Automatic cleanup of stale temp files between downloads.
- Works locally and on any platform that can run a Python web app
  (Heroku-style PaaS, a VPS, a container, etc.).

## Tech stack

- [Streamlit](https://streamlit.io/) — UI
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — downloader engine
- Python 3.9+

> Note: the app originally used `pytube`, which has been unreliable against
> YouTube's current endpoints. It was migrated to `yt-dlp`, which is actively
> maintained.

## Requirements

- Python **3.9+** (tested on 3.13)
- `pip` / `venv`
- An active internet connection

## Quick start (local)

```bash
# 1. Clone
git clone https://github.com/helio-nogueira-cardoso/ytd.git
cd ytd

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
streamlit run main.py
```

Streamlit will open the app at http://localhost:8501.

## Usage

1. Open the app in your browser.
2. Paste a YouTube URL into the input field.
3. Press **Enter** or click **Download**.
4. Wait for the spinner to finish. You'll see the thumbnail, title and duration.
5. Click **Save video** to download the MP4 to your machine.

## How it works

- `yt-dlp` fetches the video metadata and streams, picking the best
  `mp4` progressive format (or merging audio + video when needed).
- The file is written to the OS temp directory under a `ytd_<videoId>.mp4`
  name so it can be safely cleaned up later.
- Streamlit serves the file via `st.download_button`, renaming it to the
  sanitized video title on the client side.
- Before every download, files older than 10 minutes that match the `ytd_`
  prefix are removed to keep the temp directory tidy.

## Project structure

```
.
├── main.py            # Streamlit app (UI + download logic)
├── requirements.txt   # Python dependencies (streamlit, yt-dlp)
├── Procfile           # PaaS entrypoint (Heroku-compatible)
├── setup.sh           # Generates a valid ~/.streamlit/config.toml at boot
├── .gitignore
└── README.md
```

## Deployment

The repository is ready for Heroku-style PaaS deployment.

- `Procfile` declares the web process:
  `web: sh setup.sh && streamlit run main.py`
- `setup.sh` writes a valid Streamlit config honoring the `$PORT` env var.

Generic steps:

```bash
# Heroku CLI
heroku create <app-name>
git push heroku main
heroku open
```

On Railway, Render, Fly.io, etc., point the service at `main` and use the same
start command from the `Procfile`.

### Running in Docker (optional)

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8501
EXPOSE 8501
CMD ["sh", "-c", "streamlit run main.py --server.port=$PORT --server.headless=true"]
```

## Configuration

Streamlit looks for `~/.streamlit/config.toml`. `setup.sh` creates one with:

```toml
[server]
headless = true
enableCORS = false
port = $PORT   # defaults to 8501
```

Useful environment variables:

| Variable | Purpose                                  | Default |
|----------|------------------------------------------|---------|
| `PORT`   | Port Streamlit binds to (PaaS providers) | `8501`  |

## Troubleshooting

- **`HTTP 400 Bad Request` when downloading** — usually means `yt-dlp` is out
  of date. Bump it: `pip install --upgrade yt-dlp`.
- **`Error parsing config toml`** — the `~/.streamlit/config.toml` file is
  malformed. Delete it (`rm ~/.streamlit/config.toml`) and re-run
  `sh setup.sh`, or remove the file entirely and let Streamlit use defaults.
- **`ffmpeg not found`** — some formats require `ffmpeg` to merge video and
  audio. Install it via your package manager (`sudo apt install ffmpeg` /
  `brew install ffmpeg`). The default `best[ext=mp4]` format rarely needs it.
- **"Download failed" for a specific URL** — age-restricted, region-blocked,
  or private videos cannot be downloaded without extra authentication.

## Development

Auto-reload is built into Streamlit — just save the file and the browser
reloads. To validate without opening the browser:

```bash
python -c "import ast; ast.parse(open('main.py').read())"
```

## Disclaimer

This project is provided for **personal and educational use only**. Downloading
YouTube videos may violate [YouTube's Terms of Service](https://www.youtube.com/t/terms)
unless the content is clearly offered for offline download (for example, via
YouTube Premium) or is in the public domain / released under a permissive
license. The author is not responsible for how this tool is used.

## Author

**Hélio Nogueira Cardoso**
GitHub: [@helio-nogueira-cardoso](https://github.com/helio-nogueira-cardoso)
