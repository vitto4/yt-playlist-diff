# Source : https://github.com/vitto4/yt-playlist-diff
"""
Parser and diff service for CSV archives of YouTube playlists in the `yt-playlist-diff` format.
"""


# ---------------------------------------------------------------------------- #
#                                 IMPORT LOGIC                                 #
# ---------------------------------------------------------------------------- #

# Safe
import io
import csv
import datetime

# Should be safe as long as the script is distributed as a zipapp
import misc_text as txt

# Safe, provided previous blocks ran.
from colorama import Fore

try:
    from enum import Enum
except ModuleNotFoundError:
    print(txt.enum_import_error)
    txt.error_handler()

try:
    import prettytable as pt
except ModuleNotFoundError:
    print(txt.err_generic_module_import.format(module="`prettytable`"))
    txt.error_handler()


# ------------------------------------- . ------------------------------------ #


class CheckupResult(Enum):
    """See function `checkup`."""

    PASS = 1
    ID = 2


def _poll() -> bool:
    """Polls the user, Y/N question. (case insensitive)

    Returns:
        bool: `True` if user answered "Y", `False` otherwise.
    """
    user_input = input()

    return True if (str.lower(user_input) == "y") else False


def read(file: io.StringIO | io.TextIOWrapper) -> dict:
    """Reads CSV archives in the `yt-playlist-diff` format

    Args:
        file (io.StringIO | io.TextIOWrapper): The archive as a text file/object.

    Returns:
        dict: Dictionary representing the archive in the following format :
                * "playlist_id" (str): YouTube ID of the playlist.
                * "save_date" (str): Unix timestamp at which the archive was made.
                * "data" (list[list]): List containing all videos and their metadata,
                                     each video is a list, check csv header for more
                                     information.
    """

    # Output
    out = {}

    reader = csv.reader(file, delimiter=",", skipinitialspace=True)

    # Metadata
    out["playlist_id"] = next(file)[14:-1]
    out["save_date"] = next(file)[14:-1]

    # Data
    next(file)  # Do not include the header in the csv being read
    out["data"] = list(reader)

    return out


def _checkup(old_archive: dict, new_archive: dict) -> CheckupResult:
    """Check whether the archives provided are compatible, i.e. they are of the same playlist (same ID), and they are provided in the right chronological order.

    Args:
        old_archive (dict): Dictionary of the archive that is supposed to be the oldest.
        new_archive (dict): Dictionary of the archive that is supposed to be the newest.

    Returns:
        CheckupResult: Enum variant, PASS if everything is ok ; ID if IDs do not match.
    """
    # Fallback output
    out = CheckupResult.PASS

    # Accommodate for unix time in seconds or milliseconds.
    new_pl_unix_time = (
        int(new_archive["save_date"]) / 1000
        if (len(str(int(new_archive["save_date"]))) >= 13)
        else int(new_archive["save_date"])
    )
    old_pl_unix_time = (
        int(old_archive["save_date"]) / 1000
        if (len(str(int(old_archive["save_date"]))) >= 13)
        else int(old_archive["save_date"])
    )

    print(txt.checkup_section)
    print(
        txt.message_checkup.format(
            old_id=old_archive["playlist_id"],
            new_id=new_archive["playlist_id"],
            old_date=datetime.datetime.fromtimestamp(old_pl_unix_time).strftime("%Y-%m-%d %H:%M:%S"),
            new_date=datetime.datetime.fromtimestamp(new_pl_unix_time).strftime("%Y-%m-%d %H:%M:%S"),
        )
    )

    # The two files aren't from the same playlist
    if old_archive["playlist_id"] != new_archive["playlist_id"]:
        print(txt.warn_playlists_ids_do_not_match, end=" ")
        out = CheckupResult.PASS if _poll() else CheckupResult.ID
    # The first file is newer than the second
    if old_archive["save_date"] >= new_archive["save_date"]:
        print(txt.warn_archive_dates_wrong_order, end=" ")
        # We can handle this, no need to prompt for termination
        # out = CheckupResult.PASS if poll() else CheckupResult.DATE

    return out


def _collect(playlist: dict) -> dict:
    """Collects all unavailable videos from `playlist`.

    Args:
        playlist (dict): Dictionary of the targeted archive.

    Returns:
        dict: Dictionary representing the IDs of the lost videos for which we are trying to recover metadata, and the corresponding YouTube index of the videos in the newest version of the playlist as values.
    """
    # List of lists containing all videos and their metadata
    data = playlist["data"]
    # List of the YouTube IDs of lost/removed videos
    lost_ids = {}

    for idx in range(len(data)):
        # If said video is unavailable
        if data[idx][2] == "True":
            # Collect its YouTube ID
            lost_ids[data[idx][1]] = data[idx][0]

    return lost_ids


def _compare(playlist: dict, lost_ids: dict) -> dict:
    """Checks the archive for sought-after YouTube video IDs, in the hope of finding the corresponding metadata.

    Args:
        playlist (dict): Dictionary of the archive to compare against.
        lost_ids (dict): Dictionary generated by `collect`, effectively a list of all IDs for which we are trying to find the metadata.

    Returns:
        dict: Dictionary with lost IDs as keys, and either `[yt_index, False]` (if no metadata was found), `[yt_index, True]` (if lost metadata was found) or [yt_index, metadata] as values ; where `yt_index` is the index of the video in the newest version of the playlist.
    """
    # Output
    out = {}
    # List of lists containing all videos and their metadata
    data = playlist["data"]
    # Column containing all the YouTube IDs of the videos in the archive
    ids = [row[1] for row in data]

    for lost in lost_ids.keys():
        try:
            # Find the index of the current ID in the playlist
            index = ids.index(lost)
            # Register found data only if `available`
            out[lost] = (
                [lost_ids[lost], data[index]] if (data[index][2] == "False") else [lost_ids[lost], True]
            )
        # No corresponding video has been found in the playlist
        except:
            out[lost] = [lost_ids[lost], False]

    return out


