## Apple Music AAC GUI

A graphical Apple Music download tool developed based on [gamdl](https://github.com/glomatico/gamdl) and the ideas from [AppleMusic-Downloader](https://github.com/wenfeng110402/AppleMusic-Downloader), supporting AAC 256kbps, lyrics, cover art, conversion to FLAC, and more.

![View App](./screenshot.png)

[Steps: 0to1](./Use-Steps.md)

[简体中文](./README.md)

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
![MIT](https://img.shields.io/github/license/Zhischooler/applemusic-aac-gui?style=social)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey%3E)

✨ Features

· 🎵 Download songs, albums, playlists, and artist pages from Apple Music (subscription required)

· 🔉 Audio quality options: AAC 48–256 kbps (default 256)

· 📄 Download synchronized lyrics (.lrc) and embed them in the file

· 🖼️ Custom cover image size (e.g., 600x600)

· 🔄 Transcode AAC (m4a) to FLAC lossless format (requires FFmpeg)

· 📋 Batch queue downloading with configurable concurrency

· ⚙️ Persistent configuration (cover size, lyrics, FLAC conversion)

· 🖥️ Graphical interface built with PySide6, cross‑platform (Windows / macOS / Linux)

📦 Dependencies

· Python 3.10+

· gamdl ≥ 2.7.0

· FFmpeg (required only if you need FLAC conversion)

· PySide6 (GUI framework)

🚀 Quick Start

1. Clone the repository

```bash
git clone https://github.com/Zhischooler/apple-music-aac-gui.git
cd apple-music-aac-gui
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Install FFmpeg (if FLAC conversion is needed)

· Windows: Download from ffmpeg.org and add to PATH.

· macOS: brew install ffmpeg

· Linux: sudo apt install ffmpeg (or use your package manager)

4. Obtain Cookies

Use a browser extension like Get cookies.txt LOCALLY to export cookies.txt (Netscape format) from music.apple.com.

5. Run

```bash
python apple_music_gui.py
```

⚙️ Configuration File

The program automatically generates config.txt on first run, with the following format:

```
coversize:600x600      # Cover image size (width x height)
downloadlyrics:true    # Whether to download lyrics
m4atoflac:false        # Whether to convert to FLAC
```

You can edit the file directly or adjust settings via the GUI; changes are saved automatically.

🛠️ Technical Architecture

· GUI Framework: PySide6 (Qt for Python)

· Download Engine: gamdl (Python package)

· Inter‑process Communication: subprocess for real‑time log output

· Configuration Management: plain text key‑value pairs

🙏 Acknowledgements

· gamdl – core downloading implementation

· wenfeng110402/AppleMusic-Downloader – UI design reference

📄 License

This project is licensed under the MIT License – see the LICENSE file for details.

⚠️ Disclaimer

· This tool is for educational and personal use only. Do not use it for commercial purposes or copyright infringement.

· Please ensure you have an active Apple Music subscription and comply with Apple’s terms of service.

· The author assumes no responsibility for any consequences arising from the use of this tool.
