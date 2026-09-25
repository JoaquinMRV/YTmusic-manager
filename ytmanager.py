"""
YouTube Music liked-songs cleaner.

Removes (unlikes) songs from your "Liked Music" that are duplicates and/or
match an artist / title filter. Runs as a dry run unless --apply is given.
"""

import argparse
import os
import sys

from ytmusicapi import YTMusic


def should_remove(song, artists_filter=None, titles_filter=None):
    """
    Check if song matches filters.
    :param song: A dict for the song.
    :param artists_filter: List of artist names (lowercased), or None for no filter.
    :param titles_filter: List of song titles (lowercased), or None for no filter.
    :return: True if matches the filters, False otherwise (or if no filter is set).
    """
    # With no filters at all, nothing matches (otherwise every song would be removed).
    if not artists_filter and not titles_filter:
        return False

    if artists_filter:
        song_artists = [a["name"].lower() for a in song.get("artists") or []]
        match_artist = any(f in artist for artist in song_artists for f in artists_filter)
    else:
        match_artist = True  # No artist filter = only the title filter counts

    if titles_filter:
        title = (song.get("title") or "").lower()
        match_title = any(f in title for f in titles_filter)
    else:
        match_title = True  # No title filter = only the artist filter counts

    return match_artist and match_title


def parse_args():
    parser = argparse.ArgumentParser(
        description="Remove duplicate and/or filtered songs from your YouTube Music liked songs."
    )
    parser.add_argument("--auth", default="browser.json",
                        help="Path to the ytmusicapi auth file (default: browser.json)")
    parser.add_argument("--artist", action="append", default=[],
                        help="Remove songs by this artist (partial, case-insensitive). Can be repeated.")
    parser.add_argument("--title", action="append", default=[],
                        help="Remove songs whose title contains this text (case-insensitive). Can be repeated.")
    parser.add_argument("--no-duplicates", action="store_true",
                        help="Do not remove duplicates, only apply the artist/title filters.")
    parser.add_argument("--apply", action="store_true",
                        help="Actually unlike the songs. Without this flag the script only shows what it would do.")
    parser.add_argument("--yes", action="store_true",
                        help="Skip the confirmation prompt when using --apply.")
    return parser.parse_args()


def main():
    args = parse_args()
    artists_filter = [a.lower() for a in args.artist] or None
    titles_filter = [t.lower() for t in args.title] or None
    remove_duplicates = not args.no_duplicates

    if not remove_duplicates and not artists_filter and not titles_filter:
        print("Nothing to do: duplicates are disabled and no --artist/--title filter was given.")
        return

    if not os.path.exists(args.auth):
        print(f"Auth file '{args.auth}' not found. Run `ytmusicapi browser` first (see README).")
        sys.exit(1)

    print("Initializing YTMusic...")
    ytmusic = YTMusic(args.auth)

    print("Fetching liked songs... (this might take a few seconds)")
    # A high limit tells the library to handle all the scrolling automatically
    results = ytmusic.get_liked_songs(limit=9999)
    liked_songs = results["tracks"]
    print(f"Total liked songs found: {len(liked_songs)}")

    # Identify duplicates (by title + artist); the first copy is kept
    duplicate_ids = set()
    if remove_duplicates:
        seen = set()
        for song in liked_songs:
            key = (
                (song.get("title") or "").strip().lower(),
                tuple(sorted(a["name"].strip().lower() for a in song.get("artists") or [])),
            )
            if key in seen:
                duplicate_ids.add(id(song))
            else:
                seen.add(key)
        print(f"Duplicate songs found: {len(duplicate_ids)}")

    # Prepare removal list
    to_remove = []
    for song in liked_songs:
        filt = should_remove(song, artists_filter, titles_filter)
        dupe = id(song) in duplicate_ids
        if filt or dupe:
            to_remove.append((song, filt, dupe))

    print(f"Songs to remove: {len(to_remove)}\n")
    if not to_remove:
        return

    for idx, (song, filt, dupe) in enumerate(to_remove, 1):
        artists = ", ".join(a["name"] for a in song.get("artists") or [])
        reasons = " & ".join(r for r, on in (("matches filter", filt), ("duplicate", dupe)) if on)
        print(f"  [{idx}/{len(to_remove)}] {song.get('title')} by {artists} ({reasons})")

    if not args.apply:
        print("\nDry run: nothing was changed. Re-run with --apply to unlike these songs.")
        return

    if not args.yes:
        answer = input(f"\nUnlike these {len(to_remove)} songs? Type 'yes' to continue: ")
        if answer.strip().lower() != "yes":
            print("Cancelled.")
            return

    removed = 0
    for idx, (song, _, _) in enumerate(to_remove, 1):
        title = song.get("title")
        print(f"Removing [{idx}/{len(to_remove)}]: {title}...")
        try:
            ytmusic.rate_song(song.get("videoId"), "INDIFFERENT")
            removed += 1
        except Exception as e:
            print(f"  Failed to unlike {title}: {e}")

    print(f"Done! Removed {removed} of {len(to_remove)} songs.")


if __name__ == "__main__":
    main()
