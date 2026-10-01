#!/usr/bin/env python3
import os
import sys
import subprocess

SUPPORTED_EXTS = ('.flac', '.mp3')

def is_audio_file(filename):
    return filename.lower().endswith(SUPPORTED_EXTS) and not filename.startswith('.')

def find_album_folders(base_dir):
    """Find all subdirectories containing FLAC or MP3 files under base_dir."""
    album_dirs = []
    for root, _, files in os.walk(base_dir):
        if any(is_audio_file(f) for f in files):
            album_dirs.append(root)
    return sorted(album_dirs)

def get_audio_files(directory):
    """Get all FLAC and MP3 files in the specified directory."""
    if not os.path.exists(directory):
        return []
    files = []
    for f in os.listdir(directory):
        if is_audio_file(f):
            files.append(os.path.join(directory, f))
    return sorted(files)

def extract_and_show_cover(file_path):
    """Extract embedded cover art (FLAC/MP3) with fallback if mutagen is missing."""
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
            
            print("\n" + "="*50)
            if subprocess.call(["which", "chafa"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                subprocess.run(["chafa", "--size=40x20", tmp_cover])
            else:
                print("[Cover Art Loaded - Install 'chafa' for image preview]")
            print("="*50 + "\n")
    except ImportError:
        # Fallback gracefully if mutagen package is not installed on target OS
        pass
    except Exception:
        pass

def select_album(base_dir):
    """Let the user browse and select an album folder."""
    album_dirs = find_album_folders(base_dir)
    if not album_dirs:
        print(f"Error: No audio albums (FLAC/MP3) found under '{base_dir}'.")
        return None

    if len(album_dirs) == 1:
        return album_dirs[0]

    print("\n" + "=== Available Albums ===")
    for idx, album in enumerate(album_dirs, 1):
        rel_path = os.path.relpath(album, base_dir)
        print(f"[{idx:2d}] {rel_path}")

    print("=========================")
    try:
        choice_input = input(f"Select album number (1-{len(album_dirs)}) [q to quit]: ").strip()
        if choice_input.lower() == 'q':
            return None
        choice = int(choice_input) - 1
        if 0 <= choice < len(album_dirs):
            return album_dirs[choice]
    except (ValueError, KeyboardInterrupt):
        return None
    return None

def play_album(album_dir, base_dir):
    """Track selection menu for the chosen album."""
    songs = get_audio_files(album_dir)
    if not songs:
        print("No audio tracks found in this directory.")
        return 'change_album'

    # Create temporary input config for mpv to allow pressing 'q' to stop track
    input_conf = "/tmp/mpv_input.conf"
    with open(input_conf, "w") as f:
        f.write("q quit\nq stop\n")

    album_name = os.path.basename(album_dir)
    while True:
        print("\n" + "🎵 " * 3 + f" Current Album: {album_name} " + "🎵 " * 3)
        for idx, song in enumerate(songs, 1):
            filename = os.path.basename(song)
            print(f"[{idx:2d}] {filename}")

        print("\nCommands: Enter track number | [m] Move/Switch Album | [q] Quit Player")
        user_input = input("Selection: ").strip().lower()

        if user_input == 'q':
            return 'quit'
        elif user_input == 'm':
            return 'change_album'

        try:
            choice = int(user_input) - 1
            if 0 <= choice < len(songs):
                selected_song = songs[choice]
                print(f"\n▶ Now Playing: {os.path.basename(selected_song)}")
                print("[Info] Press 'q' or 'Ctrl+C' anytime during playback to return to this menu.\n")
                
                # Render cover art
                extract_and_show_cover(selected_song)
                
                # Execute mpv audio playback with custom input config
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
    """Print a helpful reminder on how to restart the player upon exit."""
    print("\n" + "="*50)
    print(" Exited Player.")
    print(" To start the player again, run:")
    print("   $ pi-player")
    print(" or:")
    print("   $ python3 /usr/bin/pi-player")
    print("="*50 + "\n")

def main():
    cwd = os.getcwd()
    music_base = cwd

    parts = cwd.split(os.sep)
    if "Music" in parts:
        music_index = parts.index("Music")
        music_base = os.sep.join(parts[:music_index + 1])
    elif "music" in parts:
        music_index = parts.index("music")
        music_base = os.sep.join(parts[:music_index + 1])
    elif os.path.exists("/root/music"):
        music_base = "/root/music"

    current_album = None

    while True:
        if not current_album:
            current_album = select_album(music_base)
            if not current_album:
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
