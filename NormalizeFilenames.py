import argparse
import os
import re
import sys
from os.path import join as join_path

try:
    from mutagen import File as MutagenFile
except ImportError:
    sys.exit("mutagen not installed. Run: pip install mutagen")


MUSIC_EXTENSIONS = (".mp3", ".m4a", ".flac", ".wav", ".ogg")
ILLEGAL_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

ARTIST_KEYS = ("TPE1", "artist", "ARTIST", "\xa9ART", "Author")
TITLE_KEYS = ("TIT2", "title", "TITLE", "\xa9nam")


def get_tag(tags, keys):
    for key in keys:
        val = tags.get(key)
        if not val:
            continue
        if isinstance(val, list):
            val = val[0]
        text = str(val).strip()
        if text:
            return text
    return None


def get_metadata(path):
    audio = MutagenFile(path)
    if audio is None or not audio.tags:
        return None
    artist = get_tag(audio.tags, ARTIST_KEYS)
    title = get_tag(audio.tags, TITLE_KEYS)
    if not artist or not title:
        return None
    return artist, title


def sanitize(s):
    s = ILLEGAL_CHARS.sub("", s)
    return re.sub(r"\s+", " ", s).strip()


def main():
    parser = argparse.ArgumentParser(
        description="Rename music files to '{Artist} - {Title}.ext' based on embedded tags."
    )
    parser.add_argument("folder", help="Music folder to scan recursively")
    parser.add_argument("--apply", action="store_true", help="Actually rename (default: dry run)")
    args = parser.parse_args()

    if not os.path.isdir(args.folder):
        sys.exit(f"Not a directory: {args.folder}")

    renamed = skipped = no_tags = conflicts = 0

    for root, _, files in os.walk(args.folder):
        for file in files:
            if not file.lower().endswith(MUSIC_EXTENSIONS):
                continue

            old_path = join_path(root, file)
            ext = os.path.splitext(file)[1].lower()

            meta = get_metadata(old_path)
            if not meta:
                no_tags += 1
                print(f"[no-tags]  {old_path}")
                continue

            artist, title = meta
            new_name = f"{sanitize(artist)} - {sanitize(title)}{ext}"

            if new_name == file:
                skipped += 1
                continue

            new_path = join_path(root, new_name)
            if os.path.exists(new_path) and os.path.normcase(new_path) != os.path.normcase(old_path):
                conflicts += 1
                print(f"[conflict] {file} -> {new_name} (target exists)")
                continue

            tag = "[rename]  " if args.apply else "[dry]     "
            print(f"{tag}{file} -> {new_name}")
            if args.apply:
                os.rename(old_path, new_path)
                renamed += 1

    summary = f"\nRenamed: {renamed}, already-ok: {skipped}, no-tags: {no_tags}, conflicts: {conflicts}"
    print(summary)
    if not args.apply:
        print("Dry run — pass --apply to actually rename.")


if __name__ == "__main__":
    main()
