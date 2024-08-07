# Source : https://github.com/vitto4/yt-playlist-diff
"""
This file contains most of the text to be printed by the script.
"""

# ---------------------------------------------------------------------------- #
#                                 IMPORT LOGIC                                 #
# ---------------------------------------------------------------------------- #

import sys

try:
    from colorama import init, Fore, Style

    init()
except ModuleNotFoundError:
    print(
        "[Err] Could not import module `colorama`. You can install the necessary dependencies by running the following command :"
        + "\n\n"
        + "  $ pip install -r requirements.txt"
        + "\n\n"
        + "If you don't have a copy of this file, you can find it over at https://github.com/vitto4/yt-playlist-diff/blob/main/src/requirements.txt"
    )
    sys.exit(1)

try:
    from enum import Enum
except ModuleNotFoundError:
    print(
        (
            Fore.RED
            + Style.BRIGHT
            + "[Err]"
            + Style.NORMAL
            + " Could not import module `enum`. Please check that your python version is >= 3.4."
            + Style.RESET_ALL
        )
    )
    sys.exit(1)


# ------------------------------------- . ------------------------------------ #


def error_handler():
    sys.exit(1)


# ---------------------------------------------------------------------------- #
#                                     MISC                                     #
# ---------------------------------------------------------------------------- #


# Stands for « reset »
RS = Style.RESET_ALL
SCRIPT_NAME = "script.pyz"

# ---------------------------------------------------------------------------- #
#                                   ARGPARSE                                   #
# ---------------------------------------------------------------------------- #


class Operation(Enum):
    """Simple enum to abstract on the three operations that this script supports.

    Attributes:
        _: Each operation (enum variant) has a value equal to its user-facing text representation.
    """

    DUMP = "dump"
    UPSTREAM = "up-diff"
    LOCAL = "local-diff"


class SubArgs(Enum):
    """Simple enum to abstract on the six arguments accepted by the three subparsers.

    Attributes:
        _: Each argument (enum variant) has a value equal to its user-facing text representation.
    """

    ID = "--id"
    BROWSER = "--browser"
    OUTPUT = "--output"
    DIFF_BASE = "--diff-base"
    DIFF_WITH = "--diff-with"
    ID_OVERRIDE = "--id-override"


arg_desc = (
    "| Fetch a YouTube playlist using its ID.\n"
    + "| Dump it into a CSV archive.\n"
    + "| Diff two archives of the same playlist to (hopefully) recover lost videos.\n"
)


arg_epilog = (
    "| Examples :\n"
    + "|\n"
    + "|  * Dump a playlist\n"
    + f"|    > {SCRIPT_NAME} {Operation.DUMP.value} {SubArgs.ID.value} LOremipSUmdolOrsiTamEtConseCtETuRA {SubArgs.BROWSER.value} chrome {SubArgs.OUTPUT.value} ./cool_playlist.csv\n"
    + "|\n"
    + "|  * Diff an archive with upstream\n"
    + f"|    > {SCRIPT_NAME} {Operation.UPSTREAM.value} {SubArgs.DIFF_BASE.value} ./trendy_memes.csv {SubArgs.BROWSER.value} firefox\n"
    + "|\n"
    + "|  * Diff two local archives\n"
    + f"|    > {SCRIPT_NAME} {Operation.LOCAL.value} {SubArgs.DIFF_BASE.value} ./dusty_old_archive.csv {SubArgs.DIFF_WITH.value} ./shiny_new_archive.csv \n"
    + "|\n"
)


arg_operation_dump = "Dump the playlist into a CSV archive."
arg_operation_upstream = "Fetch upstream and perform a diff with your local archive."
arg_operation_local = "Perform a local diff between two archives."

