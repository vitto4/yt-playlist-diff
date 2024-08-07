# yt-playlist-diff
<p align="center">
  <a href="https://youtube.com">
    <img alt="YouTube" src="https://img.shields.io/badge/YouTube-%23FF0000.svg?&logo=YouTube&logoColor=white"
  /></a>
  <a href="https://python.org/downloads">
    <img alt="Python" src="https://img.shields.io/badge/python-3.4+-blue.svg"
  /></a>
  <a href="https://github.com/vitto4/yt-playlist-diff/releases">
    <img alt="GitHub Release" src="https://img.shields.io/github/v/release/vitto4/yt-playlist-diff"
  /></a>
  

</p>

<p align="center"><i>A python script to dump and diff YouTube playlists as csv archives.</i></p>

![screenshot.png](misc/example.png)

## 🏮 Index
1. [Overview](#-overview)
2. [Installation](#-installation)
3. [Usage](#-usage)
4. [Additional notes](#-additional-notes)
5. [Contributing](#-contributing)


## ☁ Overview

When a video goes private or is deleted, it will appear as such in YouTube playlists, making it difficult for the user to figure out what the original video was.

This project is my attempt at solving the problem. It consists of a script that can both :
- Dump for you the contents of any YouTube playlist you can view through your browser. Outputs a `csv` archive.
- Perform a `diff` on two archives of the same playlist to compile a list of all videos that went missing, along with their original title and channel if available in the older archive.

<details>
  <summary>Usage</summary>

```
Usage: main.py [-h] OPERATION ...

| Fetch a YouTube playlist using its ID.
| Dump it into a CSV archive.
| Diff two archives of the same playlist to (hopefully) recover lost videos.

Positional Arguments:
  OPERATION
    dump      Dump the playlist into a CSV archive.
    up-diff   Fetch upstream and perform a diff with your local archive.
    local-diff
              Perform a local diff between two archives.

Options:
  -h, --help  show this help message and exit

| Examples :
|
|  * Dump a playlist
|    > script.pyz dump --id LOremipSUmdolOrsiTamEtConseCtETuRA --browser chrome --output ./cool_playlist.csv
|
|  * Diff an archive with upstream
|    > script.pyz up-diff --diff-base ./trendy_memes.csv --browser firefox
|
|  * Diff two local archives
|    > script.pyz local-diff --diff-base ./dusty_old_archive.csv --diff-with ./shiny_new_archive.csv
|
```

</details>


All in all, it should enable you to keep track of which video vanishes over the course of time.

The major advantage of this approach is that it'll work regardless of whether the playlist is set to public or private, as long as you tell the script in which browser you're logged into YouTube.

Here's an example of the structure of an archive :

```csv
Playlist ID : LOremipSUmdolOrsiTamEtConseCtETuRA
Archived on : 1704067200000
index, id, isUnavailable, channel, channelUrl, title
1, GGrFShhGRWc, True, "Unknown artist", "Unknown link", "[Deleted video]"
2, dQw4w9WgXcQ, False, "Rick Astley", "https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw", "Rick Astley - Never Gonna Give You Up (Official Music Video)"
3, ...
```


## 💾 Installation

1. Make sure you have [Python](https://www.python.org/downloads/) installed.
2. Grab both `requirements.txt` and `script.pyz` from the latest [release](https://github.com/vitto4/yt-playlist-diff/releases).
3. Install the required dependencies. I recommend using a [venv](https://docs.python.org/3/tutorial/venv.html).

If you're on linux :

```sh
$ python3 -m venv env
$ source env/bin/activate
(env) $ pip install -r requirements.txt
```
Or for windows :
```bat
> py -m venv env
> env\Scripts\activate.bat
(env) > pip install -r requirements.txt
```

4. You're all set. The script is distributed as a python [zipapp](https://docs.python.org/3/library/zipapp.html) (`.pyz` file), but fear not, you can run it like any other python script.

## 📚 Usage

### General workflow

![](misc/diagram.drawio.svg)


#### 1 : Dump your playlist

The first step is to make a clean archive of your playlist. We'll call it *BASE*.

<details>
  <summary>Usage</summary>

```
Usage: script.pyz dump [-h] --id PLAYLIST_ID [--browser BROWSER] [--output PATH]

Options:
  -h, --help         show this help message and exit
  --id PLAYLIST_ID   YouTube ID of the playlist to dump
                     E.g. : `LOremipSUmdolOrsiTamEtConseCtETuRA`.
  --browser BROWSER  Browser to use for session cookies (required to access private playlists when fetching)
                     E.g. : `chrome`, `firefox`.
  --output PATH      Customize the path (and name) of the output archive
                     E.g. : `./folder/my_shiny_new_archive.csv`.
```

</details>

So you can do something like :

```sh
script.pyz dump --id <PlaylistID>
```

#### 2 : Diff two archives

You have a clean archive from some time ago, and now your playlist's missing a few videos.
To find out what these are, perform an **upstream diff**.

<details>
  <summary>Usage</summary>

```
Usage: script.pyz up-diff [-h] --diff-base PATH [--id-override PLAYLIST_ID] [--browser BROWSER]

Options:
  -h, --help            show this help message and exit
  --diff-base PATH      Path to your existing archive in CSV format
                        E.g. : `./dusty_old_archive.csv`.
  --id-override PLAYLIST_ID
                        YouTube ID of the playlist to fetch. This should be detected automatically using the archive provided in `--diff-base`.
  --browser BROWSER     Browser to use for session cookies (required to access private playlists when fetching)
                        E.g. : `chrome`, `firefox`.
```

</details>

Hence you can run the script like :

```sh
script.pyz up-diff --diff-base ./old_archive.csv
```

This will produce a detailed report of what videos are gone, with metadata if possible (title, channel, URL, ...).

Internally, the *UPSTREAM* version of the playlist is fetched directly from YouTube ; i.e. your `old_archive.csv` will be diffed against the latest version of the playlist available online.

Note that this step can also be performed locally, with a **local diff**.

<details>
  <summary>Usage</summary>

```
Usage: script.pyz local-diff [-h] --diff-base PATH --diff-with PATH

Options:
  -h, --help        show this help message and exit
  --diff-base PATH  Path to your existing archive in CSV format
                    E.g. : `./dusty_old_archive.csv`.
  --diff-with PATH  Path to the most recent of the two archives you want to diff.
```

</details>

This enables you to provide a second archive to diff against, in place of *UPSTREAM* :

```sh
script.pyz local-diff --diff-base ./old_archive.csv --diff-with ./new_archive.csv
```

#### 3 : Dump it again

When you're done recovering videos, don't forget to make a new **clean** archive of your updated/repaired playlist for future use with this script.

This will prevent redundant hits next time you perform a **diff**. (i.e. a video would be flagged as lost when you have, in fact, already replaced it with a reuploaded version)

## 🔖 Additional notes

This repo [used to host](https://github.com/vitto4/yt-playlist-diff/tree/yt-playlist-bookmarklet) a JS bookmarklet to perform the dump, but it was a bit too tedious to maintain, hence the switch to [`yt-dlp`](https://github.com/yt-dlp/yt-dlp).

The zipapp is created using the following command :

```sh
python3 -m zipapp src --main=main:main --output=script.pyz
```

I had a surprisingly hard time to try and explain how to actually use my code, this is when I decided to make the [workflow diagram](#general-workflow), hopefully it clears things up a bit !

I initially made this for my own use, but I hope it can be useful to others as well :)


## 🧩 Contributing

Contributions are (of course) welcome.

As long as `yt-dlp` keeps working, I believe the script should not break ; hence the project probably doesn't need much updating.
Feel free to open an issue if I've missed anything or if you need some help !