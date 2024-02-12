"""
This file contains most of the text to be printed
by `list_parser.py`.
"""
import sys
try:
    from colorama import init, Fore, Back, Style
    init()
except ModuleNotFoundError:
    print("[Err] Could not import module `colorama`. You can install the necessary dependencies by running the following command :\n\n  $ pip install -r requirements.txt\n")
    sys.exit(1)

# ---------------------------------------------------------------------------- #
#                                     TEXT                                     #
# ---------------------------------------------------------------------------- #

# ----------------------------------- MISC ----------------------------------- #

RS = Style.RESET_ALL

# ---------------------------------- FORMAT ---------------------------------- #

indent_simple = "   "
indent_line = "|  "
indent_arrow = "\u21aa  "
indent_bullet = "• "
yes_no_prompt = Style.BRIGHT + Fore.GREEN + "[Y" + Fore.RESET + "/" + Fore.RED + "N]" + Fore.RESET + RS
separator_line = Style.BRIGHT + "--------------------------------------------------" + RS

# ---------------------------------- ERRORS ---------------------------------- #

enum_import_error = Fore.RED + Style.BRIGHT + "[Err]" + Style.NORMAL + " Could not import module `enum`. Please check that your python version is >= 3.4." + RS
prettytable_import_error = Fore.RED + Style.BRIGHT + "[Err]" + Style.NORMAL + " Could not import module `prettytable`. You can install the necessary dependencies by running the following command :\n\n  " + Style.BRIGHT + Fore.YELLOW +  "$" + RS + " pip install -r requirements.txt\n"
playlists_ids_do_not_match = Fore.RED + Style.BRIGHT + "\n[Err]" + Style.NORMAL + " Playlist IDs do not match.\n" + RS + Fore.RED + indent_line + Fore.RESET + "The two files do not appear to be from the same playlist. (IDs do not match)\n" + Fore.RED + indent_line + Fore.RESET + "Do you wish to continue anyway ? " + yes_no_prompt + RS
archive_dates_wrong_order = Fore.RED + Style.BRIGHT + "\n[Err]" + Style.NORMAL + " Archive dates reversed.\n" + RS + Fore.RED + indent_line + Fore.RESET + "The first playlist archive provided seems to be more recent than the second one.\n" + Fore.RED + indent_line + Fore.RESET + Style.BRIGHT + Fore.BLUE + "[Reminder]" + Style.NORMAL + " The oldest backup should be the first argument.\n" + RS + Fore.RED + indent_line + Fore.RESET + "Do you wish to continue anyway ? " + yes_no_prompt + RS

# ----------------------------------- INFO ----------------------------------- #

documentation = Style.BRIGHT + "\nParser for csv archives of youtube playlists in the yt-list-bookmarklet format.\n\n" + Fore.GREEN + "Usage :" + RS + " list_parser.py " + Fore.YELLOW +"[oldest archive csv relative path] " + Fore.BLUE + "[newest archive csv relative path]\n" + RS
result_allgood = Fore.GREEN + Style.BRIGHT + "Good news !" + RS + " Your playlist is healthy and every video is available for you to enjoy :)\n"


# ----------------------------------- TABLE ---------------------------------- #

header_yt_id_lost = Fore.RED + Style.BRIGHT + "Youtube ID" + RS
header_yt_id_recovered = Fore.GREEN + Style.BRIGHT + "Youtube ID" + RS
header_index = Fore.BLUE + Style.BRIGHT + "Index" + RS
header_category = Fore.WHITE + Style.BRIGHT + "Category" + RS
header_title = Fore.WHITE + Style.BRIGHT + "Title" + RS
header_channel = Fore.WHITE + Style.BRIGHT + "Channel" + RS
header_url = Fore.WHITE + Style.BRIGHT + "Channel URL" + RS
category_al = "AL"
category_nl = Fore.YELLOW + Style.BRIGHT + "NL" + RS
legend_al = "This video is currently lost, and already was in the older archive provided."
legend_nl = "This video wasn't found in the older archive provided. It was both added to the playlist, and lost " + Style.BRIGHT + "after" + RS + " the older archive was made."
legend_nl_tip = Fore.BLUE + Style.BRIGHT + "[Tip]" + Style.NORMAL + " If you have many of these " + category_nl + Fore.BLUE + " videos, consider archiving your playlist more frequently." + RS
legend_full = Style.BRIGHT + "Legend :\n" + RS + indent_bullet + category_al + " : " + legend_al + "\n" + indent_bullet + category_nl + " : " + legend_nl + "\n\n" + legend_nl_tip

# ------------------------------- INSTRUCTIONS ------------------------------- #

instruction_indent = Fore.BLUE + indent_line + RS
instruction_heading = Fore.BLUE + Style.BRIGHT + indent_arrow + "Instructions :\n" + RS
instruction_al = instruction_indent + indent_bullet + Style.BRIGHT + "AL (Already Lost) :\n" + RS + instruction_indent + indent_simple + "You can use tools such as Google cache, https://web.archive.org or https://archive.is to try and find what these videos were.\n" + instruction_indent + indent_simple + "Sometimes, googling the youtube ID of the video wrapped with quotes also works, because of websites linking to said video and mentioning the title as well.\n"
instruction_nl = instruction_indent + indent_bullet + Style.BRIGHT + "NL (Newly Lost) :\n" + RS + instruction_indent + indent_simple + "You can use tools such as Google cache, https://web.archive.org or https://archive.is to try and find what these videos were.\n" + instruction_indent + indent_simple + "Sometimes, googling the youtube ID of the video wrapped with quotes also works, because of websites linking to said video and mentioning the title as well.\n"
instruction_recovered = instruction_indent + indent_bullet + Style.BRIGHT + "Recovered :\n" + RS + instruction_indent + indent_simple + "Search up the videos' titles on youtube and add them back to your playlist !\n"
instruction_tip = instruction_indent + "\n" + instruction_indent + "To keep things clean and tidy, after you're done investigating, you can remove all videos found by the script from your playlist to not have too many redundant hits next time you run it.\n" + instruction_indent + "You'll find the videos in your playlist using the index provided in the tables.\n" + instruction_indent + "If and after you've done so, don't forget to make another « clean » archive of your updated/repaired playlist for future use with this script.\n"