arg_id = "YouTube ID of the playlist to dump\nE.g. : `LOremipSUmdolOrsiTamEtConseCtETuRA`."
arg_id_override = f"YouTube ID of the playlist to fetch. This should be detected automatically using the archive provided in `{SubArgs.DIFF_BASE.value}`."
arg_browser = "Browser to use for session cookies (required to access private playlists when fetching)\nE.g. : `chrome`, `firefox`."
arg_diff_base = "Path to your existing archive in CSV format\nE.g. : `./dusty_old_archive.csv`."
arg_path = "Customize the path (and name) of the output archive\nE.g. : `./folder/my_shiny_new_archive.csv`."
arg_diff_with = "Path to the most recent of the two archives you want to diff."

# ---------------------------------------------------------------------------- #
#                                    FORMAT                                    #
# ---------------------------------------------------------------------------- #

indent_simple = "   "
indent_line = "|  "
indent_arrow = ">  "  # "\u21aa  "
indent_bullet = "• "
yes_no_prompt = Style.BRIGHT + Fore.GREEN + "[Y" + Fore.RESET + "/" + Fore.RED + "N]" + Fore.RESET + RS
separator_line = "\n" + Style.BRIGHT + "--------------------------------------------------" + "\n" + RS

# ---------------------------------------------------------------------------- #
#                                ERRORS/WARNINGS                               #
# ---------------------------------------------------------------------------- #

err_generic_module_import = (
    Fore.RED
    + Style.BRIGHT
    + "[Err]"
    + Style.NORMAL
    + " Could not import module {module}. You can install the necessary dependencies by running the following command :"
    + "\n\n"
    + Style.BRIGHT
    + Fore.YELLOW
    + "$"
    + RS
    + " pip install -r requirements.txt"
    + "\n\n"
    + "If you don't have a copy of this file, you can find it over at "
    + Style.BRIGHT
    + Fore.BLUE
    + "https://github.com/vitto4/yt-playlist-diff/blob/main/src/requirements.txt"
    + RS
)

warn_playlists_ids_do_not_match = (
    Fore.YELLOW
    + Style.NORMAL
    + "\n[Warn]"
    + " Playlist IDs do not match.\n"
    + RS
    + Fore.YELLOW
    + indent_line
    + Fore.RESET
    + "The two files do not appear to be from the same playlist. (IDs do not match)\n"
    + Fore.YELLOW
    + indent_line
    + Fore.RESET
    + "Do you wish to continue anyway ? "
    + yes_no_prompt
    + RS
)

err_file_read = (
    Fore.RED
    + Style.BRIGHT
    + "[Err]"
    + Style.NORMAL
    + " Could not open "
    + Fore.WHITE
    + Style.BRIGHT
    + "{file_path}"
    + Style.NORMAL
    + Fore.RED
    + ". Please double check for any typo."
    + RS
)

err_file_write = (
    Fore.RED
    + Style.BRIGHT
    + "[Err]"
    + Style.NORMAL
    + " Could not write to "
    + Fore.WHITE
    + Style.BRIGHT
    + "{file_path}"
    + Style.NORMAL
    + Fore.RED
    + "."
    + RS
)

warn_archive_dates_wrong_order = (
    Fore.YELLOW
    + Style.NORMAL
    + "\n[Warn]"
    + " Archive dates reversed.\n"
    + RS
    + Fore.YELLOW
    + indent_line
    + Fore.RESET
    + f"Archive provided with `{SubArgs.DIFF_BASE.value}` seems to be more recent than your target (`{SubArgs.DIFF_WITH.value}` or `{SubArgs.ID.value}`).\n"
    + Fore.YELLOW
    + indent_line
    + Fore.RESET
    + "This is not fatal.\n"
    + RS
)

message_script_terminated = (
    Style.BRIGHT + "\nScript was terminated because of error : " + Fore.RED + "{result}\n" + RS
)

# ---------------------------------------------------------------------------- #
#                                     INFO                                     #
# ---------------------------------------------------------------------------- #


# ---------------------------------- CHECKUP --------------------------------- #

checkup_section = "\n" + Fore.GREEN + indent_arrow + Style.BRIGHT + "Checkup" + RS

