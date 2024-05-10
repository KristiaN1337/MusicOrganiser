import os
import shutil
import shlex
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC


class colors:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    WHITE = "\033[97m"
    END = "\033[0m"


def print_border(text):
    border_length = len(text) + 4
    print("╔" + "═" * border_length + "╗")
    print("║ " + text + " ║")
    print("╚" + "═" * border_length + "╝")


def get_artist_and_album(filepath):
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
            return artist[0], album[0]
        else:
            print(
                f"{colors.YELLOW}Missing artist or album information for '{filepath}'. Skipping.{colors.END}"
            )
            return None, None
    except Exception as e:
        print(f"{colors.RED}Error reading metadata for '{filepath}': {e}{colors.END}")
        return None, None


def sanitize_filename(filename):
    invalid_chars = ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]
    sanitized_filename = "".join(c if c not in invalid_chars else "_" for c in filename)
    return sanitized_filename


def backup_playlist_file(playlist_path):
    try:
        backup_path = playlist_path + ".bak"
        shutil.copyfile(playlist_path, backup_path)
        print()
        print_border_line()
        print()
        print(
            f"{colors.GREEN}Backup of the playlist file created: {backup_path}{colors.END}"
        )
        print()
        print_border_line()
        print()
        return backup_path
    except Exception as e:
        print_border_line()
        print()
        print(
            f"{colors.RED}Error creating backup of the playlist file: {e}{colors.END}"
        )
        print()
        print_border_line()
        return None


def rollback_changes(file_path_mapping, original_playlist_path, playlist_contents):
    try:
        original_playlist_path = original_playlist_path.replace('"', "")

        with open(original_playlist_path, "w", encoding="utf-8") as f:
            for line in playlist_contents:
                f.write(line + "\n")

        print()
        print_border_line()
        print()
        print(
            f"{colors.GREEN}Restored original playlist file: {original_playlist_path}{colors.END}"
        )
        print()
        print_border_line()
        print()

        for old_path, new_path in file_path_mapping.items():
            if os.path.exists(new_path):
                shutil.move(new_path, old_path)
                print(
                    f"{colors.GREEN}Rolled back{colors.END} '{colors.YELLOW}{os.path.basename(new_path)}{colors.END}' {colors.WHITE}to{colors.END} '{colors.BLUE}{old_path}{colors.END}'"
                )
            else:
                print(
                    f"{colors.RED}File '{new_path}' not found. Rollback failed.{colors.END}"
                )

        print("\n" * 1)
        print_border(f"{colors.BLUE}Rollback completed.{colors.END}")
        print("\n" * 1)
    except Exception as e:
        print_border(f"{colors.RED}Error during rollback: {e}{colors.END}")


def resolve_relative_paths(playlist_contents, playlist_dir):
    resolved_paths = []
    for line in playlist_contents:
        line = line.strip()
        if not os.path.isabs(line):
            resolved_path = os.path.abspath(os.path.join(playlist_dir, line))
            resolved_paths.append(resolved_path)
        else:
            resolved_paths.append(line)
    return resolved_paths


def organize_music_files(playlist_path, destination_dir=None):
    file_path_mapping = {}
    playlist_contents = []
    playlist_contents_memory = []

    if destination_dir is None:
        destination_dir = r"PATH_TO_DEFAULT_DESTINATION_DIRECTORY"

    try:
        playlist_path = shlex.split(playlist_path)[0]

        backup_path = backup_playlist_file(playlist_path)
        if not backup_path:
            return None

        playlist_dir = os.path.dirname(playlist_path)

        with open(playlist_path, "r", encoding="utf-8") as f:
            playlist_contents = f.readlines()
            playlist_contents_memory = playlist_contents[:]

        playlist_contents = resolve_relative_paths(playlist_contents, playlist_dir)

        missing_files = []
        for line in playlist_contents:
            line = line.strip()
            if not os.path.isfile(line):
                missing_files.append(line)

        if missing_files:
            print(f"{colors.RED}The following files are missing:")
            print()
            for file in missing_files:
                print(file)
            print()
            print(
                f"{colors.YELLOW}Please make sure all files are present and try again.{colors.END}"
            )
            return None

        for line in playlist_contents:
            line = line.strip()
            if os.path.isfile(line):
                artist, album = get_artist_and_album(line)
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

                filename = os.path.basename(line)
                destination_file_path = os.path.join(album_dir, filename)
                shutil.move(line, destination_file_path)
                print(
                    f"{colors.GREEN}Moved{colors.END} '{colors.YELLOW}{filename}{colors.END}' to '{colors.BLUE}{destination_file_path}{colors.END}'"
                )

                file_path_mapping[line] = destination_file_path

        with open(playlist_path, "w", encoding="utf-8") as f:
            for new_path in file_path_mapping.values():
                f.write(f"{new_path}\n")

        print("\n" * 1)
        print(f"{colors.GREEN}Music files organized successfully!{colors.END}")
        print()

        return file_path_mapping, playlist_contents  # Return both variables
    except Exception as e:
        print(
            f"{colors.RED}Error reading or organizing playlist file '{playlist_path}': {e}{colors.END}"
        )
        rollback_changes(file_path_mapping, playlist_path, playlist_contents_memory)
        return None


def print_border_line():
    terminal_width = shutil.get_terminal_size().columns
    print("═" * terminal_width)


def main():
    while True:
        print_border(f"{colors.BLUE}KristiaN's Music Organiser v0.5{colors.END}")
        print("\n" * 1)

        playlist_path = input(
            f"{colors.YELLOW}Enter the path to the M3U playlist file: {colors.END}"
        )
        destination_directory = input(
            f"{colors.YELLOW}Enter the path to the destination directory for the organized music files (press Enter for default): {colors.END}"
        )
        print()

        if not destination_directory:
            destination_directory = r"PATH_TO_DEFAULT_DESTINATION_DIRECTORY"

        organize_result = organize_music_files(playlist_path, destination_directory)
        while organize_result is None:
            retry = input(
                f"Enter '{colors.GREEN}retry{colors.END}' to try again, or press {colors.RED}Enter{colors.END} to exit:"
            )
            if retry.lower() == "retry" or retry.lower() == "r":
                organize_result = organize_music_files(
                    playlist_path, destination_directory
                )
            else:
                return

        if organize_result:
            file_path_mapping, playlist_contents = organize_result

            num_files_moved = len(file_path_mapping)
            print()
            print_border(
                f"{colors.BLUE}Total files moved: {num_files_moved}{colors.END}"
            )
            print("\n" * 1)

            prompt = input(
                f"Enter '{colors.RED}rollback{colors.END}' to undo changes, '{colors.GREEN}rerun{colors.END}' to organize again, or press {colors.YELLOW}ENTER{colors.END} to close the script: "
            )
            if prompt.lower() == "rollback":
                rollback_changes(file_path_mapping, playlist_path, playlist_contents)
            elif prompt.lower() != "rerun" and prompt.lower() != "r":
                return


if __name__ == "__main__":
    main()
