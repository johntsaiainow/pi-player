# Pi Player (`pi-player`)

A lightweight, terminal-based FLAC & MP3 audio player built specifically for embedded Linux and Yocto environments (such as Raspberry Pi with Voice HAT). It features recursive directory navigation, terminal cover art rendering via `chafa`, and pure-audio playback via `mpv` to bypass hardware video driver initialization errors in headless setups.

---

## Features

- **Multi-Format Support**: Plays `.flac` and `.mp3` files seamlessly.
- **Embedded Cover Art Support**: Automatically extracts cover art from ID3 (MP3) or Vorbis comments (FLAC) using `mutagen`.
- **Terminal Rendering**: Displays album covers directly in the TTY console using `chafa`.
- **Headless & Driver-Safe**: Configured with `mpv` audio-only flags (`--vid=no --vo=null --ao=alsa`) to prevent console crashes caused by embedded cover art.
- **Recursive Directory Browsing**: Automatically scans `./Music`, `/root/music`, or subdirectories for album folders and lets you switch between them easily.
- **Interactive Controls**:
  - `q` during playback: Stops current track and returns to the album menu.
  - `m` on track menu: Switch/move to another album folder.
  - `q` on menu: Exit player with clear restart instructions.

---

## Directory Structure

```text
.
├── player.py       # Main Python player script
└── README.md       # Repository documentation
Quick Start (Standalone / Testing)
Prerequisites
Ensure the following tools are available on your host or target Linux system:

Bash
# Ubuntu / Debian
sudo apt install python3 python3-mutagen mpv chafa
Execution
Simply run the script in any directory containing music or within a Music parent folder:

Bash
python3 player.py
Integration with Yocto / OpenEmbedded
To include pi-player in your Yocto build (e.g., meta-voicehat or meta-pi-agent layer):

1. Recipe Setup (recipes-multimedia/pi-player/pi-player.bb)
Code snippet
SUMMARY = "Terminal MP3/FLAC Player with Cover Art support"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://player.py"

RDEPENDS:${PN} = " \
    python3-core \
    mpv \
"

S = "${WORKDIR}"

do_install() {
    install -d ${D}${bindir}
    install -m 0755 ${WORKDIR}/player.py ${D}${bindir}/pi-player

    # Automatically launch pi-player on tty1 root autologin
    install -d ${D}/root
    echo '[ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ] && exec pi-player' >> ${D}/root/.profile
}

FILES:${PN} += " \
    ${bindir}/pi-player \
    /root/.profile \
"
2. Enable in local.conf
Add pi-player to your image configuration (conf/local.conf):

Code snippet
IMAGE_INSTALL:append = " pi-player"

# Enable root console autologin (optional)
GETTY_AUTOLOGIN = "root"
AUTO_LOGIN = "root"
License
This project is open-source under the MIT License.