message_checkup = (
    Fore.GREEN
    + indent_line
    + Fore.RESET
    + "Checking playlist "
    + Style.BRIGHT
    + "{new_id}"
    + RS
    + " archived on "
    + Fore.CYAN
    + Style.BRIGHT
    + "{new_date}"
    + RS
    + ",\n"
    + Fore.GREEN
    + indent_line
    + Fore.RESET
    + "Against playlist "
    + Style.BRIGHT
    + "{old_id}"
    + RS
    + " archived on "
    + Fore.CYAN
    + Style.BRIGHT
    + "{old_date}"
    + RS
    + "."
)

result_allgood = (
    Fore.GREEN
    + Style.BRIGHT
    + "Good news !"
    + RS
    + " Your playlist is healthy and every video is available for you to enjoy :)\n"
)

# ----------------------------------- FETCH ---------------------------------- #

upstream_fetch_section = "\n" + Fore.BLUE + indent_arrow + Style.BRIGHT + "Fetch" + RS

message_upstream_read_archive_base = (
    Fore.BLUE
    + indent_line
    + Style.NORMAL
    + Fore.WHITE
    + "Reading archive"
    + Fore.BLUE
    + Style.BRIGHT
    + " {path}"
    + Fore.WHITE
    + Style.NORMAL
    + "."
    + RS
)

message_upstream_fetching_playlist = (
    Fore.BLUE
    + indent_line
    + Style.NORMAL
    + Fore.WHITE
    + "Fetching playlist"
    + Fore.BLUE
    + Style.BRIGHT
    + " {id}"
    + Fore.WHITE
    + Style.NORMAL
    + "."
    + RS
)

message_upstream_fetched_playlist = Fore.BLUE + indent_line + Fore.WHITE + "Done." + RS


# ----------------------------------- DUMP ----------------------------------- #

dump_section = "\n" + Fore.BLUE + indent_arrow + Style.BRIGHT + "Dump" + RS


message_dump_fetching_playlist = (
    Fore.BLUE
    + indent_line
    + Style.NORMAL
    + Fore.WHITE
    + "Fetching playlist"
    + Fore.BLUE
    + Style.BRIGHT
    + " {id}"
    + Fore.WHITE
    + Style.NORMAL
    + "."
    + RS
)

message_dump_id_override = (
    Fore.BLUE
    + indent_line
    + Style.NORMAL
    + Fore.WHITE
    + "Overriding playlist ID with "
    + Fore.BLUE
    + Style.BRIGHT
    + "{id}"
    + Fore.WHITE
    + Style.NORMAL
    + "."
    + RS
)

message_dump_found_id_in_archive = (
    Fore.BLUE
    + indent_line
    + Style.NORMAL
    + Fore.WHITE
    + "Found playlist ID `"
    + Fore.BLUE
    + Style.BRIGHT
    + "{id}"
    + Fore.WHITE
    + Style.NORMAL
    + "`."
    + RS
)

message_dump_playlist_dumped = (
    Fore.BLUE
    + indent_line
    + Style.NORMAL
    + Fore.WHITE
    + "Playlist dumped to "
    + Fore.BLUE
    + Style.BRIGHT
    + "{path}"
    + Fore.WHITE
    + Style.NORMAL
    + ".\n"
    + RS
)


# ---------------------------------------------------------------------------- #
#                                   ANALYSIS                                   #
# ---------------------------------------------------------------------------- #

message_lost_count = (
    "\n"
    + Fore.RED
    + Style.BRIGHT
    + indent_arrow
    + "{lost_total} video(s)"
    + RS
    + " were found to be lost in the newest archive provided... =(\n"
    + indent_simple
    + "But don't worry, this script has got you covered "
    + Style.BRIGHT
    + "|•'-'•)و✧ "
    + RS
)

message_couldnt_recover = (
    Fore.RED + Style.BRIGHT + indent_arrow + "[{lost}/{total}]" + RS + " could unfortunately not be recovered"
)

message_recovered = (
    Fore.GREEN + Style.BRIGHT + indent_arrow + "[{recovered}/{total}]" + RS + " were successfully recovered"
)

