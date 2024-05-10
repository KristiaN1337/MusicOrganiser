import os
import shutil
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC


class colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    END = "\033[0m"


def get_first_contributing_artist_and_album(filepath):
    try:
        if filepath.endswith(".mp3"):
            audio = EasyID3(filepath)
        elif filepath.endswith(".flac"):
            audio = FLAC(filepath)
        else:
            print(f"{colors.RED}Unsupported file format: {filepath}{colors.END}")
            return None, None

        artist = audio.get("artist", None)
        album = audio.get("album", None)

        if artist and album:
            return (
                artist[0],
                album[0],
            )
        else:
            return None, None
    except Exception as e:
        print(f"{colors.RED}Error reading metadata for '{filepath}': {e}{colors.END}")
        return None, None


def sanitize_filename(filename):
    invalid_chars = ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]
    sanitized_filename = "".join(c for c in filename if c not in invalid_chars)
    return sanitized_filename


def update_playlist_file(playlist_path, old_path, new_path):
    try:
        with open(playlist_path, "r") as f:
            lines = f.readlines()

        updated_lines = [line.replace(old_path, new_path) for line in lines]

        return updated_lines
    except Exception as e:
        print(
            f"{colors.RED}Error updating playlist file '{playlist_path}': {e}{colors.END}"
        )
        return None


def create_playlist_file(playlist_path, playlist_entries):
    try:
        with open(playlist_path, "w") as f:
            f.writelines(playlist_entries)

        print(f"{colors.GREEN}Playlist file created: {playlist_path}{colors.END}")
    except Exception as e:
        print(
            f"{colors.RED}Error creating playlist file '{playlist_path}': {e}{colors.END}"
        )


def organize_music_files(
    source_dir, destination_dir, playlist_path, modified_playlist_destination
):
    playlist_entries = []

    for root, _, files in os.walk(source_dir):
        for filename in files:
            if filename.endswith((".mp3", ".flac")):
                source_file_path = os.path.join(root, filename)

                artist, album = get_first_contributing_artist_and_album(
                    source_file_path
                )
                if artist is None or album is None:
                    continue

                sanitized_artist = sanitize_filename(artist)
                sanitized_album = sanitize_filename(album)

                artist_dir = os.path.join(destination_dir, sanitized_artist)
                if not os.path.exists(artist_dir):
                    os.makedirs(artist_dir)

                album_dir = os.path.join(artist_dir, sanitized_album)
                if not os.path.exists(album_dir):
                    os.makedirs(album_dir)

                destination_file_path = os.path.join(album_dir, filename)
                shutil.move(source_file_path, destination_file_path)
                print(
                    f"{colors.GREEN}Moved '{filename}' to '{destination_file_path}'{colors.END}"
                )

                if playlist_path:
                    playlist_entries.append(
                        os.path.relpath(
                            destination_file_path, modified_playlist_destination
                        )
                        + "\n"
                    )

    if playlist_entries:
        modified_playlist_path = os.path.join(
            modified_playlist_destination, os.path.basename(playlist_path)
        )
        create_playlist_file(modified_playlist_path, playlist_entries)


source_directory = input(
    f"{colors.YELLOW}Enter the path to the source directory: {colors.END}"
)
destination_directory = input(
    f"{colors.YELLOW}Enter the path to the destination directory: {colors.END}"
)
playlist_path = input(
    f"{colors.YELLOW}Enter the path to the playlist file (leave blank if none): {colors.END}"
).strip()
modified_playlist_destination = input(
    f"{colors.YELLOW}Enter the destination directory for the modified playlist (leave blank if none): {colors.END}"
).strip()

organize_music_files(
    source_directory,
    destination_directory,
    playlist_path,
    modified_playlist_destination,
)
