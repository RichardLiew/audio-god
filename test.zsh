#!/usr/bin/env zsh

##############################################################################

# Created Time: 2025-06-26T13:42:21Z

# Total Steps: 25

##############################################################################

set -e

##############################################################################

export AUDGOD_CACHE_PATH=./test/.audgod-cache

##############################################################################

# Step (1):
./audio-god testing cleanup \
    --log-level=WARNING \
    --log-file=stderr

# Step (2):
./audio-god testing init \
    --log-level=WARNING \
    --log-file=stderr

# Step (3):
./audio-god convert kmx-to-mp4 \
    --source=./test/Source/Kmx \
    --extensions=kmx \
    --output=./test/Output/Kmx-To-Mp4 \
    --recursive \
    --ignored-file=./test/test.ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

# Step (4):
./audio-god convert mp4-to-mp3 \
    --source=./test/Source/Mp4 \
    --extensions=mp4 \
    --output=./test/Output/Mp4-To-Mp3 \
    --recursive \
    --ignored-file=./test/test.ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

# Step (5):
./audio-god convert qmc-to-mp3 \
    --source=./test/Source/Qmc \
    --extensions=qmc,qmc0,qmc3,qmcflac \
    --output=./test/Output/Qmc-To-Mp3 \
    --executer=./executers/qmc-to-mp3/decoder \
    --recursive \
    --ignored-file=./test/test.ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

# Step (6):
./audio-god redecorate-note \
    --document=./test/test.songs.note \
    --field-type=auto \
    --log-level=WARNING \
    --log-file=stderr

# Step (7):
./audio-god fill-properties \
    --source=./test/Source/Mp3 \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/test.ignores.txt \
    --document=./test/test.songs.note \
    --root=./test/Source/Mp3 \
    --properties='{
        "_comment": "sources choose from command/file/directory/filename",
        "default": {
            "sources": ["command", "file"],
            "value": null
        },
        "genre": {
            "sources": ["command", "file"],
            "value": null
        }
    }' \
    --log-level=WARNING \
    --log-file=stderr

# Step (8):
./audio-god format-properties \
    --source=./test/Source/Mp3 \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/test.ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

# Step (9):
./audio-god rename-audios \
    --source=./test/Source/Mp3 \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/test.ignores.txt \
    --filename-pattern='@{artist} + @{title}' \
    --log-level=WARNING \
    --log-file=stderr

# Step (10):
./audio-god manage-artworks bind \
    --source=./test/Source/Mp3 \
    --artworks=./test/Source/Png \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/test.ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

# Step (11):
./audio-god display \
    --source=./test/Source/Mp3 \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/test.ignores.txt \
    --fields=core \
    --field-type=cn \
    --output=./test/Output/test.display.table \
    --data-format=outputted \
    --page-number=1 \
    --page-size=0 \
    --sort='[
        {"_comment": ""},
        ["title,artist", true],
        ["genre", false]
    ]' \
    --filter='{
        "_options": {
            "_comment": "relation choose from and/or",
            "relation": "or"
        },
        "title,core": {
            "_comment": "function choose from equal/search/empty",
            "function": "search",
            "parameters": ["", true, false]
        }
    }' \
    --align='{
        "_comment": "align=l/c/r, valign=t/m/b",
        "title,artist": "l:m"
    }' \
    --style=tabled \
    --numbered \
    --log-level=WARNING \
    --log-file=stderr

# Step (12):
./audio-god organize grouped \
    --source=./test/Source/Mp3 \
    --root=./test/Output/Grouped \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/test.ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

# Step (13):
./audio-god export note \
    --source=./test/Output/Grouped \
    --fields=basic \
    --field-type=cn \
    --output=./test/Output/test.songs.note \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/test.ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

# Step (14):
./audio-god export markdown \
    --source=./test/Output/Grouped \
    --fields=basic \
    --field-type=cn \
    --output=./test/Output/test.songs.md \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/test.ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

# Step (15):
./audio-god export xml \
    --source=./test/Output/Grouped \
    --fields=ituned \
    --field-type=cn \
    --output=./test/Output/test.songs.xml \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/test.ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

# Step (16):
./audio-god export json \
    --source=./test/Output/Grouped \
    --fields=basic \
    --field-type=cn \
    --output=./test/Output/test.songs.json \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/test.ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

# Step (17):
./audio-god list-repeated \
    --source=./test/Output/Grouped \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/test.ignores.txt \
    --output=./test/Output/test.repeated.txt \
    --log-level=WARNING \
    --log-file=stderr

# Step (18):
./audio-god organize ituned \
    --source=./test/Output/Grouped \
    --root='./test/Output/iTunes/iTunes Media/Music' \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/test.ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

# Step (19):
./audio-god export plist \
    --source=./test/Source/Mp3 \
    --fields=ituned \
    --field-type=en \
    --output=./test/Output/iTunes/Library.xml \
    --itunes-version-plist=/System/Applications/Music.app/Contents/version.plist \
    --itunes-media-folder='./test/Output/iTunes/iTunes Media/Music' \
    --track-initial-id=601 \
    --playlist-initial-id=3001 \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/test.ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

# Step (20):
./audio-god manage-artworks derive \
    --source='./test/Output/iTunes/iTunes Media/Music' \
    --output=./test/Output/Artworks \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/test.ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

# Step (21):
./audio-god convert note-to-markdown \
    --document=./test/Output/test.songs.note \
    --field-type=auto \
    --output=./test/Output/test.songs.note.md \
    --log-level=WARNING \
    --log-file=stderr

# Step (22):
./audio-god convert markdown-to-note \
    --document=./test/Output/test.songs.md \
    --output=./test/Output/test.songs.md.note \
    --log-level=WARNING \
    --log-file=stderr

# Step (23):
./audio-god operate backup \
    --source=./test/test.operate.backup.txt \
    --ignored-file=./test/test.ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

# Step (24):
./audio-god operate remove \
    --source=./test/test.operate.remove.txt \
    --ignored-file=./test/test.ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

# Step (25):
./audio-god operate tree \
    --source=./test/Output \
    --output=./test/Output/test.output.tree \
    --log-level=WARNING \
    --log-file=stderr

##############################################################################

unset AUDGOD_CACHE_PATH