prompt_user_instructions = (
    separator_line
    + "\nDo you wish to be presented with the instructions on what to do with these results ? "
    + yes_no_prompt
)

# ---------------------------------------------------------------------------- #
#                                    TABLES                                    #
# ---------------------------------------------------------------------------- #

header_yt_id_lost = Fore.RED + Style.BRIGHT + "YouTube ID" + RS
header_yt_id_recovered = Fore.GREEN + Style.BRIGHT + "YouTube ID" + RS
header_index = Fore.BLUE + Style.BRIGHT + "Index" + RS
header_category = Fore.WHITE + Style.BRIGHT + "Category" + RS
header_title = Fore.WHITE + Style.BRIGHT + "Title" + RS
header_channel = Fore.WHITE + Style.BRIGHT + "Channel" + RS
header_url = Fore.WHITE + Style.BRIGHT + "Channel URL" + RS
category_al = "AL"
category_nl = Fore.YELLOW + "NL" + RS
legend_al = "This video is currently lost, and already was in the older archive provided."
legend_nl = (
    "This video wasn't found in the older archive provided. It was both added to the playlist, and lost "
    + Style.BRIGHT
    + "after"
    + RS
    + " the older archive was made."
)
legend_nl_tip = (
    Fore.BLUE
    + Style.BRIGHT
    + "[Tip]"
    + Style.NORMAL
    + Fore.RESET
    + " If you have many of these "
    + category_nl
    + " videos, consider archiving your playlist more frequently."
    + RS
)
legend_full = (
    Style.BRIGHT
    + "Legend :\n"
    + RS
    + indent_bullet
    + category_al
    + " : "
    + legend_al
    + "\n"
    + indent_bullet
    + category_nl
    + " : "
    + legend_nl
    + "\n\n"
    + legend_nl_tip
)

# ---------------------------------------------------------------------------- #
#                                 INSTRUCTIONS                                 #
# ---------------------------------------------------------------------------- #

instruction_indent = Fore.BLUE + indent_line + RS
instruction_heading = Fore.BLUE + Style.BRIGHT + indent_arrow + "Instructions\n" + RS
instruction_al = (
    instruction_indent
    + indent_bullet
    + Style.BRIGHT
    + "AL (Already Lost)\n"
    + RS
    + instruction_indent
    + indent_simple
    + "You can use tools such as Google cache, https://web.archive.org or https://archive.is to try and find what these videos were.\n"
    + instruction_indent
    + indent_simple
    + "Sometimes, googling the YouTube ID of the video wrapped with quotes also works, because of websites linking to said video and mentioning the title as well.\n"
)
instruction_nl = (
    instruction_indent
    + indent_bullet
    + Style.BRIGHT
    + "NL (Newly Lost)\n"
    + RS
    + instruction_indent
    + indent_simple
    + "You can use tools such as Google cache, https://web.archive.org or https://archive.is to try and find what these videos were.\n"
    + instruction_indent
    + indent_simple
    + "Sometimes, googling the YouTube ID of the video wrapped with quotes also works, because of websites linking to said video and mentioning the title as well.\n"
)
instruction_recovered = (
    instruction_indent
    + indent_bullet
    + Style.BRIGHT
    + "Recovered\n"
    + RS
    + instruction_indent
    + indent_simple
    + "Search up the videos' titles on YouTube (you'll most likely find reuploads) and add them back to your playlist !\n"
)
instruction_tip = (
    instruction_indent
    + "\n"
    + instruction_indent
    + "To keep things clean and tidy after you're done investigating, you can remove all videos found by the script from your playlist to not have too many redundant hits next time you run it.\n"
    + instruction_indent
    + "You'll find the videos in your playlist using the index provided in the tables.\n"
    + instruction_indent
    + "If and after you've done so, don't forget to make another « clean » archive of your updated/repaired playlist for future use with this script.\n"
    + instruction_indent
    + "See https://github.com/vitto4/yt-playlist-diff/tree/main?tab=readme-ov-file#-usage for additional information.\n"
)
