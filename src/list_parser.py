"""
Parser for csv archives of youtube playlists
in the yt-playlist-bookmarklet format
"""

# ---------------------------------------------------------------------------- #
#                                 IMPORT LOGIC                                 #
# ---------------------------------------------------------------------------- #

import sys
import csv
import datetime
try:
    import misc_text as txt
except ModuleNotFoundError:
    print("[Err] Could not import module `misc_text`. Please make sure you placed the file named `misc_text.py` in the same directory as this script.")
    sys.exit(1)

# Safe operations, provided previous blocks ran.
from colorama import Fore, Back, Style
try:
    from enum import Enum
except ModuleNotFoundError:
    print(txt.enum_import_error)
    sys.exit(1)
try:
    import prettytable as pt
except ModuleNotFoundError:
    print(txt.prettytable_import_error)
    sys.exit(1)

# ---------------------------------------------------------------------------- #
#                                  DEFINITIONS                                 #
# ---------------------------------------------------------------------------- #

# --------------------------------- VARIABLES -------------------------------- #

cln_args = sys.argv[1:]   # `1:` Skip the name of the file (i.e. the python executable)


# ---------------------------------- CLASSES --------------------------------- #

class CheckupResult(Enum):
    """
    See function `checkup`.
    """
    PASS = 1
    DATE = 2
    ID = 3
    ERR = 4



# --------------------------------- FUNCTIONS -------------------------------- #


def poll() -> bool:
    """
    Polls the user, Y/N question.
    (case insensitive)

    Returns
    -------
    - bool = `True` if user answered "Y", `False` if user answered "N" or anything else.
    """
    user_input = input()

    return True if (str.lower(user_input) == "y") else False


def read(file_path: str) -> dict:
    """
    Reads csv archives in the yt-playlist-bookmarklet format.

    Args
    ----
    - `file_path`: str = String containing the relative path of the targeted csv file.

    Returns
    -------
    - `out`: dict = Dictionary representing the csv file in the following format :\n
                "playlist_id": str = Youtube ID of the playlist.\n
                "save_date": str = Unix timestamp at which the archive was made.\n
                "data": list(list) = List containing all videos and their metadata,
                                     each video is a list, check csv header for more
                                     information.
    """
    # Output
    out = {}

    # Reading the files
    try:
        with open(file_path, "r", encoding="utf-8") as playlist:

            # Reader object
            reader = csv.reader(playlist, delimiter=",", skipinitialspace=True)

            # Metadata
            out["playlist_id"] = next(playlist)[14:-1]
            out["save_date"] = next(playlist)[14:-1]

            # Data
            next(playlist)                                          # Do not include the header in the read csv
            out["data"] = list(reader)

    except FileNotFoundError:
        print(Fore.RED + Style.BRIGHT + "[Err]" + Style.NORMAL + " Could not open " + Fore.WHITE + Style.BRIGHT + file_path + Style.NORMAL + Fore.RED + ". Please double check for any typo." + txt.RS)
        sys.exit(1)

    return out


def checkup(old_playlist: dict, new_playlist: dict) -> CheckupResult:
    """
    Check whether the two provided archives are compatible,
    i.e. they are the same playlist (same ID) and the older
    one is actually the oldest archive of the two.

    Args
    ----
    - `old_playlist`: dict = Dictionary of the archive that is supposed to be the oldest.
    - `new_playlist`: dict = Dictionary of the archive that is supposed to be the newest.

    Returns
    -------
    - `out`: CheckupResult = Enum variant : PASS if everything is ok ; ERR, ID or DATE if not.

    """
    out = CheckupResult.ERR                                             # Fallback output

    # Variables
    new_pl_unix_time = int(new_playlist['save_date']) / 1000 if (len(str(int(new_playlist['save_date']))) >= 13) else int(new_playlist['save_date'])      # Accommodate for unix time in seconds or miliseconds.
    old_pl_unix_time = int(old_playlist['save_date']) / 1000 if (len(str(int(old_playlist['save_date']))) >= 13) else int(old_playlist['save_date'])

    print("\n" + Fore.GREEN + Style.BRIGHT + "Checkup :" + txt.RS)
    print(Fore.GREEN + txt.indent_line + Fore.RESET + "Checking playlist " + Style.BRIGHT + f"{new_playlist['playlist_id']}" + txt.RS +  " archived on " + Fore.BLUE + Style.BRIGHT + f"{datetime.datetime.fromtimestamp(new_pl_unix_time).strftime('%Y-%m-%d %H:%M:%S')}" + txt.RS + ",\n" + Fore.GREEN + txt.indent_line + Fore.RESET + "Against playlist " + Style.BRIGHT + f"{old_playlist['playlist_id']}" + txt.RS + " archived on " + Fore.YELLOW + Style.BRIGHT + f"{datetime.datetime.fromtimestamp(old_pl_unix_time).strftime('%Y-%m-%d %H:%M:%S')}" + txt.RS + ".\n")


    if old_playlist["playlist_id"] != new_playlist["playlist_id"]:      # The two files aren't from the same playlist
        print(txt.playlists_ids_do_not_match, end=" ")
        out = CheckupResult.PASS if poll() else CheckupResult.ID
    
    elif old_playlist["save_date"] >= new_playlist["save_date"]:        # The first file is newer than the second
        print(txt.archive_dates_wrong_order, end=" ")
        out = CheckupResult.PASS if poll() else CheckupResult.DATE

    else:                                                               # Else everything is fine
        out = CheckupResult.PASS

    return out


