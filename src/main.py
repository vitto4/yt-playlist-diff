# Source : https://github.com/vitto4/yt-playlist-diff
"""
# yt-playlist-diff

* Fetch a YouTube playlist using its ID.
* Dump it into a CSV archive.
* Diff two archives of the same playlist to (hopefully) recover lost videos.
"""

# ---------------------------------------------------------------------------- #
#                                 IMPORT LOGIC                                 #
# ---------------------------------------------------------------------------- #

import argparse

# Should be safe as long as the script is distributed as a zipapp
import misc_text as txt
from misc_text import Operation, SubArgs
import dump
import diff

try:
    from rich_argparse import RawTextRichHelpFormatter
except ModuleNotFoundError:
    print(txt.err_generic_module_import.format(module="`rich_argparse`"))
    txt.error_handler()

# ------------------------------------- . ------------------------------------ #


def parser_setup():
    """Sets up everything `argparse`-related."""

    # We want to be able to retrieve args from anywhere
    global args

    parser = argparse.ArgumentParser(
        description=txt.arg_desc,
        formatter_class=RawTextRichHelpFormatter,
        epilog=txt.arg_epilog,
    )

    # Main argument, the operation to perform
    subparsers = parser.add_subparsers(
        dest="operation",
        metavar="OPERATION",
        required=True,
    )

    # fmt: off

    # Arguments related to Operation.DUMP
    dump_parser = subparsers.add_parser(Operation.DUMP.value, help=txt.arg_operation_dump, formatter_class=parser.formatter_class)
    dump_parser.add_argument(SubArgs.ID.value, required=True, metavar="PLAYLIST_ID", help=txt.arg_id)
    dump_parser.add_argument(SubArgs.BROWSER.value, metavar="BROWSER", help=txt.arg_browser)
    dump_parser.add_argument(SubArgs.OUTPUT.value, metavar="PATH", help=txt.arg_path)

    # Arguments related to Operation.UPSTREAM
    upstream_diff_parser = subparsers.add_parser(Operation.UPSTREAM.value, help=txt.arg_operation_upstream, formatter_class=parser.formatter_class)
    upstream_diff_parser.add_argument(SubArgs.DIFF_BASE.value, required=True, metavar="PATH", help=txt.arg_diff_base)
    upstream_diff_parser.add_argument(SubArgs.ID_OVERRIDE.value, metavar="PLAYLIST_ID", help=txt.arg_id_override)
    upstream_diff_parser.add_argument(SubArgs.BROWSER.value, metavar="BROWSER", help=txt.arg_browser)

    # Arguments related to Operation.LOCAL
    local_diff_parser = subparsers.add_parser(Operation.LOCAL.value, help=txt.arg_operation_local, formatter_class=parser.formatter_class)
    local_diff_parser.add_argument(SubArgs.DIFF_BASE.value, required=True, metavar="PATH", help=txt.arg_diff_base)
    local_diff_parser.add_argument(SubArgs.DIFF_WITH.value, required=True, metavar="PATH", help=txt.arg_diff_with)

    # fmt: on

    args = parser.parse_args()


def main():
    parser_setup()

    # ---------------------------------- ROUTING --------------------------------- #

    # Match all three possible operations
    match args.operation:
        case Operation.DUMP.value:
            print(txt.dump_section)
            print(txt.message_dump_fetching_playlist.format(id=args.id))

            # The playlist isn't immediately dumped into a file, but kept in ram in a `StringIO`
            # This is useful when we only want to diff without dumping (so in the next `case`).
            strio, default_file_path = dump.dump(
                args.id,
                browser=args.browser,
            )

            # If a path was provided by the user, override the default one
            file_path = args.output if args.output is not None else default_file_path

            # Attempt to write the dump to the disk
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(strio.getvalue())
                    print(txt.message_dump_playlist_dumped.format(path=file_path))
            except IOError:
                print(txt.err_file_write.format(file_path=file_path))

        case Operation.UPSTREAM.value:
            print(txt.upstream_fetch_section)

            # Try reading the archive
            try:
                with open(args.diff_base, "r", encoding="utf-8") as f:
                    base = diff.read(f)
                    print(txt.message_upstream_read_archive_base.format(path=args.diff_base))
            except FileNotFoundError:
                print(txt.err_file_read.format(file_path=args.diff_base))
                txt.error_handler()

            playlist_id = args.id_override if (args.id_override is not None) else base["playlist_id"]
            print(
                txt.message_dump_id_override.format(id=playlist_id)
                if (args.id_override is not None)
                else txt.message_dump_found_id_in_archive.format(id=playlist_id)
            )

            print(txt.message_upstream_fetching_playlist.format(id=playlist_id))
            upstream_dump, _ = dump.dump(
                playlist_id,
                browser=args.browser,
            )
            print(txt.message_upstream_fetched_playlist)

            upstream_dump.seek(0)  # Reset the cursor to read from the beginning
            against = diff.read(upstream_dump)

            diff.diff(base, against)

        case Operation.LOCAL.value:
            try:
                with open(args.diff_base, "r", encoding="utf-8") as f:
                    base = diff.read(f)
            except FileNotFoundError:
                print(txt.err_file_read.format(file_path=args.diff_base))
                txt.error_handler()

            try:
                with open(args.diff_with, "r", encoding="utf-8") as f:
                    against = diff.read(f)
            except FileNotFoundError:
                print(txt.err_file_read.format(file_path=args.diff_with))
                txt.error_handler()

            diff.diff(base, against)


if __name__ == "__main__":
    main()
