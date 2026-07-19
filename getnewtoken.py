#!/usr/bin/env python3
"""Helper CLI to refresh the Spotipy OAuth cache used by Autofy.

Typical usage:
    python3 getnewtoken.py

During the run you'll be prompted to remove the existing cache file
(`./util/spotify.cache`). After confirming, a browser window opens for the
Spotify auth flow. Once you accept, the cache file will be rewritten with a
fresh refresh token.

python FlattenFolder.py ~/media/music/DNB\ Hard                      # dry run
python FlattenFolder.py ~/media/music/DNB\ Hard --apply              # actually move
python FlattenFolder.py ~/media/music/DNB\ Hard --apply --all        # also move .nfo, art, etc.
python FlattenFolder.py ~/media/music/DNB\ Hard --apply --keep-dirs  # leave empty dirs behind
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from util.spotify import get_cache_path, get_new_token

CachePath = Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--force-delete-cache",
        action="store_true",
        help="Delete the cache file without prompting.",
    )
    group.add_argument(
        "--keep-cache",
        action="store_true",
        help="Skip deleting the cache file (useful if you only want to re-auth).",
    )
    parser.add_argument(
        "--clean-only",
        action="store_true",
        help="Only run the cache-clean step, then exit without launching the auth flow.",
    )
    return parser.parse_args(argv)


def delete_cache_interactively(cache_path: CachePath, *, force: bool) -> bool:
    """Delete the cache file, optionally asking the user first.

    Returns True if the file was deleted.
    """

    if not cache_path.exists():
        print(f"No cache file found at {cache_path}.")
        return False

    if force:
        cache_path.unlink()
        print(f"Deleted existing cache at {cache_path} (forced).")
        return True

    prompt = input(
        f"Existing cache detected at {cache_path}. Delete it now? [y/N]: "
    ).strip().lower()
    if prompt in {"y", "yes"}:
        cache_path.unlink()
        print(f"Deleted existing cache at {cache_path}.")
        return True

    print("Keeping current cache file.")
    return False


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    cache_path = Path(get_cache_path())

    if args.keep_cache:
        print("Skipping cache deletion per --keep-cache.")
    else:
        delete_cache_interactively(cache_path, force=args.force_delete_cache)

    if args.clean_only:
        print("Clean-only run complete. Cache file state updated; skipping auth flow.")
        return 0

    try:
        print("Starting Spotify re-auth flow...")
        get_new_token()
        print("Re-auth flow finished. Check './util/spotify.cache' for a new token.")
        return 0
    except Exception as e:  # pragma: no cover - interactive helper
        print("Error during re-auth:", e)
        print(
            "If no browser opened, check the printed URL (Spotipy may have provided one)\n"
            "and verify the Redirect URI in your Spotify app settings matches `config.py`."
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