def collect(playlist: dict) -> dict:
    """
    Collects all unavailable videos from `playlist`.

    Args
    ----
    - `playlist`: dict = Dictionary of the targeted archive.

    Returns
    -------
    - `lost_ids`: dict = Dictionary representing the IDs of the lost videos for which we are trying to find metadata, and the corresponding youtube index of the videos in the newest version of the playlist as values.
    """
    # Local variables
    data = playlist["data"]                         # List of lists containing all videos and their metadata
    lost_ids = {}                                   # List of the youtube IDs of lost/removed videos

    for idx in range(len(data)):
        if data[idx][2] == "True":                  # If said video is unavailable
            lost_ids[data[idx][1]] = data[idx][0]   # collect its youtube ID

    return lost_ids


def compare(playlist: dict, lost_ids: dict) -> dict:
    """
    Checks the archive `playlist` for sought-after youtube video IDs,
    in hopes of finding the corresponding metadata in it.

    Args
    ----
    - `playlist`: dict = Dictionary of the archive to compare against.
    - `lost_ids`: dict = Dictionary generated by `collect`, effectively a list of all IDs for which we are trying to find the metadata.

    Returns
    -------
    - `out`: dict = Dictionary with lost IDs as keys and either `[yt_index, False]` (if no metadata was found), `[yt_index, True]` (if lost metadata was found) or [yt_index, metadata] as values ; where `yt_index` is the index of the video in the newest version of the playlist.
    """
    out = {}                                # Output
    data = playlist["data"]                 # List of lists containing all videos and their metadata
    ids = [row[1] for row in data]          # Column containing all the youtube IDs of the 

    for lost in lost_ids.keys():
        try:
            index = ids.index(lost)                                                                                 # Find the index of the current ID in the playlist
            out[lost] = [lost_ids[lost], data[index]] if (data[index][2] == "False") else [lost_ids[lost], True]    # Register found data only if `available`
        except:
            out[lost] = [lost_ids[lost], False]                                                                     # No corresponding video has been found in the playlist
    
    return out


