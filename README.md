# Pi Player (`pi-player`)

`pi-player` is a lightweight, terminal-based FLAC & MP3 audio player engineered specifically for embedded Linux systems (such as the Raspberry Pi with Voice HAT) and TTY console environments.

It features **recursive directory navigation**, **terminal cover art rendering (via `chafa`)**, **full interactive playback controls (pause, seek, volume adjust, track stop)**, and **safe system shutdown**. By enforcing pure-audio parameters in `mpv`, it completely prevents console crashes caused by video driver initialization failures when playing files with embedded album artwork in headless setups.

---

## 🌟 Key Features

1. **Dual-Format Support & Tag Parsing (FLAC & MP3)**:
   - Scans and plays both `.flac` and `.mp3` files seamlessly.
   - Integrates `mutagen` parsing (with graceful fallback) to extract embedded artwork from FLAC Vorbis Comments and MP3 ID3v2 (APIC) tags, or local image files (`cover.jpg`, `folder.jpg`).

2. **Terminal Cover Art Rendering**:
   - Renders album covers directly in the TTY/Console screen using ANSI color blocks via `chafa`.
   - Gracefully falls back to text output if `chafa` or `mutagen` is missing on the target host.

3. **Headless & Driver-Safe Playback**:
   - Enforces `mpv` audio-only flags (`--vid=no --vo=null --ao=alsa`) to ignore video tracks entirely, preventing crashes caused by display driver initialization errors.

4. **Rich Interactive Playback Controls**:
   - Real-time keyboard control during playback via dynamic `mpv` keybindings.
   - Adjust volume, pause/resume, seek forward/backward, or stop the track instantly.

5. **Recursive Directory Browsing & Navigation**:
   - Automatically detects working directories, parent `Music` / `music` folders, or `/root/music`.
   - Switch easily between album folders (`[m]`) or trigger a safe system shutdown (`[s]`).

---

## 🎮 Playback & Navigation Controls

### During Track Playback

| Key / Shortcut | Action |
| :--- | :--- |
| **`Space`** | **Pause / Resume** playback |
| **`Right`** / **`f`** | **Seek forward 5 seconds** |
| **`Left`** / **`b`** | **Seek backward 5 seconds** |
| **`Up`** / **`+`** | **Increase volume (+5%)** |
| **`Down`** / **`-`** | **Decrease volume (-5%)** |
| **`q`** / **`Esc`** | **Stop track** and return to track selection menu |

### In Menus (Album & Track Selection)

| Input Command | Action |
| :--- | :--- |
| **`1` – `N`** | Select track or album number |
| **`m`** | **Move/Switch Album** (returns to album selection) |
| **`s`** | **Safe System Shutdown** (triggers `poweroff`) |
| **`q`** | **Quit Player** (returns to shell console with restart guide) |

---

## 🛠 Deployment Methods

### Option 1: Standalone CLI Usage

Ideal for testing on desktop Linux distributions (Ubuntu/Debian), Raspberry Pi OS, or any standard Linux terminal.

#### 1. Install Prerequisites
```bash
# Ubuntu / Debian / Raspberry Pi OS
sudo apt update
sudo apt install -y python3 python3-mutagen mpv chafa
2. Run the Player
Place player.py in your music folder (e.g., ~/Music) or run it from anywhere:

Bash
python3 player.py
Option 2: Yocto / OpenEmbedded Integration
Designed for embedding directly into custom Yocto images (e.g., Scarthgap branch) with automatic boot to tty1 console and launching the player on root autologin.

1. Create the Recipe (recipes-multimedia/pi-player/pi-player.bb)
Add the following recipe to your Yocto layer (e.g., meta-voicehat):

Code snippet
SUMMARY = "Terminal MP3/FLAC Player with Cover Art support"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://player.py"

# Runtime dependencies
RDEPENDS:${PN} = " \
    python3-core \
    mpv \
"

S = "${WORKDIR}"

do_install() {
    # 1. Install player script to /usr/bin/pi-player
    install -d ${D}${bindir}
    install -m 0755 ${WORKDIR}/player.py ${D}${bindir}/pi-player

    # 2. Configure automatic launch on tty1 root login
    install -d ${D}/root
    echo 'if [ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then' > ${D}/root/.profile
    echo '    exec pi-player' >> ${D}/root/.profile
    echo 'fi' >> ${D}/root/.profile

    echo 'if [ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then' > ${D}/root/.bashrc
    echo '    exec pi-player' >> ${D}/root/.bashrc
    echo 'fi' >> ${D}/root/.bashrc
}

FILES:${PN} += " \
    ${bindir}/pi-player \
    /root/.profile \
    /root/.bashrc \
"
Note: Place player.py inside recipes-multimedia/pi-player/files/player.py.

2. Update local.conf
Append the following configuration to conf/local.conf:

Code snippet
# Install pi-player into target image
IMAGE_INSTALL:append = " pi-player"

# Enable root console autologin without password (tty1 / Serial Console)
GETTY_AUTOLOGIN = "root"
AUTO_LOGIN = "root"
3. Build the Image
Bash
bitbake core-image-base
📖 Operational Example
1. Album Selection Menu
Plaintext
=== Available Albums ===
[ 1] Queen/Greatest Hits
[ 2] Beatles/Abbey Road
=========================
Commands: Enter album number | [s] Shutdown System | [q] Quit
Select: 1
2. Track Selection Menu
Plaintext
🎵 🎵 🎵  Current Album: Greatest Hits  🎵 🎵 🎵
[ 1] 01.Bohemian Rhapsody.flac
[ 2] 02.Another One Bites The Dust.flac
[ 3] 03.Killer Queen.flac

Commands: Track number | [m] Move/Switch Album | [s] Shutdown | [q] Exit
Selection: 1
3. Track Playback & Controls
Plaintext
▶ Now Playing: 01.Bohemian Rhapsody.flac
--------------------------------------------------
 Controls during playback:
  [SPACE] Pause/Resume  | [q/ESC] Stop & Back to Menu
  [RIGHT/f] Seek +5s   | [LEFT/b] Seek -5s
  [UP/+] Vol +5%        | [DOWN/-] Vol -5%
--------------------------------------------------

==================================================
 (Color ANSI cover art rendered here via chafa)
==================================================
📄 License
This project is licensed under the MIT License.
