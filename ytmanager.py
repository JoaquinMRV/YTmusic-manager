
from ytmusicapi import YTMusic, OAuthCredentials

def should_remove(song, artists_filter=None, titles_filter=None):
    """
    Check if song matches filters.
    :param song: A dict for the song.
    :param artists_filter: List of artist names (lowercased), or None for no filter.
    :param titles_filter: List of song titles (lowercased), or None for no filter.
    :return: True if matches any filter, False otherwise.
    """
    # Always check with lowercased values for robustness.
    match_artist = False
    match_title = False
    if artists_filter:
        song_artists = [a["name"].lower() for a in song.get("artists", [])]
        match_artist = any(f in artist for artist in song_artists for f in artists_filter)
    else:
        match_artist = True  # No filter = always match

    if titles_filter:
        title = song.get("title", "").lower()
        match_title = any(f in title for f in titles_filter)
    else:
        match_title = True  # No filter = always match

    return match_artist and match_title

def main():
    # MODIFY THESE FILTERS AS NEEDED:
    artists_filter = []  # Lowercase, partial match OK, empty list or None for no filter
    titles_filter = ["the peeper"]  # Lowercase, partial match OK, empty list or None for no filter
    remove_duplicates = True  # Set to True to remove duplicates (all but one copy)

    print("Initializing YTMusic...")
    ytmusic = YTMusic("browser.json")

    # Fetch all liked songs
    # Fetch all liked songs
    print("Fetching liked songs... (this might take a few seconds)")
    # A high limit tells the library to handle all the scrolling automatically
    results = ytmusic.get_liked_songs(limit=9999) 
    liked_songs = results['tracks']

    print(f"Total liked songs found: {len(liked_songs)}")

    # Identify duplicates (by title + artist)
    duplicates = []
    if remove_duplicates:
        seen = {}
        for song in liked_songs:
            key = (
                song.get("title", "").strip().lower(),
                tuple(sorted(a["name"].strip().lower() for a in song.get("artists", [])))
            )
            if key in seen:
                duplicates.append(song)
            else:
                seen[key] = song
        print(f"Duplicate songs found: {len(duplicates)}")

    # Prepare removal list
    filtered_songs = []
    for song in liked_songs:
        remove_for_filter = should_remove(
            song,
            artists_filter=[a.lower() for a in artists_filter] if artists_filter else None,
            titles_filter=[t.lower() for t in titles_filter] if titles_filter else None,
        )
        remove_for_duplicate = song in duplicates
        if remove_for_filter or remove_for_duplicate:
            filtered_songs.append((song, remove_for_filter, remove_for_duplicate))

    print(f"Songs to remove based on filters or duplication: {len(filtered_songs)}")
    # Proceed with removal
    for idx, (song, filt, dupe) in enumerate(filtered_songs, 1):
        videoId = song.get("videoId")
        title = song.get("title")
        artists = ", ".join(a["name"] for a in song.get("artists", []))
        reasons = []
        if filt:
            reasons.append("matches filter")
        if dupe:
            reasons.append("duplicate")
        reason_str = " & ".join(reasons)
        print(f"Removing [{idx}/{len(filtered_songs)}]: {title} by {artists} ({reason_str})...")
        try:
            ytmusic.rate_song(videoId, 'INDIFFERENT')
        except Exception as e:
            print(f"  Failed to unlike {title}: {e}")

    print(f"Done! Removed {len(filtered_songs)} songs (filtered and/or duplicates).")

if __name__ == "__main__":
    main()


  #Instructions:
  #  - To remove by specific artist or song name: edit artists_filter and titles_filter.
   # - Set remove_duplicates = True to also remove repeated (duplicate) liked songs.
  #  - Duplicates are compared based on title + all artist names.
  #  - This script is destructive! Test first on a smaller sample if concerned.
