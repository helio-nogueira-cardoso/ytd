# YTD — YouTube Downloader

A small desktop YouTube downloader. Paste a URL, hit Download, choose where to
save the MP4. Tkinter UI, `yt-dlp` under the hood, `ffmpeg` bundled.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)

---

## Features

- One-field UI — paste a YouTube URL, press Enter, done.
- Downloads the best available video + audio and merges into MP4.
- Live progress bar with download speed.
- Configurable download folder — set once on first launch, change anytime
  via **Configurações → Pasta de download...**
- Files are named after the video title (sanitized).
- Bundled `ffmpeg` in the released executables — no extra installs.
- Pre-built binaries for **Windows** and **Linux** on every tagged release.

## Where the config lives

The download folder is persisted across sessions in:

- **Linux/macOS:** `~/.config/ytd/config.json` (or `$XDG_CONFIG_HOME/ytd/`)
- **Windows:** `%APPDATA%\ytd\config.json`

## Why a desktop app

YouTube actively blocks downloads from datacenter IPs (cloud hosts / VPS).
Running on your own machine uses your residential IP, which is what
`yt-dlp` is designed for. The previous Streamlit version was migrated to
a native Tkinter app for this reason.

## Install — pre-built binary (recommended)

Grab the latest from the [Releases page](https://github.com/helio-nogueira-cardoso/ytd/releases):

- **Windows:** `ytd.exe` — double-click to run.
- **Linux:** `ytd` — `chmod +x ytd && ./ytd`.

No Python or `ffmpeg` install needed.

## Install — from source

```bash
git clone https://github.com/helio-nogueira-cardoso/ytd.git
cd ytd
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Requires Python 3.10+. On Linux you may need `python3-tk` (Debian/Ubuntu:
`sudo apt install python3-tk`).

## Building locally

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name ytd \
    --collect-all imageio_ffmpeg \
    --collect-all yt_dlp \
    --collect-all curl_cffi \
    main.py
```

The binary lands in `dist/`.

## Releasing

The GitHub Actions workflow `.github/workflows/build.yml` builds Windows
and Linux binaries automatically on every tag matching `v*` and attaches
them to a GitHub Release.

```bash
git tag v1.0.0
git push origin v1.0.0
```

Watch the run under the repo's "Actions" tab. Artifacts also appear on
manual runs (workflow_dispatch) for testing.

## Project structure

```
.
├── main.py                       # Tkinter app + yt-dlp logic
├── requirements.txt              # yt-dlp, curl-cffi, imageio-ffmpeg
├── .github/workflows/build.yml   # cross-platform release builds
├── .gitignore
└── README.md
```

## Troubleshooting

- **"Sign in to confirm you're not a bot"** — your IP is being challenged
  by YouTube. Usually only happens on cloud/VPS IPs; residential
  connections rarely hit this. Try again or switch network.
- **`yt-dlp` errors after a YouTube change** — bump the dep:
  `pip install --upgrade yt-dlp` (and rebuild the binary if you ship one).
- **Linux: `ModuleNotFoundError: No module named 'tkinter'`** — install
  the Tk binding for Python: `sudo apt install python3-tk`.

## Disclaimer

For personal and educational use only. Downloading YouTube videos may
violate [YouTube's Terms of Service](https://www.youtube.com/t/terms)
unless the content is offered for offline download (e.g. via YouTube
Premium) or is in the public domain / under a permissive license. The
author is not responsible for how this tool is used.

## Author

**Hélio Nogueira Cardoso**
GitHub: [@helio-nogueira-cardoso](https://github.com/helio-nogueira-cardoso)
