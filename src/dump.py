# Source : https://github.com/vitto4/yt-playlist-diff
"""
Dump service for the script. YouTube playlists --> CSV.
"""

# ---------------------------------------------------------------------------- #
#                                 IMPORT LOGIC                                 #
# ---------------------------------------------------------------------------- #

import io
import time
from datetime import datetime

# Should be safe as long as the script is distributed as a zipapp
import misc_text as txt

try:
    import yt_dlp
except ModuleNotFoundError:
    print(txt.err_generic_module_import.format(module="`yt-dlp`"))
    txt.error_handler()

# ------------------------------------- . ------------------------------------ #


def _get_playlist_from_yt(playlist_id: str, browser: str) -> dict:
    """Fetch the playlist using `yt_dlp`

    Args:
        playlist_id (str): YouTube ID of the playlist (e.g. PLhixgUqwRTjwvBI-hmbZ2rpkAl4lutnJG)
        browser (str): Browser to use as specified in https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py#L336C5-L336C23

    Returns:
        dict: The information dictionary of the playlist.
    """
    ydl_opts = {
        "skip_download": True,  # We don't want to download any video
        "quiet": True,  # No need to be verbose
        "extract_flat": True,  # I don't remember what that is, better leave it like that
        "playlist_items": "1-5000",  # A playlist can (as of yet) not contain more than 5000 videos, this is a YouTube limitation
    }

    if browser is not None:
        ydl_opts["cookiesfrombrowser"] = (browser,)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        playlist_dict = ydl.extract_info(
            f"https://www.youtube.com/playlist?list={playlist_id}", download=False
        )

    return playlist_dict


def _write_csv_header(playlist_dict: dict, strio: io.StringIO):
    """Write the header to `output_file`, containing metadata and the CSV header

    Args:
        playlist_dict (dict): The `yt_dlp` information dictionary of the playlist being processed.
        output_file (str): Path to the output (csv) file
    """
    strio.write(
        f"""Playlist ID : {playlist_dict["id"]}\n"""
        + f"""Archived on : {int(time.time() * 1000)}\n"""
        + """index, id, isUnavailable, channel, channelUrl, title\n"""
    )


def _write_csv_body(playlist_dict: dict, strio: io.StringIO):
    """Go through each video of `playlist_dict` and append it to the CSV output file

    Args:
        playlist_dict (dict): The `yt_dlp` information dictionary of the playlist being processed.
        output_file (str): Path to the output (csv) file
    """
    for i, entry in enumerate(playlist_dict["entries"], start=1):
        unavailable = (
            entry["thumbnails"][0]["url"] == "https://i.ytimg.com/img/no_thumbnail.jpg"
        )  # A video that is for some reason not available to play should have that thumbnail

        strio.write(
            f"""{i}, """
            + f"""{entry["id"]}, """
            + f"""{unavailable}, """
            + f"""\"{entry["channel"] if not unavailable else "Unknown channel"}\", """
            + f"""\"{entry["channel_url"] if not unavailable else "Unknown link"}\", """
            + f"""\"{entry["title"]}\"\n"""
        )


def dump(
    playlist_id: str,
    browser: str = None,
) -> tuple[io.StringIO, str]:
    """Fetch and dump the playlist into a CSV archive. Return the result.

    Args:
        playlist_id (str): YouTube ID of the playlist (e.g. PLhixgUqwRTjwvBI-hmbZ2rpkAl4lutnJG)
        browser (str, optional): Browser to use as specified in https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py#L336C5-L336C23. Defaults to None.

    Returns:
        tuple[io.StringIO, str]: A StringIO object (TL;DR, a file-like thingy) containing the freshly dumped CSV archive, and a filename suggestion (str) like <playlist-title>-<date>.csv.
    """
    playlist_dict = _get_playlist_from_yt(playlist_id, browser)

    strio = io.StringIO()

    _write_csv_header(playlist_dict, strio)
    _write_csv_body(playlist_dict, strio)

    return (strio, f"""{playlist_dict["title"]} - {datetime.now().strftime("%Y-%m-%d")}.csv""")
