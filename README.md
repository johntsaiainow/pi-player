# Pi Player

**Pi Player** is a lightweight, terminal-native **FLAC and MP3 audio player for embedded Linux**, designed for Raspberry Pi, Yocto/OpenEmbedded systems, headless appliances, and TTY console environments.

It combines a simple text-based music browser with `mpv` playback and optional terminal album-art rendering through `chafa` — no desktop environment, X11, Wayland, or graphical media player required.

The project is particularly suited for small embedded audio appliances such as the **Raspberry Pi + Google AIY Voice HAT**.

---

## Features

- **FLAC and MP3 playback**
- Recursive album and directory browsing
- Embedded album-art extraction
- Terminal cover-art rendering with `chafa`
- Interactive playback controls
- Volume and seek controls
- Headless / TTY-safe `mpv` configuration
- Graceful fallback when artwork support is unavailable
- Safe system shutdown directly from the player
- Standalone Linux operation
- Yocto / OpenEmbedded integration
- Automatic launch from `tty1`

---

## Design Philosophy

Pi Player is intentionally small.

Instead of building a complete graphical media stack, it uses standard Linux components:

```text
┌─────────────────────────────┐
│          Pi Player          │
│        Python / TTY         │
├──────────────┬──────────────┤
│    mutagen   │    chafa     │
│   Metadata   │  Cover Art   │
├──────────────┴──────────────┤
│             mpv             │
│       Audio Playback        │
├─────────────────────────────┤
│         ALSA / Linux        │
├─────────────────────────────┤
│ Raspberry Pi / Embedded HW  │
└─────────────────────────────┘
```

The result is a music player that can boot directly into a console and operate without a traditional desktop environment.

---

## Audio Playback

Pi Player uses `mpv` as its playback engine.

Playback is forced into audio-only mode:

```text
--vid=no
--vo=null
--ao=alsa
```

This is important on headless and embedded systems because MP3 and FLAC files may contain embedded artwork that `mpv` can otherwise interpret as a video stream.

Disabling video output avoids unnecessary display-driver initialization and makes playback much more reliable on console-only systems.

---

## Album Art

Pi Player can display album artwork directly in the terminal.

Artwork can be obtained from:

- FLAC metadata
- MP3 ID3v2 `APIC` tags
- `cover.jpg`
- `folder.jpg`

When available, `mutagen` extracts the embedded artwork and `chafa` renders it as ANSI terminal graphics.

If either component is unavailable, Pi Player continues operating normally with text-only output.

---

## Playback Controls

### During Playback

| Key | Action |
|---|---|
| `Space` | Pause / Resume |
| `Right` or `f` | Seek forward 5 seconds |
| `Left` or `b` | Seek backward 5 seconds |
| `Up` or `+` | Volume +5% |
| `Down` or `-` | Volume -5% |
| `q` or `Esc` | Stop playback and return to track selection |

### Album / Track Menus

| Command | Action |
|---|---|
| `1` – `N` | Select album or track |
| `m` | Return to album selection |
| `s` | Safely shut down the system |
| `q` | Exit Pi Player |

---

## Music Library Discovery

Pi Player searches for a usable music library automatically.

It supports common locations such as:

```text
~/Music
~/music
/root/music
```

and can also operate from the current working directory.

Music directories can contain multiple album subdirectories.

Example:

```text
music/
├── Beatles/
│   └── Abbey Road/
│       ├── 01 - Come Together.flac
│       ├── 02 - Something.flac
│       └── cover.jpg
│
└── Queen/
    └── Greatest Hits/
        ├── 01 - Bohemian Rhapsody.flac
        ├── 02 - Another One Bites the Dust.flac
        └── folder.jpg
```

---

# Standalone Linux Installation

Pi Player can run on Ubuntu, Debian, Raspberry Pi OS, and similar Linux distributions.

## Install Dependencies

```bash
sudo apt update

sudo apt install -y \
    python3 \
    python3-mutagen \
    mpv \
    chafa
```

Clone the repository:

```bash
git clone https://github.com/johntsaiainow/pi-player.git
cd pi-player
```

Run the player:

```bash
python3 files/player.py
```

Or install it manually:

```bash
sudo install -m 0755 files/player.py /usr/local/bin/pi-player
```

Then run:

```bash
pi-player
```

---

# Yocto / OpenEmbedded

Pi Player is also designed to be integrated directly into a custom embedded Linux image.

The repository includes:

```text
pi-player.bb
```