def _analyse(recovered: dict):
    """This function serves as the final output of the script.

    It will check for the metadata of lost videos from the new archive in the old archive.
    It will then print out the results for the user.

    Args:
        recovered (dict): Dictionary generated by `compare`, containing all IDs of lost videos, and, if applicable, the recovered metadata.
    """
    # String to display containing instructions, will be built from relevant parts
    user_instructions = txt.instruction_heading
    # Number of videos marked as unavailable
    lost_total = len(recovered)

    print(txt.message_lost_count.format(lost_total=lost_total))

    # -------------------------------- LOST VIDEOS ------------------------------- #

    ### Already lost videos ###
    # List of index of every element that has `True` as value, meaning a video that is lost in both the new and old archive
    already_lost_idx = [idx for (idx, element) in enumerate(recovered.values()) if (element[1] is True)]
    # Corresponding YouTube video IDs
    already_lost = [list(recovered.keys())[idx] for idx in already_lost_idx]

    ### Newly lost videos ###

    # List of index of every element that has `False` as value, meaning a video that is lost in the newest archive and not present in the older one
    newly_lost_idx = [idx for (idx, element) in enumerate(recovered.values()) if (element[1] is False)]
    # Corresponding YouTube video IDs
    newly_lost = [list(recovered.keys())[idx] for idx in newly_lost_idx]

    # If any video is lost
    if len(already_lost) + len(newly_lost) > 0:
        # Setting up the table for lost videos (output)
        lost_table = pt.PrettyTable(padding_width=3)
        lost_table.set_style(pt.SINGLE_BORDER)
        lost_table.field_names = [txt.header_yt_id_lost, txt.header_index, txt.header_category]

        # If relevant to print
        if len(already_lost) > 0:
            # Add instructions
            user_instructions += txt.instruction_al
            for idx in range(len(already_lost)):
                # Add row with corresponding category to the table
                lost_table.add_row(
                    [
                        Fore.RED + already_lost[idx] + txt.RS,
                        Fore.BLUE + recovered[already_lost[idx]][0] + txt.RS,
                        txt.category_al,
                    ]
                )

        # If relevant to print
        if len(newly_lost) > 0:
            # Add instructions
            user_instructions += txt.instruction_nl
            for idx in range(len(newly_lost)):
                # Add row with corresponding category to the table
                lost_table.add_row(
                    [
                        Fore.RED + newly_lost[idx] + txt.RS,
                        Fore.BLUE + recovered[newly_lost[idx]][0] + txt.RS,
                        txt.category_nl,
                    ]
                )

        print(txt.separator_line)
        print(
            txt.message_couldnt_recover.format(lost=(len(already_lost) + len(newly_lost)), total=lost_total)
        )
        print(lost_table)
        print(txt.legend_full)

    # ----------------------------- RECOVERED VIDEOS ----------------------------- #

    ### Recovered videos ###
    # List of index of every element that has a value that is not a boolean, meaning a video for which the metadata was successfully recovered (hooray !)
    recovered_idx = [
        idx for (idx, element) in enumerate(recovered.values()) if (type(element[1]) is not bool)
    ]
    # Corresponding metadata
    recovered_data = [list(recovered.values())[idx] for idx in recovered_idx]

    # If relevant to print
    if len(recovered_data) > 0:
        # Setting up the table for lost videos (output)
        recovered_table = pt.PrettyTable(padding_width=3)
        recovered_table.set_style(pt.SINGLE_BORDER)
        recovered_table.field_names = [
            txt.header_yt_id_recovered,
            txt.header_index,
            txt.header_title,
            txt.header_channel,
            txt.header_url,
        ]

        user_instructions += txt.instruction_recovered  # Add instructions

        for idx in range(len(recovered_data)):
            recovered_table.add_row(
                [
                    Fore.GREEN + recovered_data[idx][1][1] + txt.RS,
                    Fore.BLUE + recovered_data[idx][0] + txt.RS,
                    recovered_data[idx][1][5],
                    recovered_data[idx][1][3],
                    recovered_data[idx][1][4],
                ]
            )  # Skip a line
        print(txt.separator_line)
        print(txt.message_recovered.format(recovered=len(recovered_data), total=lost_total))
        print(recovered_table)

    # ----------------------------- USER INSTRUCTIONS ---------------------------- #

    print(txt.prompt_user_instructions, end=" ")
    if _poll():
        # Skip a line
        print()
        user_instructions += txt.instruction_tip
        print(user_instructions)


# ---------------------------------------------------------------------------- #
#                                  MAIN LOGIC                                  #
# ---------------------------------------------------------------------------- #


def diff(diff_base: dict, diff_with: dict):
    # Check files metadata for compatibility
    result = _checkup(diff_base, diff_with)

    # If everything is fine
    if result == CheckupResult.PASS:
        # Find all lost videos in the newest archive
        lost_ids = _collect(diff_with)

        # If videos were lost
        if len(lost_ids) > 0:
            # Fetch the corresponding metadata from the older archive
            recovered = _compare(diff_base, lost_ids)
            # Analyse, match and print out the results
            _analyse(recovered)
        # Else, nothing was lost
        else:
            print("\n" + txt.result_allgood)
    # Else, a problem was found and user chose to abort.
    else:
        print(txt.message_script_terminated.format(result=result))


# ------------------------------------- . ------------------------------------ #
