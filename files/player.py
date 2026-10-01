#!/usr/bin/env python3
import os
import sys
import subprocess
import time

SUPPORTED_EXTS = ('.flac', '.mp3')

def is_audio_file(filename):
    return filename.lower().endswith(SUPPORTED_EXTS) and not filename.startswith('.')

def find_album_folders(base_dir):
    """Find all subdirectories containing FLAC or MP3 files."""
    album_dirs = []
    for root, _, files in os.walk(base_dir):
        if any(is_audio_file(f) for f in files):
            album_dirs.append(root)
    return sorted(album_dirs)

def get_audio_files(directory):
    """Get all FLAC/MP3 files in directory."""
    if not os.path.exists(directory):
        return []
    files = []
    for f in os.listdir(directory):
        if is_audio_file(f):
            files.append(os.path.join(directory, f))
    return sorted(files)

def extract_and_show_cover(file_path):
    """Extract and render embedded cover art with graceful fallbacks."""
    album_dir = os.path.dirname(file_path)
    for cover_name in ['cover.jpg', 'cover.png', 'folder.jpg', 'front.jpg']:
        cover_path = os.path.join(album_dir, cover_name)
        if os.path.exists(cover_path):
            if subprocess.call(["which", "chafa"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                print("\n" + "="*50)
                subprocess.run(["chafa", "--size=40x20", cover_path])
                print("="*50 + "\n")
            return

    try:
        from mutagen.flac import FLAC
        from mutagen.mp3 import MP3
        from mutagen.id3 import ID3, APIC, PictureType

        cover_data = None
        ext = os.path.splitext(file_path)[1].lower()

        if ext == '.flac':
            audio = FLAC(file_path)
            for pict in audio.pictures:
                if pict.type == PictureType.COVER_FRONT or pict.type == 3:
                    cover_data = pict.data
                    break
        elif ext == '.mp3':
            audio = MP3(file_path, ID3=ID3)
            for tag in audio.tags.values():
                if isinstance(tag, APIC):
                    cover_data = tag.data
                    break

        if cover_data:
            tmp_cover = "/tmp/current_cover.jpg"
            with open(tmp_cover, "wb") as f:
                f.write(cover_data)
            
            if subprocess.call(["which", "chafa"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                print("\n" + "="*50)
                subprocess.run(["chafa", "--size=40x20", tmp_cover])
                print("="*50 + "\n")
    except Exception:
        pass

def generate_mpv_input_conf():
    """Create custom keybindings for mpv background process."""
    conf_path = "/tmp/mpv_player_input.conf"
    bindings = [
        "q quit 0",
        "ESC quit 0",
        "SPACE cycle pause",
        "RIGHT seek 5",
        "LEFT seek -5",
        "f seek 5",
        "b seek -5",
        "UP add volume 5",
        "DOWN add volume -5",
        "+ add volume 5",
        "- add volume -5",
    ]
    with open(conf_path, "w") as f:
        f.write("\n".join(bindings) + "\n")
    return conf_path

def shutdown_system():
    """Safely shutdown the Raspberry Pi system."""
    print("\n" + "="*50)
    print(" Shutting down the system safely...")
    print("="*50 + "\n")
    time.sleep(1)
    subprocess.run(["poweroff"])

def select_album(base_dir):
    """Album selection menu."""
    album_dirs = find_album_folders(base_dir)
    if not album_dirs:
        print(f"Error: No audio albums found under '{base_dir}'.")
        return None

    if len(album_dirs) == 1:
        return album_dirs[0]

    print("\n" + "=== Available Albums ===")
    for idx, album in enumerate(album_dirs, 1):
        rel_path = os.path.relpath(album, base_dir)
        print(f"[{idx:2d}] {rel_path}")

    print("=========================")
    print("Commands: Enter album number | [s] Shutdown System | [q] Quit")
    try:
        choice_input = input("Select: ").strip().lower()
        if choice_input == 'q':
            return 'quit'
        elif choice_input == 's':
            shutdown_system()
            return 'quit'
        
        choice = int(choice_input) - 1
        if 0 <= choice < len(album_dirs):
            return album_dirs[choice]
    except (ValueError, KeyboardInterrupt):
        return None
    return None

def play_album(album_dir, base_dir):
    """Track selection menu and interactive playback controller."""
    songs = get_audio_files(album_dir)
    if not songs:
        print("No audio tracks found.")
        return 'change_album'

    input_conf = generate_mpv_input_conf()
    album_name = os.path.basename(album_dir)

    while True:
        print("\n" + "🎵 " * 3 + f" Current Album: {album_name} " + "🎵 " * 3)
        for idx, song in enumerate(songs, 1):
            filename = os.path.basename(song)
            print(f"[{idx:2d}] {filename}")

        print("\nCommands: Track number | [m] Move/Switch Album | [s] Shutdown | [q] Exit")
        user_input = input("Selection: ").strip().lower()

        if user_input == 'q':
            return 'quit'
        elif user_input == 'm':
            return 'change_album'
        elif user_input == 's':
            shutdown_system()
            return 'quit'

        try:
            choice = int(user_input) - 1
            if 0 <= choice < len(songs):
                selected_song = songs[choice]
                print(f"\n▶ Now Playing: {os.path.basename(selected_song)}")
                print("-" * 50)
                print(" Controls during playback:")
                print("  [SPACE] Pause/Resume  | [q/ESC] Stop & Back to Menu")
                print("  [RIGHT/f] Seek +5s   | [LEFT/b] Seek -5s")
                print("  [UP/+] Vol +5%        | [DOWN/-] Vol -5%")
                print("-" * 50 + "\n")

                extract_and_show_cover(selected_song)

                # Execute mpv with custom input configuration
                cmd = [
                    "mpv",
                    "--vid=no",
                    "--vo=null",
                    "--ao=alsa",
                    "--osc=no",
                    "--sub-font-provider=none",
                    f"--input-conf={input_conf}",
                    selected_song
                ]
                subprocess.run(cmd)
            else:
                print("Invalid track number!")
        except (ValueError, KeyboardInterrupt):
            print("\nPlayback stopped.")

def print_exit_reminder():
    print("\n" + "="*50)
    print(" Exited Player.")
    print(" To start the player again, run:")
    print("   $ pi-player")
    print("="*50 + "\n")

def main():
    cwd = os.getcwd()
    music_base = cwd

    parts = cwd.split(os.sep)
    if "Music" in parts:
        music_base = os.sep.join(parts[:parts.index("Music") + 1])
    elif "music" in parts:
        music_base = os.sep.join(parts[:parts.index("music") + 1])
    elif os.path.exists("/root/music"):
        music_base = "/root/music"

    current_album = None

    while True:
        if not current_album:
            current_album = select_album(music_base)
            if current_album == 'quit' or not current_album:
                print_exit_reminder()
                break

        action = play_album(current_album, music_base)
        if action == 'quit':
            print_exit_reminder()
            break
        elif action == 'change_album':
            current_album = None

if __name__ == "__main__":
    main()
