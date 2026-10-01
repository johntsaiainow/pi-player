Here is the complete, professional English version of the README.md. It covers both Standalone CLI execution and Yocto Embedded Integration, along with detailed features and command-line instructions.

Markdown
# Pi Player (`pi-player`)

`pi-player` is a lightweight, terminal-based FLAC & MP3 audio player engineered specifically for embedded Linux systems (such as the Raspberry Pi) and TTY console environments.

It features **recursive directory navigation**, **terminal cover art rendering (via `chafa`)**, and **one-key playback interruption**. By enforcing pure-audio parameters in `mpv`, it completely prevents console crashes caused by video driver initialization failures when playing files with embedded album artwork in headless setups.

---

## 🌟 Key Features

1. **Dual-Format Support & Tag Parsing (FLAC & MP3)**:
   - Scans and plays both `.flac` and `.mp3` files seamlessly.
   - Integrates `mutagen` parsing to automatically extract embedded artwork from FLAC Vorbis Comments and MP3 ID3v2 (APIC) tags.

2. **Terminal Cover Art Rendering**:
   - Renders album covers directly in the TTY/Console screen using ANSI color blocks via `chafa`.
   - Gracefully falls back to a clean text-based menu if `chafa` or `mutagen` is not present on the host system.

3. **Headless & Driver-Safe Playback**:
   - Enforces `mpv` flags (`--vid=no --vo=null --ao=alsa`) to ignore video tracks entirely, preventing crashes caused by headless display driver initialization errors.

4. **Recursive Directory Browsing & Navigation (Move/Switch)**:
   - Automatically detects the current working directory, parent `Music` / `music` folders, or `/root/music`.
   - Provides an intuitive album selection menu to freely navigate between artists and folders.

5. **Interactive Playback Controls**:
   - Press **`q`** or **`Ctrl+C`** during track playback: Immediately stops the song and returns to the track menu.
   - Press **`m`** on the menu: Switch/move to another album folder.
   - Press **`q`** on the menu: Exits the player with a clear reminder of how to relaunch it.

---

## 🛠 Deployment Methods

### Option 1: Standalone CLI Usage

Ideal for testing on desktop Linux distributions (e.g., Ubuntu/Debian), Raspberry Pi OS, or any system with Python 3 installed.

#### 1. Install Prerequisites
Install the required packages using your system package manager:
```bash
# Ubuntu / Debian / Raspberry Pi OS
sudo apt update
sudo apt install -y python3 python3-mutagen mpv chafa
2. Run the Player
Place player.py in your music directory (e.g., ~/Music) or run it directly from any location:

Bash
python3 player.py
Option 2: Yocto / OpenEmbedded Integration
Designed for embedding directly into custom Yocto images (e.g., Scarthgap branch), enabling automatic boot to tty1 console and launching the player on root autologin.

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
    echo '[ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ] && exec pi-player' >> ${D}/root/.profile
}

FILES:${PN} += " \
    ${bindir}/pi-player \
    /root/.profile \
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
📖 User Guide & Operations
1. Album Selection Menu
Upon startup, if multiple album directories are detected under the base path, the player displays an album list:

Plaintext
=== Available Albums ===
[ 1] Queen/Greatest Hits
[ 2] Beatles/Abbey Road
=========================
Select album number (1-2) [q to quit]: 1
Enter a number (1-N): Selects and enters the chosen album folder.

Enter q: Exits the player.

2. Track Selection Menu
After picking an album, the track list is displayed:

Plaintext
🎵 🎵 🎵  Current Album: Greatest Hits  🎵 🎵 🎵
[ 1] 01.Bohemian Rhapsody.flac
[ 2] 02.Another One Bites The Dust.flac
[ 3] 03.Killer Queen.flac

Commands: Enter track number | [m] Move/Switch Album | [q] Quit Player
Selection: 1
Enter track number (1-N): Starts playing the selected audio file.

Enter m: Returns to the main menu to switch albums.

Enter q: Exits the player.

3. Playback Controls
Selecting a song renders the embedded cover art and begins audio playback:

Plaintext
▶ Now Playing: 01.Bohemian Rhapsody.flac
[Info] Press 'q' or 'Ctrl+C' anytime during playback to return to this menu.

==================================================
 (Color ANSI cover art rendered here via chafa)
==================================================
Press q or Ctrl+C: Instantly stops track playback and returns to the track menu.

Track Completion: Automatically returns to the track menu when the song ends.

4. Exit & Restart Reminder
Pressing q on any menu exits the script and displays clear relaunch commands:

Plaintext
==================================================
 Exited Player.
 To start the player again, run:
   $ pi-player
 or:
   $ python3 /usr/bin/pi-player
==================================================
📄 License
This project is licensed under the MIT License.
