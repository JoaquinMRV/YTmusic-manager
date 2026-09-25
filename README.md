# YTMusic Manager

A small Python script that cleans up your **YouTube Music "Liked Music"** list:

- 🔁 **Removes duplicate songs** (same title + same artists), keeping one copy
- 🎤 **Removes all songs by a given artist**
- 🎵 **Removes songs whose title contains some text**

"Removing" means the song is **unliked**. It is not deleted from YouTube Music, and you can like it again anytime.

By default the script runs as a **dry run**: it only lists what it *would* remove. Nothing changes until you add `--apply`.

---

## Requirements

- Python 3.8+
- A YouTube Music account
- A desktop browser (Chrome, Firefox, or Edge) to copy your login headers

## Installation

```bash
git clone https://github.com/JoaquinMRV/ytmusic-manager.git
cd ytmusic-manager
pip install -r requirements.txt
```

## Authentication (one-time setup)

The script uses [ytmusicapi](https://github.com/sigma67/ytmusicapi), which needs your browser's request headers to act as you.

1. Open [music.youtube.com](https://music.youtube.com) in your browser and make sure you're logged in.
2. Open DevTools (`F12`) → **Network** tab.
3. Click **Library** (or scroll) so requests appear, then filter for `browse`.
4. Click a `POST` request to `browse?...`, then copy its **request headers**:
   - **Chrome / Edge:** Headers → Request Headers → select everything from `accept: */*` to the end, and copy.
   - **Firefox:** right-click the request → Copy → Copy Request Headers.
5. In this folder, run:

   ```bash
   ytmusicapi browser
   ```

   Paste the headers, then press `Enter`, then `Ctrl+Z` + `Enter` on Windows or `Ctrl+D` on macOS/Linux.

This creates a `browser.json` file. See the [official ytmusicapi guide](https://ytmusicapi.readthedocs.io/en/stable/setup/browser.html) if you get stuck.

> ⚠️ **Keep `browser.json` private!** It contains your session cookies, so anyone who has it can access your YouTube/Google account. It's already in `.gitignore`. Never upload or share it. If it leaks, log out of all sessions in your Google account.
>
> The login usually stays valid for about 2 years, unless you log out of that browser session.

## Usage

**Always preview first (dry run, nothing changes):**

```bash
python ytmanager.py
```

That lists all duplicate liked songs. When the list looks right, add `--apply`:

```bash
python ytmanager.py --apply
```

The script asks you to type `yes` before it unlikes anything.

### Examples

| Goal | Command |
|---|---|
| Remove duplicates only | `python ytmanager.py --apply` |
| Remove duplicates **and** every song by an artist | `python ytmanager.py --artist "bad bunny" --apply` |
| Remove only songs by an artist (keep duplicates) | `python ytmanager.py --artist "bad bunny" --no-duplicates --apply` |
| Remove songs whose title contains text | `python ytmanager.py --title "remix" --no-duplicates --apply` |
| Several artists at once | `python ytmanager.py --artist "artist one" --artist "artist two" --apply` |
| Artist **and** title must both match | `python ytmanager.py --artist "queen" --title "live" --no-duplicates --apply` |

### Options

| Option | Description |
|---|---|
| `--artist TEXT` | Remove songs by an artist whose name contains `TEXT` (case-insensitive). Can be repeated. |
| `--title TEXT` | Remove songs whose title contains `TEXT` (case-insensitive). Can be repeated. |
| `--no-duplicates` | Don't remove duplicates, only apply `--artist` / `--title`. |
| `--apply` | Actually unlike the songs. Without it, the script only previews. |
| `--yes` | Skip the confirmation prompt (use with care). |
| `--auth FILE` | Use a different auth file (default: `browser.json`). |

## How duplicates are detected

Two songs count as duplicates when they have the **same title** and the **same set of artists** (ignoring upper/lower case and extra spaces). The first copy in your liked list is kept and the rest are unliked.

## Notes

- Matching is **partial**: `--artist "queen"` also matches "Queens of the Stone Age". Always check the dry run.
- Very large libraries can take a while to load. YouTube may also rate-limit you if you remove thousands of songs at once. If it fails, just run it again.
- This project is not affiliated with YouTube or Google.

## License

MIT — see [LICENSE](LICENSE).