def analyse(recovered: dict):
    """
    This function serves as the final output of the script.
    It will check for the metadata of lost videos from the
    new playlist in the old playlist.

    It will then output the results for the user.

    Args
    ----
    - `recovered`: dict = Dictionary generated by `compare`, containing all IDs of lost videos, and, if applicable, the recovered metadata.
    """
    # Variables
    user_instructions = txt.instruction_heading                                                             # String to display containing instructions, will be built using above parts
    lost_total = len(recovered)                                                                             # Number of videos marked as unavailable


    print(Fore.RED + Style.BRIGHT + txt.indent_arrow + f"{lost_total} video(s)" + txt.RS + " were found to be lost in the newest archive provided... =(\n" + txt.indent_simple + "But don't worry, this script has got you covered " +  Style.BRIGHT + "|•'-'•)و✧ " + txt.RS)


    # -------------------------------- LOST VIDEOS ------------------------------- #

    # Already lost videos
    already_lost_idx = [idx for (idx, element) in enumerate(recovered.values()) if (element[1] == True)]    # List of index of every element that has `True` as value, meaning a video that is lost in both the new and old archive
    already_lost = [list(recovered.keys())[idx] for idx in already_lost_idx]                                # Corresponding youtube video IDs

    # Newly lost videos
    newly_lost_idx = [idx for (idx, element) in enumerate(recovered.values()) if (element[1] == False)]     # List of index of every element that has `False` as value, meaning a video that is lost in the newest archive and not present in the older one
    newly_lost = [list(recovered.keys())[idx] for idx in newly_lost_idx]                                    # Corresponding youtube video IDs

    if len(already_lost) + len(newly_lost) > 0:                                                             # If any video is lost                   
        # Setting up the table for lost videos (output)
        lost_table = pt.PrettyTable(padding_width=3)
        lost_table.set_style(pt.SINGLE_BORDER)
        lost_table.field_names = [txt.header_yt_id_lost, txt.header_index, txt.header_category]

        if len(already_lost) > 0:                                                                           # If relevant to print
            user_instructions += txt.instruction_al                                                         # Add instructions
            for idx in range(len(already_lost)):
                lost_table.add_row([Fore.RED + already_lost[idx] + txt.RS, Fore.BLUE + recovered[already_lost[idx]][0] + txt.RS, txt.category_al])


        if len(newly_lost) > 0:                                                                             # If relevant to print
            user_instructions += txt.instruction_nl                                                         # Add instructions
            for idx in range(len(newly_lost)):
                lost_table.add_row([Fore.RED + newly_lost[idx] + txt.RS, Fore.BLUE + recovered[newly_lost[idx]][0] + txt.RS, txt.category_nl])

        print("\n" + txt.separator_line + "\n")
        print(Fore.RED + Style.BRIGHT + txt.indent_arrow + f"[{len(already_lost) + len(newly_lost)}/{lost_total}]" + txt.RS + " could unfortunately not be recovered :")
        print(lost_table)
        print(txt.legend_full)

    # ----------------------------- RECOVERED VIDEOS ----------------------------- #

    # Recovered videos
    recovered_idx = [idx for (idx, element) in enumerate(recovered.values()) if ((element[1] != True) and (element[1] != False))]   # List of index of every element that has a value that is not a boolean, meaning a video for which the metadata was successfully recovered (hooray !)
    recovered_data = [list(recovered.values())[idx] for idx in recovered_idx]                                                       # Corresponding metadata

    if len(recovered_data) > 0:                                                                                                     # If relevant to print
        # Setting up the table for lost videos (output)
        recovered_table = pt.PrettyTable(padding_width=3)
        recovered_table.set_style(pt.SINGLE_BORDER)
        recovered_table.field_names = [txt.header_yt_id_recovered, txt.header_index, txt.header_title, txt.header_channel, txt.header_url]
        
        user_instructions += txt.instruction_recovered                                                                              # Add instructions

        for idx in range(len(recovered_data)):
            recovered_table.add_row([Fore.GREEN + recovered_data[idx][1][1] + txt.RS, Fore.BLUE + recovered_data[idx][0] + txt.RS, recovered_data[idx][1][5], recovered_data[idx][1][3], recovered_data[idx][1][4]])                                                                                                                # Skip a line
        print("\n" + txt.separator_line + "\n")
        print(Fore.GREEN + Style.BRIGHT + txt.indent_arrow + f"[{len(recovered_data)}/{lost_total}]" + txt.RS + " were successfully recovered :")
        print(recovered_table)

    # ----------------------------- USER INSTRUCTIONS ---------------------------- #
    
    print("\n" + txt.separator_line + "\n\nDo you wish to be presented with the instructions on what to do with these results ? " + txt.yes_no_prompt, end=" ")
    if poll():
        print()                                                     # Skip a line
        user_instructions += txt.instruction_tip
        print(user_instructions)






# ---------------------------------------------------------------------------- #
#                             MAIN EXECUTION LOGIC                             #
# ---------------------------------------------------------------------------- #

def main():
    if len(cln_args) != 2:                          # If no/too many arguments were provided, print documentation
        print(txt.documentation)

    else:                                           # Else continue
        old_playlist = read(cln_args[0])                # Fetch data from older archive
        new_playlist = read(cln_args[1])                # Fetch data from newest archive
        result = checkup(old_playlist, new_playlist)    # Check files metadata for compatibility

        if result == CheckupResult.PASS:                # If everything is fine
            lost_ids = collect(new_playlist)                # Find all lost videos in the newest archive
            
            if len(lost_ids) > 0:                           # If videos were lost
                recovered = compare(old_playlist, lost_ids)     # Fetch the corresponding metadata from the older archive
                analyse(recovered)                              # Analyse, match and print out the results
            
            else:                                           # Else, nothing was lost
                print(txt.result_allgood)

        else:                                           # Else, a problem was found and user chose to abort.
            print(Style.BRIGHT + "\nScript was terminated because of error : " + Fore.YELLOW + f"{result}\n" + txt.RS)


if __name__ == "__main__":
    main()