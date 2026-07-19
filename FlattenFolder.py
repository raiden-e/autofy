import argparse
import os
import shutil
import sys
from os.path import join as join_path

MUSIC_EXTENSIONS = (".mp3", ".m4a", ".flac", ".wav", ".ogg")


def main():
    parser = argparse.ArgumentParser(
        description="Move all music files from subfolders up into the target folder, then remove empty subdirs."
    )
    parser.add_argument("folder", help="Target folder to flatten")
    parser.add_argument("--apply", action="store_true", help="Actually move files (default: dry run)")
    parser.add_argument("--all", action="store_true", help="Move all files, not just music")
    parser.add_argument("--keep-dirs", action="store_true", help="Don't remove empty subdirs after moving")
    args = parser.parse_args()

    if not os.path.isdir(args.folder):
        sys.exit(f"Not a directory: {args.folder}")

    target = os.path.abspath(args.folder)
    moved = skipped = conflicts = 0

    for root, _, files in os.walk(target, topdown=False):
        if os.path.abspath(root) == target:
            continue

        for file in files:
            if not args.all and not file.lower().endswith(MUSIC_EXTENSIONS):
                continue

            old_path = join_path(root, file)
            new_path = join_path(target, file)

            if os.path.exists(new_path):
                conflicts += 1
                rel = os.path.relpath(old_path, target)
                print(f"[conflict] {rel} (target {file} exists)")
                continue

            tag = "[move]    " if args.apply else "[dry]     "
            print(f"{tag}{os.path.relpath(old_path, target)} -> {file}")
            if args.apply:
                shutil.move(old_path, new_path)
                moved += 1

        if args.apply and not args.keep_dirs and not os.listdir(root):
            os.rmdir(root)
            skipped += 1

    print(f"\nMoved: {moved}, conflicts: {conflicts}, dirs removed: {skipped}")
    if not args.apply:
        print("Dry run — pass --apply to actually move.")


if __name__ == "__main__":
    main()
