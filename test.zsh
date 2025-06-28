#!/usr/bin/env zsh

##############################################################################

# Created Time: 2025-06-29T00:48:59Z

# Total Steps: 28

##############################################################################

set -e

##############################################################################

export AUDGOD_CACHE_PATH=./test/.audgod-cache

##############################################################################

echo "\n[***] Starting ...\n"

##############################################################################

printf "%.0s@" {1..60}; printf "\n"
echo "Step (1/28):\n\n"

./audio-god testing cleanup \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (2/28):\n\n"

./audio-god testing init \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (3/28):\n\n"

./audio-god convert kmx-to-mp4 \
    --source=./test/Source/Kmx \
    --extensions=kmx \
    --output=./test/Output/Kmx-To-Mp4 \
    --recursive \
    --ignored-file=./test/test.ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (4/28):\n\n"

./audio-god convert qmc-to-audio \
    --source=./test/Source/Qmc \
    --extensions=qmc,qmc0,qmc1,qmc2,qmc3,qmcogg,qmcflac \
    --output=./test/Output/Qmc-To-Audio \
    --recursive \
    --ignored-file=./test/test.ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (5/28):\n\n"

./audio-god convert media \
    --source=./test/Source/Media \
    --extensions=mp3,mp4,mov,flac,wav,ogg,ape,wma \
    --output=./test/Output/Media \
    --format=mp3 \
    --recursive \
    --ignored-file=./test/test.ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (6/28):\n\n"

./audio-god redecorate-note \
    --document=./test/test.songs.note.origin \
    --field-type=auto \
    --output=./test/test.songs.note \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (7/28):\n\n"

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
    --separators='-,#' \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (8/28):\n\n"

./audio-god format-properties \
    --source=./test/Source/Mp3 \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/test.ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (9/28):\n\n"

./audio-god rename-audios \
    --source=./test/Source/Mp3 \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/test.ignores.txt \
    --filename-pattern='@{artist} # @{title}' \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (10/28):\n\n"

./audio-god manage-artworks bind \
    --source=./test/Source/Mp3 \
    --artworks=./test/Source/Artwork \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/test.ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (11/28):\n\n"

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

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (12/28):\n\n"

./audio-god organize grouped \
    --source=./test/Source/Mp3 \
    --root=./test/Output/Grouped \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/test.ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (13/28):\n\n"

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

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (14/28):\n\n"

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

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (15/28):\n\n"

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

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (16/28):\n\n"

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

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (17/28):\n\n"

./audio-god list-repeated \
    --source=./test/Output/Grouped \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/test.ignores.txt \
    --output=./test/Output/test.repeated.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (18/28):\n\n"

./audio-god organize ituned \
    --source=./test/Output/Grouped \
    --root='./test/Output/iTunes/iTunes Media/Music' \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/test.ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (19/28):\n\n"

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

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (20/28):\n\n"

./audio-god manage-artworks derive \
    --source='./test/Output/iTunes/iTunes Media/Music' \
    --output=./test/Output/Artwork \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/test.ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (21/28):\n\n"

./audio-god convert note-to-markdown \
    --document=./test/Output/test.songs.note \
    --field-type=auto \
    --output=./test/Output/test.songs.note.md \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (22/28):\n\n"

./audio-god convert markdown-to-note \
    --document=./test/Output/test.songs.md \
    --output=./test/Output/test.songs.md.note \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (23/28):\n\n"

./audio-god extract-structure \
    --document=./test/test.songs.note \
    --field-type=auto \
    --output=./test/Output/songs.note.tree \
    --show-count \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (24/28):\n\n"

./audio-god operate backup \
    --source=./test/test.operate.backup.txt \
    --ignored-file=./test/test.ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (25/28):\n\n"

./audio-god operate remove \
    --source=./test/test.operate.remove.txt \
    --ignored-file=./test/test.ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (26/28):\n\n"

./audio-god operate tree \
    --source=./test/Output \
    --output=./test/Output/test.output.tree \
    --show-count \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (27/28):\n\n"

./audio-god generate-script start \
    --output=./test/Output/test.start.zsh \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (28/28):\n\n"

./audio-god testing generate-script \
    --output=./test/Output/test.test.zsh \
    --log-level=WARNING \
    --log-file=stderr

##############################################################################

unset AUDGOD_CACHE_PATH

##############################################################################

printf "%.0s@" {1..60}; printf "\n"
echo "\n[***] Finished!\n"
