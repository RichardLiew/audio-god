#!/usr/bin/env zsh

##############################################################################

# Created Time: 2025-06-27T21:25:10Z

# Total Steps: 11

##############################################################################

set -e

##############################################################################

export AUDGOD_CACHE_PATH=~/.audgod-cache

##############################################################################

printf "%.0s@" {1..60}
echo "\n\n[***] Starting ...\n"

##############################################################################

# Step (1):
./audio-god convert qmc-to-audio \
    --source='~/Music/Source/Qmc' \
    --extensions=qmc,qmc0,qmc1,qmc2,qmc3,qmcogg,qmcflac \
    --output='~/Music/Output/Qmc-To-Audio' \
    --recursive \
    --ignored-file=./ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

# Step (2):
./audio-god redecorate-note \
    --document=./songs.note \
    --field-type=auto \
    --log-level=WARNING \
    --log-file=stderr

# Step (3):
./audio-god fill-properties \
    --source='~/Music/Source/Mp3' \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignores.txt \
    --document=./songs.note \
    --root='~/Music/Source/Mp3' \
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

# Step (4):
./audio-god format-properties \
    --source='~/Music/Source/Mp3' \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

# Step (5):
./audio-god rename-audios \
    --source='~/Music/Source/Mp3' \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignores.txt \
    --filename-pattern='@{artist} + @{title}' \
    --log-level=WARNING \
    --log-file=stderr

# Step (6):
./audio-god organize grouped \
    --source='~/Music/Source/Mp3' \
    --root='~/Music/Output/Grouped' \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

# Step (7):
./audio-god list-repeated \
    --source='~/Music/Output/Grouped' \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignores.txt \
    --output=./repeated.txt \
    --log-level=WARNING \
    --log-file=stderr

# Step (8):
./audio-god export note \
    --source='~/Music/Output/Grouped' \
    --fields=basic \
    --field-type=cn \
    --output=./songs.note \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

# Step (9):
./audio-god convert note-to-markdown \
    --document=./songs.note \
    --field-type=auto \
    --output=./songs.note.md \
    --log-level=WARNING \
    --log-file=stderr

# Step (10):
./audio-god organize ituned \
    --source='~/Music/Output/Grouped' \
    --root='~/Music/iTunes/iTunes Media/Music' \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

# Step (11):
./audio-god export plist \
    --source='~/Music/Source/Mp3' \
    --fields=ituned \
    --field-type=en \
    --output='~/Music/iTunes/Library.xml' \
    --itunes-version-plist=/System/Applications/Music.app/Contents/version.plist \
    --itunes-media-folder='~/Music/iTunes/iTunes Media/Music' \
    --track-initial-id=601 \
    --playlist-initial-id=3001 \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

##############################################################################

unset AUDGOD_CACHE_PATH

##############################################################################

printf "%.0s@" {1..60}
echo "\n\n[***] Finished!\n"