with the player source located under:

```text
files/player.py
```

A typical layer layout is:

```text
recipes-multimedia/
└── pi-player/
    ├── pi-player.bb
    └── files/
        └── player.py
```

Copy the recipe and source into your own Yocto layer.

For example:

```bash
mkdir -p meta-yourlayer/recipes-multimedia/pi-player/files

cp pi-player.bb \
   meta-yourlayer/recipes-multimedia/pi-player/

cp files/player.py \
   meta-yourlayer/recipes-multimedia/pi-player/files/
```

Add Pi Player to your image:

```bitbake
IMAGE_INSTALL:append = " pi-player"
```

The supplied recipe installs the executable as:

```text
/usr/bin/pi-player
```

and can automatically launch the application from the primary TTY.

Build your image normally:

```bash
bitbake core-image-base
```

or replace `core-image-base` with your custom image target.

---

## Example User Interface

### Album Selection

```text
=== Available Albums ===

[ 1] Queen/Greatest Hits
[ 2] Beatles/Abbey Road

=========================

Commands:
  Album number | [s] Shutdown | [q] Quit

Select: 1
```

### Track Selection

```text
🎵  Current Album: Greatest Hits  🎵

[ 1] 01.Bohemian Rhapsody.flac
[ 2] 02.Another One Bites The Dust.flac
[ 3] 03.Killer Queen.flac

Commands:
  Track number | [m] Albums | [s] Shutdown | [q] Exit

Selection: 1
```

### Playback

```text
▶ Now Playing: 01.Bohemian Rhapsody.flac

--------------------------------------------------
Controls during playback

[SPACE]    Pause / Resume
[← / b]    Seek -5 seconds
[→ / f]    Seek +5 seconds
[↑ / +]    Volume +5%
[↓ / -]    Volume -5%
[q / ESC]  Stop
--------------------------------------------------

        [ Terminal album art rendered by chafa ]
```

---

# Embedded Linux Use Case

Pi Player is intended to fit into a larger embedded audio platform without requiring a heavyweight graphical environment.

A typical system can look like:

```text
                     Raspberry Pi
                          │
              ┌───────────┴───────────┐
              │     Embedded Linux    │
              │      Yocto / Poky     │
              └───────────┬───────────┘
                          │
             ┌────────────┴────────────┐
             │                         │
        Pi Player                  AI / Agent
       TTY Interface                Services
             │                         │
             └────────────┬────────────┘
                          │
                        ALSA
                          │
                 Google AIY Voice HAT
                          │
                       Speaker
```

This architecture keeps the audio player independent from higher-level AI, voice-assistant, or automation services.

---

## Project Structure

```text
pi-player/
├── README.md
├── pi-player.bb
└── files/
    └── player.py
```

| File | Purpose |
|---|---|
| `README.md` | Project documentation |
| `pi-player.bb` | Yocto / OpenEmbedded BitBake recipe |
| `files/player.py` | Main Pi Player application |

---

## Target Platforms

Pi Player is designed primarily for:

- Raspberry Pi
- Google AIY Voice Kit / Voice HAT projects
- Yocto Linux
- OpenEmbedded
- Raspberry Pi OS
- Ubuntu / Debian
- Headless Linux systems
- Embedded audio appliances
- TTY-only Linux environments

---

## Requirements

### Required

```text
Python 3
mpv
ALSA
```

### Optional

```text
mutagen    Audio metadata and embedded artwork
chafa      Terminal album-art rendering
```

The application is designed to remain usable when the optional artwork components are unavailable.

---

## Goals

Pi Player follows a few simple principles:

**Terminal first.**  
A music player should not require a desktop environment just to play music.

**Embedded friendly.**  
Keep dependencies and system requirements small enough for custom Linux images.

**Unix friendly.**  
Use existing Linux tools rather than reinventing audio playback.

**Graceful degradation.**  
Missing artwork support should never prevent music from playing.

**Appliance ready.**  
The player should be capable of becoming the primary interface of a dedicated embedded audio device.

---

## Future Direction

Pi Player can serve as the audio frontend of a larger embedded AI system, including:

```text
Voice Input
    ↓
AI / Agent
    ↓
Music Selection
    ↓
Pi Player
    ↓
mpv / ALSA
    ↓
Voice HAT / Audio Hardware
```

This allows the terminal player to remain simple while external agents provide voice control, automation, music discovery, or other higher-level capabilities.

---

## License

MIT License.

See the repository license information for details.
